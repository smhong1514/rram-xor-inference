#!/usr/bin/env python3
"""
char_wl_driver.py - WL Driver Liberty Characterization

Level shifter: IN(1.8V) → OUT(VWL=3.3V). positive_unate buffer.
8 transistors: 2x 1.8V (input inverter) + 6x 5V HV (level shifter + buffer)

Timing arcs:
  IN → OUT (positive_unate): IN↑→OUT↑, IN↓→OUT↓

Sweep: 7 input_slew × 7 output_load = 49 points per direction
Total: 2 arcs × 49 + 1 cap = 99 simulations

Usage: cd ~/rram_openlane/analog/layout/wl_driver && python3 char_wl_driver.py
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
VWL = 3.3    # WL high voltage
THRESH_50 = VDD * 0.5   # 0.9V - input & output delay threshold
THRESH_20 = VDD * 0.2   # 0.36V - output slew threshold
THRESH_80 = VDD * 0.8   # 1.44V - output slew threshold

SETTLE_NS = 5.0
SIM_END_NS = 50.0
TSTEP_NS = 0.005

INPUT_SLEWS_NS = [0.0100, 0.0230, 0.0540, 0.1280, 0.3000, 0.7000, 1.6500]
OUTPUT_LOADS_PF = [0.0005, 0.00146, 0.00429, 0.01257, 0.03681, 0.10783, 0.31587]

WORK_DIR = "char_work"

# ─── DUT Subcircuit ──────────────────────────────────────────────────────────

DUT_SUBCKT = """\
.subckt wl_driver IN OUT VDD VWL VSS
XMP0 INB IN VDD VDD sky130_fd_pr__pfet_01v8 L=0.15 W=1 nf=1
XMN0 INB IN VSS VSS sky130_fd_pr__nfet_01v8 L=0.15 W=0.5 nf=1
XMP1 Q QB VWL VWL sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1
XMN1 Q IN VSS VSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=2 nf=1
XMP2 QB Q VWL VWL sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1
XMN2 QB INB VSS VSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=2 nf=1
XMP3 OUT Q VWL VWL sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=4 nf=1
XMN3 OUT Q VSS VSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=2 nf=1
.ends wl_driver
"""


# ─── SPICE Deck Generators ──────────────────────────────────────────────────

def slew_20_80_to_pwl(slew_ns):
    return slew_ns / 0.6


def gen_in_rise(slew_ns, load_pf):
    """IN→OUT cell_rise: IN rises (0→VDD), OUT rises (0→VWL). positive_unate."""
    pwl = slew_20_80_to_pwl(slew_ns)
    t_start = SETTLE_NS
    t_end = t_start + pwl
    return f"""\
* WL Driver char: IN->OUT cell_rise (slew={slew_ns}ns, load={load_pf}pF)
.lib "{PDK_LIB}" tt
{DUT_SUBCKT}
VDD vdd 0 {VDD}
VVWL vwl 0 {VWL}
VSS vss 0 0
VIN in 0 PWL(0 0 {t_start}n 0 {t_end}n {VDD})
X1 in out vdd vwl vss wl_driver
CL out 0 {load_pf}p
R_init out 0 1G

.tran {TSTEP_NS}n {SIM_END_NS}n

.control
run
meas tran cell_rise TRIG v(in) VAL={THRESH_50} RISE=1 TARG v(out) VAL={THRESH_50} RISE=1
meas tran rise_tran TRIG v(out) VAL={THRESH_20} RISE=1 TARG v(out) VAL={THRESH_80} RISE=1
quit
.endc
.end
"""


def gen_in_fall(slew_ns, load_pf):
    """IN→OUT cell_fall: IN falls (VDD→0), OUT falls (VWL→0). positive_unate."""
    pwl = slew_20_80_to_pwl(slew_ns)
    t_start = SETTLE_NS
    t_end = t_start + pwl
    return f"""\
* WL Driver char: IN->OUT cell_fall (slew={slew_ns}ns, load={load_pf}pF)
.lib "{PDK_LIB}" tt
{DUT_SUBCKT}
VDD vdd 0 {VDD}
VVWL vwl 0 {VWL}
VSS vss 0 0
VIN in 0 PWL(0 {VDD} {t_start}n {VDD} {t_end}n 0)
X1 in out vdd vwl vss wl_driver
CL out 0 {load_pf}p
R_init out vwl 1G

.tran {TSTEP_NS}n {SIM_END_NS}n

.control
run
meas tran cell_fall TRIG v(in) VAL={THRESH_50} FALL=1 TARG v(out) VAL={THRESH_50} FALL=1
meas tran fall_tran TRIG v(out) VAL={THRESH_80} FALL=1 TARG v(out) VAL={THRESH_20} FALL=1
quit
.endc
.end
"""


def gen_cap_measure():
    """IN input capacitance measurement via AC analysis."""
    return f"""\
* WL Driver input capacitance measurement
.lib "{PDK_LIB}" tt
{DUT_SUBCKT}
VDD vdd 0 {VDD}
VVWL vwl 0 {VWL}
VSS vss 0 0
VIN in 0 DC 0.9 AC 1
X1 in out vdd vwl vss wl_driver
CL out 0 10f

.ac dec 10 1meg 10g

.control
run
let cap_in = abs(imag(i(VIN))) / (2 * 3.14159265 * 1e9)
print cap_in[length(cap_in)-1]
quit
.endc
.end
"""


# ─── Simulation Runner ───────────────────────────────────────────────────────

def run_ngspice(spice_file, log_file):
    try:
        result = subprocess.run(
            [NGSPICE, "-b", spice_file, "-o", log_file],
            capture_output=True, text=True, timeout=120
        )
    except subprocess.TimeoutExpired:
        return ""
    try:
        with open(log_file, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return result.stdout + result.stderr


def parse_measure(log_text, name):
    pattern = rf'^\s*{name}\s*=\s*([-+]?\d+\.?\d*[eE][-+]?\d+)'
    match = re.search(pattern, log_text, re.MULTILINE | re.IGNORECASE)
    if match:
        val = float(match.group(1))
        if val > 0:
            return val
    return None


def _run_one_sim(args):
    spice_content, spice_file, log_file, meas_delay_name, meas_tran_name = args
    with open(spice_file, 'w') as f:
        f.write(spice_content)
    log_text = run_ngspice(spice_file, log_file)
    delay = parse_measure(log_text, meas_delay_name)
    tran = parse_measure(log_text, meas_tran_name)
    return (delay, tran)


def characterize_arc(arc_name, gen_func, meas_delay_name, meas_tran_name):
    n_slew = len(INPUT_SLEWS_NS)
    n_load = len(OUTPUT_LOADS_PF)
    delay_table = [[0.0]*n_load for _ in range(n_slew)]
    tran_table = [[0.0]*n_load for _ in range(n_slew)]

    jobs = []
    job_idx = []
    for i, slew in enumerate(INPUT_SLEWS_NS):
        for j, load in enumerate(OUTPUT_LOADS_PF):
            tag = f"{arc_name}_s{i}_l{j}"
            spice_file = os.path.join(WORK_DIR, f"{tag}.spice")
            log_file = os.path.join(WORK_DIR, f"{tag}.log")
            spice_content = gen_func(slew, load)
            jobs.append((spice_content, spice_file, log_file, meas_delay_name, meas_tran_name))
            job_idx.append((i, j))

    n_workers = min(cpu_count(), len(jobs))
    print(f"  Running {len(jobs)} sims on {n_workers} cores...")
    with Pool(n_workers) as pool:
        results = pool.map(_run_one_sim, jobs)

    fail_count = 0
    for k, (delay, tran) in enumerate(results):
        i, j = job_idx[k]
        if delay is not None:
            delay_table[i][j] = delay * 1e9
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
    n_rows = len(table)
    n_cols = len(table[0])
    for i in range(n_rows):
        for j in range(n_cols):
            if table[i][j] <= 0:
                neighbors = []
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < n_rows and 0 <= nj < n_cols and table[ni][nj] > 0:
                            neighbors.append(table[ni][nj])
                if neighbors:
                    table[i][j] = sum(neighbors) / len(neighbors)
                else:
                    table[i][j] = 0.001
    return table


# ─── Liberty File Writer ─────────────────────────────────────────────────────

def format_table_values(table):
    lines = []
    for i in range(len(table)):
        row = ", ".join(f"{table[i][j]:.5f}" for j in range(len(table[0])))
        lines.append(f'            "{row}"')
    return ", \\\n".join(lines)


def write_liberty(results, cap_in, output_file):
    slew_str = ", ".join(f"{s:.4f}" for s in INPUT_SLEWS_NS)
    load_str = ", ".join(f"{l:.5f}" for l in OUTPUT_LOADS_PF)

    in_rise_delay = format_table_values(results['in_rise_delay'])
    in_rise_tran = format_table_values(results['in_rise_tran'])
    in_fall_delay = format_table_values(results['in_fall_delay'])
    in_fall_tran = format_table_values(results['in_fall_tran'])

    lib_content = f"""\
library (wl_driver) {{
  comment : "Characterized with ngspice, Sky130B tt corner, 25C";
  comment : "Level shifter 1.8V->VWL(3.3V), thresholds at VDD(1.8V) domain";
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

  cell (wl_driver) {{
    is_macro_cell : true;
    dont_touch : true;
    dont_use : true;
    area : 156.735;

    pin (VDD) {{
      direction : inout;
    }}
    pg_pin (VDD) {{
      voltage_name : VDD;
      pg_type : primary_power;
    }}

    pin (VWL) {{
      direction : inout;
    }}
    pg_pin (VWL) {{
      voltage_name : VWL;
      pg_type : primary_power;
    }}

    pin (VSS) {{
      direction : inout;
    }}
    pg_pin (VSS) {{
      voltage_name : VSS;
      pg_type : primary_ground;
    }}

    pin (IN) {{
      direction : input;
      capacitance : {cap_in:.6f};
    }}

    pin (OUT) {{
      direction : output;
      max_capacitance : 0.5;
      function : "IN";

      timing () {{
        related_pin : "IN";
        timing_sense : positive_unate;

        cell_rise (delay_template_7x7) {{
          values ( \\
{in_rise_delay} \\
          );
        }}
        rise_transition (delay_template_7x7) {{
          values ( \\
{in_rise_tran} \\
          );
        }}
        cell_fall (delay_template_7x7) {{
          values ( \\
{in_fall_delay} \\
          );
        }}
        fall_transition (delay_template_7x7) {{
          values ( \\
{in_fall_tran} \\
          );
        }}
      }}
    }}
  }}
}}
"""
    with open(output_file, 'w') as f:
        f.write(lib_content)


# ─── Input Capacitance ───────────────────────────────────────────────────────

def measure_input_cap():
    COX = 8.8e-3  # pF/μm²
    # IN drives: MP0(1×0.15) + MN0(0.5×0.15) + MN1(2×0.5) = 0.15+0.075+1.0 = 1.225 μm²
    cap_in_est = COX * 1.225  # ~10.8 fF

    spice_file = os.path.join(WORK_DIR, "cap_in.spice")
    log_file = os.path.join(WORK_DIR, "cap_in.log")
    with open(spice_file, 'w') as f:
        f.write(gen_cap_measure())
    log_text = run_ngspice(spice_file, log_file)

    match = re.search(r'cap_in\S*\s*=\s*([-+]?\d+\.?\d*[eE][-+]?\d+)', log_text)
    if match:
        cap = abs(float(match.group(1)))
        if 1e-15 < cap < 1e-10:
            cap_in = cap * 1e12
            print(f"  IN cap (AC measured): {cap_in*1000:.1f} fF")
        else:
            cap_in = cap_in_est
            print(f"  IN cap (estimated):   {cap_in*1000:.1f} fF")
    else:
        cap_in = cap_in_est
        print(f"  IN cap (estimated):   {cap_in*1000:.1f} fF")

    return cap_in


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    start_time = time.time()

    print("=" * 60)
    print(" WL Driver Liberty Characterization")
    print(f" ngspice: {NGSPICE}")
    print(f" PDK:     sky130B tt corner")
    print(f" VWL:     {VWL}V")
    print(f" Sweep:   {len(INPUT_SLEWS_NS)} slews × {len(OUTPUT_LOADS_PF)} loads")
    print("=" * 60)

    results = {}

    # ── Arc 1: IN → OUT cell_rise ──
    print("\n[1/2] IN → OUT cell_rise (IN↑ → OUT↑)")
    d, t = characterize_arc("in_rise", gen_in_rise, "cell_rise", "rise_tran")
    results['in_rise_delay'] = interpolate_failures(d)
    results['in_rise_tran'] = interpolate_failures(t)
    dr = [v for row in d for v in row if v > 0]
    if dr:
        print(f"  Delay: {min(dr):.4f} ~ {max(dr):.4f} ns")

    # ── Arc 2: IN → OUT cell_fall ──
    print("\n[2/2] IN → OUT cell_fall (IN↓ → OUT↓)")
    d, t = characterize_arc("in_fall", gen_in_fall, "cell_fall", "fall_tran")
    results['in_fall_delay'] = interpolate_failures(d)
    results['in_fall_tran'] = interpolate_failures(t)
    dr = [v for row in d for v in row if v > 0]
    if dr:
        print(f"  Delay: {min(dr):.4f} ~ {max(dr):.4f} ns")

    # ── Input Capacitance ──
    print("\n[Cap] Input Capacitance Measurement")
    cap_in = measure_input_cap()

    # ── Write Liberty ──
    output_file = "wl_driver.lib"
    print(f"\n[Lib] Writing Liberty file: {output_file}")
    write_liberty(results, cap_in, output_file)

    elapsed = time.time() - start_time
    n_sims = 2 * len(INPUT_SLEWS_NS) * len(OUTPUT_LOADS_PF) + 1
    print(f"\n{'=' * 60}")
    print(f" Done! {n_sims} simulations in {elapsed:.1f}s ({elapsed/n_sims:.2f}s/sim)")
    print(f" Output: {os.path.abspath(output_file)}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
