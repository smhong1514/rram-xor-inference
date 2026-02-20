#!/usr/bin/env python3
"""
char_bl_write_driver.py - BL Write Driver Liberty Characterization

Runs ngspice sweeps to extract timing arcs and generates a proper .lib file.
Arcs characterized:
  1. DATA → BL (combinational, negative_unate, EN=1 held)
  2. EN → BL (three_state_enable)

Sweep: 7 input_slew × 7 output_load = 49 points per direction
Total: ~200 ngspice simulations

Usage: cd ~/rram_openlane/analog/layout/bl_write_driver && python3 char_bl_write_driver.py
"""

import os
import sys
import subprocess
import re
import time
from multiprocessing import Pool, cpu_count

# ─── Configuration ───────────────────────────────────────────────────────────

NGSPICE = "/usr/local/bin/ngspice"
PDK_LIB = os.path.expandvars("$PDK_ROOT/sky130B/libs.tech/ngspice/sky130.lib.spice")

VDD = 1.8
THRESH_50 = VDD * 0.5   # 0.9V
THRESH_20 = VDD * 0.2   # 0.36V
THRESH_80 = VDD * 0.8   # 1.44V

SETTLE_NS = 5.0    # settling time before input transition
SIM_END_NS = 50.0  # total simulation time
TSTEP_NS = 0.005   # transient step size

# Sky130 standard sweep parameters
# input_net_transition: 20%-80% slew time in ns
INPUT_SLEWS_NS = [0.0100, 0.0230, 0.0540, 0.1280, 0.3000, 0.7000, 1.6500]
# total_output_net_capacitance in pF
OUTPUT_LOADS_PF = [0.0005, 0.00146, 0.00429, 0.01257, 0.03681, 0.10783, 0.31587]

WORK_DIR = "char_work"

# ─── DUT Subcircuit ──────────────────────────────────────────────────────────

DUT_SUBCKT = """\
.subckt bl_write_driver EN DATA BL VDD VSS
* EN inverter
XMP0 EN_B EN VDD VDD sky130_fd_pr__pfet_01v8 L=0.15 W=0.5 nf=1 mult=1
XMN0 EN_B EN VSS VSS sky130_fd_pr__nfet_01v8 L=0.15 W=0.5 nf=1 mult=1
* DATA inverter
XMP3 DATA_B DATA VDD VDD sky130_fd_pr__pfet_01v8 L=0.15 W=0.5 nf=1 mult=1
XMN3 DATA_B DATA VSS VSS sky130_fd_pr__nfet_01v8 L=0.15 W=0.5 nf=1 mult=1
* Output: series PMOS (VDD -> NET_P -> BL)
XMP1 NET_P EN_B VDD VDD sky130_fd_pr__pfet_01v8 L=0.15 W=4 nf=1 mult=1
XMP2 BL DATA_B NET_P VDD sky130_fd_pr__pfet_01v8 L=0.15 W=4 nf=1 mult=1
* Output: series NMOS (BL -> NET_N -> VSS)
XMN2 BL DATA_B NET_N VSS sky130_fd_pr__nfet_01v8 L=0.15 W=4 nf=1 mult=1
XMN1 NET_N EN VSS VSS sky130_fd_pr__nfet_01v8 L=0.15 W=4 nf=1 mult=1
.ends bl_write_driver
"""


# ─── SPICE Deck Generators ──────────────────────────────────────────────────

def slew_20_80_to_pwl(slew_ns):
    """Convert 20%-80% slew to 0%-100% PWL transition time.
    For a linear ramp, 20%-80% = 60% of total → total = slew / 0.6"""
    return slew_ns / 0.6


def gen_data_rise(slew_ns, load_pf):
    """DATA→BL cell_rise: DATA rises (0→1.8), BL rises (0→1.8). positive_unate buffer."""
    pwl = slew_20_80_to_pwl(slew_ns)
    t_start = SETTLE_NS
    t_end = t_start + pwl
    return f"""\
* BL Write Driver char: DATA->BL cell_rise (slew={slew_ns}ns, load={load_pf}pF)
.lib "{PDK_LIB}" tt
{DUT_SUBCKT}
VDD vdd 0 {VDD}
VSS vss 0 0
VEN en 0 {VDD}
VDATA data 0 PWL(0 0 {t_start}n 0 {t_end}n {VDD})
X1 en data bl vdd vss bl_write_driver
CL bl 0 {load_pf}p
R_init bl 0 1G

.tran {TSTEP_NS}n {SIM_END_NS}n

.control
run
meas tran cell_rise TRIG v(data) VAL={THRESH_50} RISE=1 TARG v(bl) VAL={THRESH_50} RISE=1
meas tran rise_tran TRIG v(bl) VAL={THRESH_20} RISE=1 TARG v(bl) VAL={THRESH_80} RISE=1
quit
.endc
.end
"""


def gen_data_fall(slew_ns, load_pf):
    """DATA→BL cell_fall: DATA falls (1.8→0), BL falls (1.8→0). positive_unate buffer."""
    pwl = slew_20_80_to_pwl(slew_ns)
    t_start = SETTLE_NS
    t_end = t_start + pwl
    return f"""\
* BL Write Driver char: DATA->BL cell_fall (slew={slew_ns}ns, load={load_pf}pF)
.lib "{PDK_LIB}" tt
{DUT_SUBCKT}
VDD vdd 0 {VDD}
VSS vss 0 0
VEN en 0 {VDD}
VDATA data 0 PWL(0 {VDD} {t_start}n {VDD} {t_end}n 0)
X1 en data bl vdd vss bl_write_driver
CL bl 0 {load_pf}p
R_init bl vdd 1G

.tran {TSTEP_NS}n {SIM_END_NS}n

.control
run
meas tran cell_fall TRIG v(data) VAL={THRESH_50} FALL=1 TARG v(bl) VAL={THRESH_50} FALL=1
meas tran fall_tran TRIG v(bl) VAL={THRESH_80} FALL=1 TARG v(bl) VAL={THRESH_20} FALL=1
quit
.endc
.end
"""


def gen_en_rise(slew_ns, load_pf):
    """EN→BL cell_rise: EN rises (0→1.8), DATA=1 held, BL rises (0→1.8)."""
    pwl = slew_20_80_to_pwl(slew_ns)
    t_start = SETTLE_NS
    t_end = t_start + pwl
    return f"""\
* BL Write Driver char: EN->BL cell_rise (slew={slew_ns}ns, load={load_pf}pF)
.lib "{PDK_LIB}" tt
{DUT_SUBCKT}
VDD vdd 0 {VDD}
VSS vss 0 0
VDATA data 0 {VDD}
VEN en 0 PWL(0 0 {t_start}n 0 {t_end}n {VDD})
X1 en data bl vdd vss bl_write_driver
CL bl 0 {load_pf}p
R_init bl 0 1G

.tran {TSTEP_NS}n {SIM_END_NS}n

.control
run
meas tran cell_rise TRIG v(en) VAL={THRESH_50} RISE=1 TARG v(bl) VAL={THRESH_50} RISE=1
meas tran rise_tran TRIG v(bl) VAL={THRESH_20} RISE=1 TARG v(bl) VAL={THRESH_80} RISE=1
quit
.endc
.end
"""


def gen_en_fall(slew_ns, load_pf):
    """EN→BL cell_fall: EN rises (0→1.8), DATA=0 held, BL falls (1.8→0)."""
    pwl = slew_20_80_to_pwl(slew_ns)
    t_start = SETTLE_NS
    t_end = t_start + pwl
    return f"""\
* BL Write Driver char: EN->BL cell_fall (slew={slew_ns}ns, load={load_pf}pF)
.lib "{PDK_LIB}" tt
{DUT_SUBCKT}
VDD vdd 0 {VDD}
VSS vss 0 0
VDATA data 0 0
VEN en 0 PWL(0 0 {t_start}n 0 {t_end}n {VDD})
X1 en data bl vdd vss bl_write_driver
CL bl 0 {load_pf}p
R_init bl vdd 1G

.tran {TSTEP_NS}n {SIM_END_NS}n

.control
run
meas tran cell_fall TRIG v(en) VAL={THRESH_50} RISE=1 TARG v(bl) VAL={THRESH_50} FALL=1
meas tran fall_tran TRIG v(bl) VAL={THRESH_80} FALL=1 TARG v(bl) VAL={THRESH_20} FALL=1
quit
.endc
.end
"""


def gen_cap_measure():
    """Input capacitance measurement via AC analysis at 1 GHz."""
    return f"""\
* BL Write Driver input capacitance measurement
.lib "{PDK_LIB}" tt
{DUT_SUBCKT}
VDD vdd 0 {VDD}
VSS vss 0 0

* Measure EN capacitance: apply AC 1V at EN, measure imaginary current
VEN en 0 DC 0.9 AC 1
VDATA data 0 {VDD}
X1 en data bl vdd vss bl_write_driver
CL bl 0 10f

.ac dec 10 1meg 10g

.control
run
let cap_1g = abs(imag(i(VEN))) / (2 * 3.14159265 * 1e9)
print cap_1g[length(cap_1g)-1]
quit
.endc
.end
"""


# ─── Simulation Runner ───────────────────────────────────────────────────────

def run_ngspice(spice_file, log_file):
    """Run ngspice in batch mode. Returns log text."""
    try:
        result = subprocess.run(
            [NGSPICE, "-b", spice_file, "-o", log_file],
            capture_output=True, text=True, timeout=60
        )
    except subprocess.TimeoutExpired:
        return ""
    try:
        with open(log_file, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return result.stdout + result.stderr


def parse_measure(log_text, name):
    """Parse a .meas result value from ngspice log output.
    Format: 'name = 1.23456e-10 targ=...' or 'name = 1.23456e-10'"""
    pattern = rf'^\s*{name}\s*=\s*([-+]?\d+\.?\d*[eE][-+]?\d+)'
    match = re.search(pattern, log_text, re.MULTILINE | re.IGNORECASE)
    if match:
        val = float(match.group(1))
        if val > 0:
            return val
    return None


def _run_one_sim(args):
    """Worker function for parallel simulation. Must be top-level for pickling."""
    spice_content, spice_file, log_file, meas_delay_name, meas_tran_name = args
    with open(spice_file, 'w') as f:
        f.write(spice_content)
    log_text = run_ngspice(spice_file, log_file)
    delay = parse_measure(log_text, meas_delay_name)
    tran = parse_measure(log_text, meas_tran_name)
    return (delay, tran)


def characterize_arc(arc_name, gen_func, meas_delay_name, meas_tran_name):
    """Run a full 7x7 sweep for one timing arc direction (parallel)."""
    n_slew = len(INPUT_SLEWS_NS)
    n_load = len(OUTPUT_LOADS_PF)
    delay_table = [[0.0]*n_load for _ in range(n_slew)]
    tran_table = [[0.0]*n_load for _ in range(n_slew)]

    # Build all jobs
    jobs = []
    job_idx = []  # (i, j) mapping
    for i, slew in enumerate(INPUT_SLEWS_NS):
        for j, load in enumerate(OUTPUT_LOADS_PF):
            tag = f"{arc_name}_s{i}_l{j}"
            spice_file = os.path.join(WORK_DIR, f"{tag}.spice")
            log_file = os.path.join(WORK_DIR, f"{tag}.log")
            spice_content = gen_func(slew, load)
            jobs.append((spice_content, spice_file, log_file, meas_delay_name, meas_tran_name))
            job_idx.append((i, j))

    # Run in parallel
    n_workers = min(cpu_count(), len(jobs))
    print(f"  Running {len(jobs)} sims on {n_workers} cores...")
    with Pool(n_workers) as pool:
        results = pool.map(_run_one_sim, jobs)

    # Collect results
    fail_count = 0
    for k, (delay, tran) in enumerate(results):
        i, j = job_idx[k]
        if delay is not None:
            delay_table[i][j] = delay * 1e9  # seconds → ns
        else:
            fail_count += 1
            delay_table[i][j] = 0.0
        if tran is not None:
            tran_table[i][j] = tran * 1e9
        else:
            tran_table[i][j] = 0.0

    if fail_count > 0:
        print(f"  WARNING: {fail_count}/{n_slew*n_load} measurements failed")

    return delay_table, tran_table


def interpolate_failures(table):
    """Replace zero/negative values with interpolated estimates."""
    n_rows = len(table)
    n_cols = len(table[0])
    for i in range(n_rows):
        for j in range(n_cols):
            if table[i][j] <= 0:
                # Try to interpolate from neighbors
                neighbors = []
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < n_rows and 0 <= nj < n_cols and table[ni][nj] > 0:
                            neighbors.append(table[ni][nj])
                if neighbors:
                    table[i][j] = sum(neighbors) / len(neighbors)
                else:
                    table[i][j] = 0.001  # fallback 1ps
    return table


# ─── Liberty File Writer ─────────────────────────────────────────────────────

def format_table_values(table):
    """Format a 7x7 table as Liberty values() string."""
    lines = []
    for i in range(len(table)):
        row = ", ".join(f"{table[i][j]:.5f}" for j in range(len(table[0])))
        lines.append(f'            "{row}"')
    return ", \\\n".join(lines)


def write_liberty(results, cap_en, cap_data, output_file):
    """Generate the complete Liberty (.lib) file."""
    slew_str = ", ".join(f"{s:.4f}" for s in INPUT_SLEWS_NS)
    load_str = ", ".join(f"{l:.5f}" for l in OUTPUT_LOADS_PF)

    data_rise_delay = format_table_values(results['data_rise_delay'])
    data_rise_tran = format_table_values(results['data_rise_tran'])
    data_fall_delay = format_table_values(results['data_fall_delay'])
    data_fall_tran = format_table_values(results['data_fall_tran'])
    en_rise_delay = format_table_values(results['en_rise_delay'])
    en_rise_tran = format_table_values(results['en_rise_tran'])
    en_fall_delay = format_table_values(results['en_fall_delay'])
    en_fall_tran = format_table_values(results['en_fall_tran'])

    lib_content = f"""\
library (bl_write_driver) {{
  comment : "Characterized with ngspice, Sky130B tt corner, 25C";
  technology (cmos);
  delay_model : table_lookup;
  time_unit : "1ns";
  voltage_unit : "1v";
  current_unit : "1uA";
  pulling_resistance_unit : "1kohm";
  capacitive_load_unit (1, pF);

  nom_process : 1.0;
  nom_temperature : 25.0;
  nom_voltage : 1.80;

  input_threshold_pct_rise : 50;
  input_threshold_pct_fall : 50;
  output_threshold_pct_rise : 50;
  output_threshold_pct_fall : 50;
  slew_lower_threshold_pct_rise : 20;
  slew_upper_threshold_pct_rise : 80;
  slew_lower_threshold_pct_fall : 20;
  slew_upper_threshold_pct_fall : 80;

  default_cell_leakage_power : 0;
  default_fanout_load : 1;
  default_output_pin_cap : 0.0;
  default_input_pin_cap : 0.0;
  default_inout_pin_cap : 0.0;

  operating_conditions (typical) {{
    process : 1.0;
    temperature : 25.0;
    voltage : 1.80;
  }}
  default_operating_conditions : typical;

  lu_table_template (delay_template_7x7) {{
    variable_1 : input_net_transition;
    variable_2 : total_output_net_capacitance;
    index_1 ("{slew_str}");
    index_2 ("{load_str}");
  }}

  cell (bl_write_driver) {{
    is_macro_cell : true;
    dont_touch : true;
    dont_use : true;
    area : 1026.176;

    pin (VDD) {{
      direction : inout;
    }}
    pg_pin (VDD) {{
      voltage_name : VDD;
      pg_type : primary_power;
    }}

    pin (VSS) {{
      direction : inout;
    }}
    pg_pin (VSS) {{
      voltage_name : VSS;
      pg_type : primary_ground;
    }}

    pin (EN) {{
      direction : input;
      capacitance : {cap_en:.6f};
    }}

    pin (DATA) {{
      direction : input;
      capacitance : {cap_data:.6f};
    }}

    pin (BL) {{
      direction : output;
      max_capacitance : 0.5;
      function : "DATA";
      three_state : "(!EN)";

      timing () {{
        related_pin : "DATA";
        timing_sense : positive_unate;

        cell_rise (delay_template_7x7) {{
          values ( \\
{data_rise_delay} \\
          );
        }}
        rise_transition (delay_template_7x7) {{
          values ( \\
{data_rise_tran} \\
          );
        }}
        cell_fall (delay_template_7x7) {{
          values ( \\
{data_fall_delay} \\
          );
        }}
        fall_transition (delay_template_7x7) {{
          values ( \\
{data_fall_tran} \\
          );
        }}
      }}

      timing () {{
        related_pin : "EN";
        timing_type : three_state_enable;

        cell_rise (delay_template_7x7) {{
          values ( \\
{en_rise_delay} \\
          );
        }}
        rise_transition (delay_template_7x7) {{
          values ( \\
{en_rise_tran} \\
          );
        }}
        cell_fall (delay_template_7x7) {{
          values ( \\
{en_fall_delay} \\
          );
        }}
        fall_transition (delay_template_7x7) {{
          values ( \\
{en_fall_tran} \\
          );
        }}
      }}
    }}
  }}
}}
"""
    with open(output_file, 'w') as f:
        f.write(lib_content)


# ─── Input Capacitance Measurement ──────────────────────────────────────────

def measure_input_cap():
    """Measure EN and DATA input capacitance via ngspice AC analysis.
    Falls back to gate-area estimation if AC measurement fails."""

    # Estimate from gate areas (Cox ≈ 8.8 fF/μm² for sky130 01v8)
    COX = 8.8e-3  # pF/μm²
    # EN: MP0(0.5×0.15) + MN0(0.5×0.15) + MN1(4×0.15) = 0.075+0.075+0.6 = 0.75 μm²
    cap_en_est = COX * 0.75  # ~0.0066 pF → 6.6 fF
    # DATA: MP3(0.5×0.15) + MN3(0.5×0.15) = 0.15 μm²
    cap_data_est = COX * 0.15  # ~0.00132 pF → 1.3 fF

    # Try AC measurement for EN
    spice_file = os.path.join(WORK_DIR, "cap_en.spice")
    log_file = os.path.join(WORK_DIR, "cap_en.log")
    with open(spice_file, 'w') as f:
        f.write(gen_cap_measure())
    log_text = run_ngspice(spice_file, log_file)

    # Parse AC result
    match = re.search(r'cap_1g\S*\s*=\s*([-+]?\d+\.?\d*[eE][-+]?\d+)', log_text)
    if match:
        cap_en = abs(float(match.group(1)))
        if cap_en > 1e-15 and cap_en < 1e-10:  # sanity: 0.001pF to 100pF
            cap_en_pf = cap_en * 1e12  # F → pF
            print(f"  EN cap (AC measured): {cap_en_pf*1000:.1f} fF")
        else:
            cap_en_pf = cap_en_est
            print(f"  EN cap (estimated):   {cap_en_pf*1000:.1f} fF")
    else:
        cap_en_pf = cap_en_est
        print(f"  EN cap (estimated):   {cap_en_pf*1000:.1f} fF")

    # DATA: use estimation (same method, smaller gates)
    cap_data_pf = cap_data_est
    print(f"  DATA cap (estimated): {cap_data_pf*1000:.1f} fF")

    return cap_en_pf, cap_data_pf


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    start_time = time.time()

    print("=" * 60)
    print(" BL Write Driver Liberty Characterization")
    print(f" ngspice: {NGSPICE}")
    print(f" PDK:     sky130B tt corner")
    print(f" Sweep:   {len(INPUT_SLEWS_NS)} slews × {len(OUTPUT_LOADS_PF)} loads")
    print("=" * 60)

    results = {}

    # ── Arc 1: DATA → BL cell_rise (DATA↓ → BL↑) ──
    print("\n[1/4] DATA → BL cell_rise (DATA falls → BL rises)")
    d, t = characterize_arc("data_rise", gen_data_rise, "cell_rise", "rise_tran")
    results['data_rise_delay'] = interpolate_failures(d)
    results['data_rise_tran'] = interpolate_failures(t)
    dr = [v for row in d for v in row if v > 0]
    if dr:
        print(f"  Delay: {min(dr):.4f} ~ {max(dr):.4f} ns")

    # ── Arc 2: DATA → BL cell_fall (DATA↑ → BL↓) ──
    print("\n[2/4] DATA → BL cell_fall (DATA rises → BL falls)")
    d, t = characterize_arc("data_fall", gen_data_fall, "cell_fall", "fall_tran")
    results['data_fall_delay'] = interpolate_failures(d)
    results['data_fall_tran'] = interpolate_failures(t)
    dr = [v for row in d for v in row if v > 0]
    if dr:
        print(f"  Delay: {min(dr):.4f} ~ {max(dr):.4f} ns")

    # ── Arc 3: EN → BL cell_rise (EN↑, DATA=1 → BL↑) ──
    print("\n[3/4] EN → BL cell_rise (EN enables, DATA=1 → BL rises)")
    d, t = characterize_arc("en_rise", gen_en_rise, "cell_rise", "rise_tran")
    results['en_rise_delay'] = interpolate_failures(d)
    results['en_rise_tran'] = interpolate_failures(t)
    dr = [v for row in d for v in row if v > 0]
    if dr:
        print(f"  Delay: {min(dr):.4f} ~ {max(dr):.4f} ns")

    # ── Arc 4: EN → BL cell_fall (EN↑, DATA=0 → BL↓) ──
    print("\n[4/4] EN → BL cell_fall (EN enables, DATA=0 → BL falls)")
    d, t = characterize_arc("en_fall", gen_en_fall, "cell_fall", "fall_tran")
    results['en_fall_delay'] = interpolate_failures(d)
    results['en_fall_tran'] = interpolate_failures(t)
    dr = [v for row in d for v in row if v > 0]
    if dr:
        print(f"  Delay: {min(dr):.4f} ~ {max(dr):.4f} ns")

    # ── Input Capacitance ──
    print("\n[Cap] Input Capacitance Measurement")
    cap_en, cap_data = measure_input_cap()

    # ── Write Liberty ──
    output_file = "bl_write_driver.lib"
    print(f"\n[Lib] Writing Liberty file: {output_file}")
    write_liberty(results, cap_en, cap_data, output_file)

    elapsed = time.time() - start_time
    n_sims = 4 * len(INPUT_SLEWS_NS) * len(OUTPUT_LOADS_PF) + 1
    print(f"\n{'=' * 60}")
    print(f" Done! {n_sims} simulations in {elapsed:.1f}s ({elapsed/n_sims:.2f}s/sim)")
    print(f" Output: {os.path.abspath(output_file)}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
