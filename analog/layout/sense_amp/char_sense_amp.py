#!/usr/bin/env python3
"""
char_sense_amp.py - Sense Amplifier Liberty Characterization

StrongARM Latch-type SA: SAE=0 precharge (Q=QB=VDD), SAE=1 evaluate.
Timing arcs:
  SAE → Q  (negative_unate): SAE↑→Q↓ (evaluate), SAE↓→Q↑ (precharge)
  SAE → QB (negative_unate): same by symmetry (swapped INP/INN)

Sweep: 7 input_slew × 7 output_load = 49 points per direction
Total: 2 arcs × 49 + 1 cap = 99 simulations

Usage: cd ~/rram_openlane/analog/layout/sense_amp && python3 char_sense_amp.py
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

# Differential input: 50mV (worst-case for timing)
V_INP = 0.925  # BL voltage (higher)
V_INN = 0.875  # BLB voltage (lower)

TSTEP_NS = 0.005

# Sky130 standard sweep parameters
INPUT_SLEWS_NS = [0.0100, 0.0230, 0.0540, 0.1280, 0.3000, 0.7000, 1.6500]
OUTPUT_LOADS_PF = [0.0005, 0.00146, 0.00429, 0.01257, 0.03681, 0.10783, 0.31587]

WORK_DIR = "char_work"

# ─── DUT Subcircuit ──────────────────────────────────────────────────────────

DUT_SUBCKT = """\
.subckt sense_amp SAE INP INN Q QB VDD VSS
XMP3 Q SAE VDD VDD sky130_fd_pr__pfet_01v8 L=0.15 W=0.5 nf=1 mult=1
XMP4 QB SAE VDD VDD sky130_fd_pr__pfet_01v8 L=0.15 W=0.5 nf=1 mult=1
XMP5 QB SAE Q VDD sky130_fd_pr__pfet_01v8 L=0.15 W=0.5 nf=1 mult=1
XMP1 Q QB VDD VDD sky130_fd_pr__pfet_01v8 L=0.15 W=1 nf=1 mult=1
XMP2 QB Q VDD VDD sky130_fd_pr__pfet_01v8 L=0.15 W=1 nf=1 mult=1
XMN1 Q QB FN1 VSS sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 mult=1
XMN2 QB Q FN2 VSS sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 mult=1
XMN3 FN1 INP TAIL VSS sky130_fd_pr__nfet_01v8 L=0.15 W=2 nf=1 mult=1
XMN4 FN2 INN TAIL VSS sky130_fd_pr__nfet_01v8 L=0.15 W=2 nf=1 mult=1
XMN0 TAIL SAE VSS VSS sky130_fd_pr__nfet_01v8 L=0.15 W=2 nf=1 mult=1
.ends sense_amp
"""


# ─── SPICE Deck Generators ──────────────────────────────────────────────────

def slew_20_80_to_pwl(slew_ns):
    """Convert 20%-80% slew to 0%-100% PWL transition time."""
    return slew_ns / 0.6


def gen_evaluate(slew_ns, load_pf):
    """SAE → Q cell_fall (evaluate): SAE rises, Q falls to 0.
    Phase: 0-5ns precharge (SAE=0, Q=VDD), then SAE rises."""
    pwl = slew_20_80_to_pwl(slew_ns)
    t_start = 5.0
    t_end = t_start + pwl
    sim_end = t_end + 30.0
    return f"""\
* SA char: SAE->Q cell_fall evaluate (slew={slew_ns}ns, load={load_pf}pF)
.lib "{PDK_LIB}" tt
{DUT_SUBCKT}
VDD vdd 0 {VDD}
VSS vss 0 0
VINP inp 0 {V_INP}
VINN inn 0 {V_INN}
VSAE sae 0 PWL(0 0 {t_start}n 0 {t_end}n {VDD})
X1 sae inp inn q qb vdd vss sense_amp
CQ q 0 {load_pf}p
CQB qb 0 {load_pf}p

.tran {TSTEP_NS}n {sim_end}n

.control
run
meas tran cell_fall TRIG v(sae) VAL={THRESH_50} RISE=1 TARG v(q) VAL={THRESH_50} FALL=1
meas tran fall_tran TRIG v(q) VAL={THRESH_80} FALL=1 TARG v(q) VAL={THRESH_20} FALL=1
quit
.endc
.end
"""


def gen_precharge(slew_ns, load_pf):
    """SAE → Q cell_rise (precharge): SAE falls, Q rises back to VDD.
    Phase 1 (0-2ns): precharge (SAE=0) → Q=VDD
    Phase 2 (2-10ns): evaluate (SAE=1) → Q resolves to 0
    Phase 3 (10ns+): SAE falls → Q rises (measured)"""
    pwl = slew_20_80_to_pwl(slew_ns)
    t_eval_start = 2.0
    t_meas_start = 10.0
    t_meas_end = t_meas_start + pwl
    sim_end = t_meas_end + 30.0
    return f"""\
* SA char: SAE->Q cell_rise precharge (slew={slew_ns}ns, load={load_pf}pF)
.lib "{PDK_LIB}" tt
{DUT_SUBCKT}
VDD vdd 0 {VDD}
VSS vss 0 0
VINP inp 0 {V_INP}
VINN inn 0 {V_INN}
VSAE sae 0 PWL(0 0 {t_eval_start}n 0 {t_eval_start + 0.01}n {VDD} {t_meas_start}n {VDD} {t_meas_end}n 0)
X1 sae inp inn q qb vdd vss sense_amp
CQ q 0 {load_pf}p
CQB qb 0 {load_pf}p

.tran {TSTEP_NS}n {sim_end}n

.control
run
meas tran cell_rise TRIG v(sae) VAL={THRESH_50} TD=5n FALL=1 TARG v(q) VAL={THRESH_50} TD=5n RISE=1
meas tran rise_tran TRIG v(q) VAL={THRESH_20} TD=5n RISE=1 TARG v(q) VAL={THRESH_80} TD=5n RISE=1
quit
.endc
.end
"""


def gen_cap_measure():
    """Input capacitance measurement via AC analysis."""
    return f"""\
* SA input capacitance measurement
.lib "{PDK_LIB}" tt
{DUT_SUBCKT}
VDD vdd 0 {VDD}
VSS vss 0 0

* Measure SAE capacitance
VSAE sae 0 DC 0 AC 1
VINP inp 0 {V_INP}
VINN inn 0 {V_INN}
X1 sae inp inn q qb vdd vss sense_amp
CQ q 0 10f
CQB qb 0 10f

.ac dec 10 1meg 10g

.control
run
let cap_sae = abs(imag(i(VSAE))) / (2 * 3.14159265 * 1e9)
print cap_sae[length(cap_sae)-1]
quit
.endc
.end
"""


def gen_cap_inp_measure():
    """INP input capacitance measurement via AC analysis."""
    return f"""\
* SA INP capacitance measurement
.lib "{PDK_LIB}" tt
{DUT_SUBCKT}
VDD vdd 0 {VDD}
VSS vss 0 0

VSAE sae 0 0
VINP inp 0 DC {V_INP} AC 1
VINN inn 0 {V_INN}
X1 sae inp inn q qb vdd vss sense_amp
CQ q 0 10f
CQB qb 0 10f

.ac dec 10 1meg 10g

.control
run
let cap_inp = abs(imag(i(VINP))) / (2 * 3.14159265 * 1e9)
print cap_inp[length(cap_inp)-1]
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
    """Parse a .meas result value from ngspice log output."""
    pattern = rf'^\s*{name}\s*=\s*([-+]?\d+\.?\d*[eE][-+]?\d+)'
    match = re.search(pattern, log_text, re.MULTILINE | re.IGNORECASE)
    if match:
        val = float(match.group(1))
        if val > 0:
            return val
    return None


def _run_one_sim(args):
    """Worker function for parallel simulation."""
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
    job_idx = []
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
    """Replace zero/negative values with interpolated estimates."""
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
    """Format a 7x7 table as Liberty values() string."""
    lines = []
    for i in range(len(table)):
        row = ", ".join(f"{table[i][j]:.5f}" for j in range(len(table[0])))
        lines.append(f'            "{row}"')
    return ", \\\n".join(lines)


def write_liberty(results, cap_sae, cap_inp, output_file):
    """Generate the complete Liberty (.lib) file."""
    slew_str = ", ".join(f"{s:.4f}" for s in INPUT_SLEWS_NS)
    load_str = ", ".join(f"{l:.5f}" for l in OUTPUT_LOADS_PF)

    eval_fall_delay = format_table_values(results['eval_fall_delay'])
    eval_fall_tran = format_table_values(results['eval_fall_tran'])
    prech_rise_delay = format_table_values(results['prech_rise_delay'])
    prech_rise_tran = format_table_values(results['prech_rise_tran'])

    lib_content = f"""\
library (sense_amp) {{
  comment : "Characterized with ngspice, Sky130B tt corner, 25C";
  comment : "StrongARM latch SA, dV=50mV, Q/QB symmetric";
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

  cell (sense_amp) {{
    is_macro_cell : true;
    dont_touch : true;
    dont_use : true;
    area : 816.160;

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

    pin (SAE) {{
      direction : input;
      capacitance : {cap_sae:.6f};
    }}

    pin (INP) {{
      direction : input;
      capacitance : {cap_inp:.6f};
    }}

    pin (INN) {{
      direction : input;
      capacitance : {cap_inp:.6f};
    }}

    pin (Q) {{
      direction : output;
      max_capacitance : 0.5;

      timing () {{
        related_pin : "SAE";
        timing_sense : negative_unate;

        cell_rise (delay_template_7x7) {{
          values ( \\
{prech_rise_delay} \\
          );
        }}
        rise_transition (delay_template_7x7) {{
          values ( \\
{prech_rise_tran} \\
          );
        }}
        cell_fall (delay_template_7x7) {{
          values ( \\
{eval_fall_delay} \\
          );
        }}
        fall_transition (delay_template_7x7) {{
          values ( \\
{eval_fall_tran} \\
          );
        }}
      }}
    }}

    pin (QB) {{
      direction : output;
      max_capacitance : 0.5;

      timing () {{
        related_pin : "SAE";
        timing_sense : negative_unate;

        cell_rise (delay_template_7x7) {{
          values ( \\
{prech_rise_delay} \\
          );
        }}
        rise_transition (delay_template_7x7) {{
          values ( \\
{prech_rise_tran} \\
          );
        }}
        cell_fall (delay_template_7x7) {{
          values ( \\
{eval_fall_delay} \\
          );
        }}
        fall_transition (delay_template_7x7) {{
          values ( \\
{eval_fall_tran} \\
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
    """Measure SAE and INP input capacitance via AC analysis."""
    COX = 8.8e-3  # pF/μm² for sky130 01v8

    # SAE drives: MN0(W=2), MP3(W=0.5), MP4(W=0.5), MP5(W=0.5)
    # Total gate area: (2+0.5+0.5+0.5)×0.15 = 0.525 μm²
    cap_sae_est = COX * 0.525  # ~4.6 fF

    # INP drives: MN3(W=2) gate area = 2×0.15 = 0.3 μm²
    cap_inp_est = COX * 0.3  # ~2.6 fF

    # AC measurement for SAE
    spice_file = os.path.join(WORK_DIR, "cap_sae.spice")
    log_file = os.path.join(WORK_DIR, "cap_sae.log")
    with open(spice_file, 'w') as f:
        f.write(gen_cap_measure())
    log_text = run_ngspice(spice_file, log_file)

    match = re.search(r'cap_sae\S*\s*=\s*([-+]?\d+\.?\d*[eE][-+]?\d+)', log_text)
    if match:
        cap = abs(float(match.group(1)))
        if 1e-15 < cap < 1e-10:
            cap_sae = cap * 1e12
            print(f"  SAE cap (AC measured): {cap_sae*1000:.1f} fF")
        else:
            cap_sae = cap_sae_est
            print(f"  SAE cap (estimated):   {cap_sae*1000:.1f} fF")
    else:
        cap_sae = cap_sae_est
        print(f"  SAE cap (estimated):   {cap_sae*1000:.1f} fF")

    # AC measurement for INP
    spice_file = os.path.join(WORK_DIR, "cap_inp.spice")
    log_file = os.path.join(WORK_DIR, "cap_inp.log")
    with open(spice_file, 'w') as f:
        f.write(gen_cap_inp_measure())
    log_text = run_ngspice(spice_file, log_file)

    match = re.search(r'cap_inp\S*\s*=\s*([-+]?\d+\.?\d*[eE][-+]?\d+)', log_text)
    if match:
        cap = abs(float(match.group(1)))
        if 1e-15 < cap < 1e-10:
            cap_inp = cap * 1e12
            print(f"  INP/INN cap (AC measured): {cap_inp*1000:.1f} fF")
        else:
            cap_inp = cap_inp_est
            print(f"  INP/INN cap (estimated):   {cap_inp*1000:.1f} fF")
    else:
        cap_inp = cap_inp_est
        print(f"  INP/INN cap (estimated):   {cap_inp*1000:.1f} fF")

    return cap_sae, cap_inp


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    start_time = time.time()

    print("=" * 60)
    print(" Sense Amplifier Liberty Characterization")
    print(f" ngspice: {NGSPICE}")
    print(f" PDK:     sky130B tt corner")
    print(f" Input:   INP={V_INP}V, INN={V_INN}V (dV={1000*(V_INP-V_INN):.0f}mV)")
    print(f" Sweep:   {len(INPUT_SLEWS_NS)} slews × {len(OUTPUT_LOADS_PF)} loads")
    print("=" * 60)

    results = {}

    # ── Arc 1: SAE → Q cell_fall (evaluate) ──
    print("\n[1/2] SAE → Q cell_fall (evaluate: SAE↑ → Q↓)")
    d, t = characterize_arc("eval_fall", gen_evaluate, "cell_fall", "fall_tran")
    results['eval_fall_delay'] = interpolate_failures(d)
    results['eval_fall_tran'] = interpolate_failures(t)
    dr = [v for row in d for v in row if v > 0]
    if dr:
        print(f"  Delay: {min(dr):.4f} ~ {max(dr):.4f} ns")

    # ── Arc 2: SAE → Q cell_rise (precharge) ──
    print("\n[2/2] SAE → Q cell_rise (precharge: SAE↓ → Q↑)")
    d, t = characterize_arc("prech_rise", gen_precharge, "cell_rise", "rise_tran")
    results['prech_rise_delay'] = interpolate_failures(d)
    results['prech_rise_tran'] = interpolate_failures(t)
    dr = [v for row in d for v in row if v > 0]
    if dr:
        print(f"  Delay: {min(dr):.4f} ~ {max(dr):.4f} ns")

    # ── Input Capacitance ──
    print("\n[Cap] Input Capacitance Measurement")
    cap_sae, cap_inp = measure_input_cap()

    # ── Write Liberty ──
    output_file = "sense_amp.lib"
    print(f"\n[Lib] Writing Liberty file: {output_file}")
    write_liberty(results, cap_sae, cap_inp, output_file)

    elapsed = time.time() - start_time
    n_sims = 2 * len(INPUT_SLEWS_NS) * len(OUTPUT_LOADS_PF) + 2
    print(f"\n{'=' * 60}")
    print(f" Done! {n_sims} simulations in {elapsed:.1f}s ({elapsed/n_sims:.2f}s/sim)")
    print(f" Output: {os.path.abspath(output_file)}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
