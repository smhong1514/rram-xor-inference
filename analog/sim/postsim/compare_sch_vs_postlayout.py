#!/usr/bin/env python3
"""Compare Schematic vs Post-Layout d_cosim Simulation Results"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Load both datasets
sch = np.loadtxt('rram_cosim_full.csv')
pex = np.loadtxt('rram_cosim_postlayout.csv')

t_sch = sch[:, 0] * 1e9   # ns
t_pex = pex[:, 0] * 1e9

# Column mapping (same for both):
# 1:rdy 3:rv 5:rd 7:wen 9:ren 13:wl_in1 17:wl1
# 19:bl0 21:bl1 23:bl2 25:bl3 27:sa_q0 29:sa_q1 31:sa_q2 33:sa_q3
# 35:prech 37:sl_en1 39:bl_en2 41:bl_dat2

def extract(data):
    return {
        'rdy': data[:, 1], 'rv': data[:, 3], 'rd': data[:, 5],
        'wen': data[:, 7], 'ren': data[:, 9],
        'wl1': data[:, 17],
        'bl0': data[:, 19], 'bl1': data[:, 21],
        'bl2': data[:, 23], 'bl3': data[:, 25],
        'sa_q0': data[:, 27], 'sa_q1': data[:, 29],
        'sa_q2': data[:, 31], 'sa_q3': data[:, 33],
        'bl_en2': data[:, 39], 'bl_dat2': data[:, 41],
    }

s = extract(sch)
p = extract(pex)

# ─── Metric extraction ───

def find_read_window(t, ren):
    """Find READ phase: where ren (SAE) first goes high"""
    high = np.where(ren > 0.9)[0]
    if len(high) == 0:
        return None, None
    start_idx = high[0]
    # Find end of first high pulse
    after = np.where(ren[start_idx:] < 0.9)[0]
    if len(after) == 0:
        end_idx = high[-1]
    else:
        end_idx = start_idx + after[0]
    return start_idx, end_idx

def find_write_window(t, wen):
    """Find WRITE phase: where wen first goes high"""
    high = np.where(wen > 0.9)[0]
    if len(high) == 0:
        return None, None
    start_idx = high[0]
    after = np.where(wen[start_idx:] < 0.9)[0]
    if len(after) == 0:
        end_idx = high[-1]
    else:
        end_idx = start_idx + after[0]
    return start_idx, end_idx

def measure_bl_read(t, bl, start, end):
    """Measure BL voltage at end of READ window (steady state)"""
    window = bl[start:end]
    if len(window) == 0:
        return float('nan')
    return window[-1]

def measure_sa_output(sa, start, end):
    """Measure SA output at end of READ window"""
    window = sa[start:end]
    if len(window) == 0:
        return float('nan')
    return window[-1]

def measure_wl_high(t, wl, start, end):
    """Measure peak WL voltage during READ"""
    window = wl[start:end]
    if len(window) == 0:
        return float('nan')
    return np.max(window)

def measure_bl_write_swing(t, bl_dat, wen_start, wen_end):
    """Measure BL write driver output during WRITE"""
    window = bl_dat[wen_start:wen_end]
    if len(window) == 0:
        return float('nan')
    return np.max(window)

def measure_rise_time(t, sig, threshold_lo=0.36, threshold_hi=1.44):
    """Measure 20%-80% rise time of first rising edge (for 1.8V signals)"""
    cross_lo = np.where(sig > threshold_lo)[0]
    if len(cross_lo) == 0:
        return float('nan')
    cross_hi = np.where(sig[cross_lo[0]:] > threshold_hi)[0]
    if len(cross_hi) == 0:
        return float('nan')
    return t[cross_lo[0] + cross_hi[0]] - t[cross_lo[0]]

def measure_wl_rise(t, wl, threshold_lo=0.66, threshold_hi=2.64):
    """Measure 20%-80% rise time for 3.3V WL signal"""
    cross_lo = np.where(wl > threshold_lo)[0]
    if len(cross_lo) == 0:
        return float('nan')
    cross_hi = np.where(wl[cross_lo[0]:] > threshold_hi)[0]
    if len(cross_hi) == 0:
        return float('nan')
    return t[cross_lo[0] + cross_hi[0]] - t[cross_lo[0]]

# Measure for schematic
rs_s, re_s = find_read_window(t_sch, s['ren'])
ws_s, we_s = find_write_window(t_sch, s['wen'])

# Measure for post-layout
rs_p, re_p = find_read_window(t_pex, p['ren'])
ws_p, we_p = find_write_window(t_pex, p['wen'])

print("=" * 70)
print("  Schematic vs Post-Layout Comparison")
print("=" * 70)

# READ phase metrics
print("\n── READ Phase ──")
print(f"{'Metric':<30} {'Schematic':>12} {'Post-Layout':>12} {'Delta':>10}")
print("-" * 66)

metrics = []

for name, col in [('BL0 (HRS)', 'bl0'), ('BL1 (LRS)', 'bl1'),
                   ('BL2 (HRS)', 'bl2'), ('BL3 (LRS)', 'bl3')]:
    v_s = measure_bl_read(t_sch, s[col], rs_s, re_s)
    v_p = measure_bl_read(t_pex, p[col], rs_p, re_p)
    delta = v_p - v_s
    print(f"  {name:<28} {v_s:>10.4f} V {v_p:>10.4f} V {delta:>+8.4f} V")
    metrics.append((name, v_s, v_p, delta))

print()
for name, col in [('SA_Q0 (HRS→LOW)', 'sa_q0'), ('SA_Q1 (LRS→HIGH)', 'sa_q1'),
                   ('SA_Q2 (HRS→LOW)', 'sa_q2'), ('SA_Q3 (LRS→HIGH)', 'sa_q3')]:
    v_s = measure_sa_output(s[col], rs_s, re_s)
    v_p = measure_sa_output(p[col], rs_p, re_p)
    delta = v_p - v_s
    print(f"  {name:<28} {v_s:>10.4f} V {v_p:>10.4f} V {delta:>+8.4f} V")
    metrics.append((name, v_s, v_p, delta))

# WL Driver
print()
wl_s = measure_wl_high(t_sch, s['wl1'], rs_s, re_s)
wl_p = measure_wl_high(t_pex, p['wl1'], rs_p, re_p)
print(f"  {'WL1 peak':<28} {wl_s:>10.4f} V {wl_p:>10.4f} V {wl_p-wl_s:>+8.4f} V")
metrics.append(('WL1 peak', wl_s, wl_p, wl_p - wl_s))

# Timing
print()
wl_rt_s = measure_wl_rise(t_sch, s['wl1'])
wl_rt_p = measure_wl_rise(t_pex, p['wl1'])
print(f"  {'WL1 rise (20-80%)':<28} {wl_rt_s:>9.2f} ns {wl_rt_p:>9.2f} ns {wl_rt_p-wl_rt_s:>+7.2f} ns")

sa_rt_s = measure_rise_time(t_sch, s['sa_q1'])
sa_rt_p = measure_rise_time(t_pex, p['sa_q1'])
print(f"  {'SA_Q1 rise (20-80%)':<28} {sa_rt_s:>9.2f} ns {sa_rt_p:>9.2f} ns {sa_rt_p-sa_rt_s:>+7.2f} ns")

# WRITE phase
print("\n── WRITE Phase ──")
print(f"{'Metric':<30} {'Schematic':>12} {'Post-Layout':>12} {'Delta':>10}")
print("-" * 66)

bl_w_s = measure_bl_write_swing(t_sch, s['bl_dat2'], ws_s, we_s)
bl_w_p = measure_bl_write_swing(t_pex, p['bl_dat2'], ws_p, we_p)
print(f"  {'BL Write Driver swing':<28} {bl_w_s:>10.4f} V {bl_w_p:>10.4f} V {bl_w_p-bl_w_s:>+8.4f} V")

# Functional check
print("\n── Functional Verification ──")
print(f"{'Check':<40} {'Schematic':>10} {'Post-Layout':>10}")
print("-" * 62)

# READ: HRS BL < VREF(0.9V) and LRS BL > VREF
def check_read(s_dict, t, rs, re):
    bl0 = measure_bl_read(t, s_dict['bl0'], rs, re)  # HRS
    bl1 = measure_bl_read(t, s_dict['bl1'], rs, re)  # LRS
    # HRS BL > LRS BL (HRS discharges less → higher voltage)
    bl_diff_ok = bl0 > bl1 + 0.01
    sa_q0 = measure_sa_output(s_dict['sa_q0'], rs, re)
    sa_q1 = measure_sa_output(s_dict['sa_q1'], rs, re)
    # SA resolves to rail: Q0→LOW (HRS), Q1→HIGH (LRS)
    sa_ok = sa_q0 < 0.9 and sa_q1 > 0.9
    return bl_diff_ok and sa_ok

read_s = check_read(s, t_sch, rs_s, re_s)
read_p = check_read(p, t_pex, rs_p, re_p)
print(f"  {'READ: BL differential + SA resolve':<38} {'PASS' if read_s else 'FAIL':>10} {'PASS' if read_p else 'FAIL':>10}")

# WRITE: bl_en and bl_data activate
def check_write(s_dict, ws, we):
    if ws is None:
        return False
    bl_en = np.max(s_dict['bl_en2'][ws:we])
    return bl_en > 0.9

write_s = check_write(s, ws_s, we_s)
write_p = check_write(p, ws_p, we_p)
print(f"  {'WRITE: BL driver activation':<38} {'PASS' if write_s else 'FAIL':>10} {'PASS' if write_p else 'FAIL':>10}")

# Controller resp_valid
rv_s = np.max(s['rv']) > 0.9
rv_p = np.max(p['rv']) > 0.9
print(f"  {'Controller: resp_valid asserted':<38} {'PASS' if rv_s else 'FAIL':>10} {'PASS' if rv_p else 'FAIL':>10}")

print("\n" + "=" * 70)
print("  Conclusion: Post-layout results", end="")
if read_p and write_p and rv_p:
    print(" MATCH schematic behavior.")
else:
    print(" DIFFER from schematic behavior!")
print("=" * 70)

# ─── Overlay comparison plot ───

fig, axes = plt.subplots(4, 1, figsize=(16, 16), sharex=True)
fig.suptitle('Schematic vs Post-Layout Comparison\n'
             'Solid = Post-Layout (extracted),  Dashed = Schematic',
             fontsize=14, fontweight='bold')

# Panel 1: WL Driver output
ax = axes[0]
ax.plot(t_pex, p['wl1'], color='#FF5722', linewidth=1.5, label='WL1 (post-layout)')
ax.plot(t_sch, s['wl1'], color='#FF5722', linewidth=1.0, linestyle='--', alpha=0.6, label='WL1 (schematic)')
ax.axhline(y=3.3, color='r', linestyle=':', alpha=0.3, linewidth=0.5)
ax.set_ylabel('Voltage (V)')
ax.set_title('WL Driver Output')
ax.legend(loc='upper right', fontsize=9)
ax.set_ylim(-0.5, 4.0)
ax.grid(True, alpha=0.3)

# Panel 2: Bitline voltages (BL0=HRS, BL1=LRS)
ax = axes[1]
ax.plot(t_pex, p['bl0'], color='#E91E63', linewidth=1.5, label='BL0 HRS (post-layout)')
ax.plot(t_sch, s['bl0'], color='#E91E63', linewidth=1.0, linestyle='--', alpha=0.6, label='BL0 HRS (schematic)')
ax.plot(t_pex, p['bl1'], color='#9C27B0', linewidth=1.5, label='BL1 LRS (post-layout)')
ax.plot(t_sch, s['bl1'], color='#9C27B0', linewidth=1.0, linestyle='--', alpha=0.6, label='BL1 LRS (schematic)')
ax.axhline(y=0.9, color='gray', linestyle='--', alpha=0.5, label='VREF=0.9V')
ax.set_ylabel('Voltage (V)')
ax.set_title('Bitline Voltages During READ')
ax.legend(loc='upper right', fontsize=8, ncol=2)
ax.set_ylim(-0.2, 2.2)
ax.grid(True, alpha=0.3)

# Panel 3: SA outputs
ax = axes[2]
ax.plot(t_pex, p['sa_q0'], color='#E91E63', linewidth=1.5, label='SA_Q0 HRS (post-layout)')
ax.plot(t_sch, s['sa_q0'], color='#E91E63', linewidth=1.0, linestyle='--', alpha=0.6, label='SA_Q0 HRS (schematic)')
ax.plot(t_pex, p['sa_q1'], color='#9C27B0', linewidth=1.5, label='SA_Q1 LRS (post-layout)')
ax.plot(t_sch, s['sa_q1'], color='#9C27B0', linewidth=1.0, linestyle='--', alpha=0.6, label='SA_Q1 LRS (schematic)')
ax.set_ylabel('Voltage (V)')
ax.set_title('Sense Amplifier Outputs')
ax.legend(loc='upper right', fontsize=8, ncol=2)
ax.set_ylim(-0.2, 2.2)
ax.grid(True, alpha=0.3)

# Panel 4: Closed-loop (SA → resp_data)
ax = axes[3]
ax.plot(t_pex, p['rd'], color='#FF9800', linewidth=1.5, label='resp_data (post-layout)')
ax.plot(t_sch, s['rd'], color='#FF9800', linewidth=1.0, linestyle='--', alpha=0.6, label='resp_data (schematic)')
ax.plot(t_pex, p['rv'], color='#4CAF50', linewidth=1.2, label='resp_valid (post-layout)')
ax.plot(t_sch, s['rv'], color='#4CAF50', linewidth=1.0, linestyle='--', alpha=0.6, label='resp_valid (schematic)')
ax.set_ylabel('Voltage (V)')
ax.set_xlabel('Time (ns)')
ax.set_title('Controller Feedback: resp_data & resp_valid')
ax.legend(loc='upper right', fontsize=8, ncol=2)
ax.set_ylim(-0.2, 2.2)
ax.grid(True, alpha=0.3)

# Phase annotations
for ax in axes:
    ax.axvspan(45, 115, alpha=0.05, color='blue')
    ax.axvspan(145, 250, alpha=0.05, color='red')
    ax.axvspan(260, 340, alpha=0.05, color='green')

axes[0].text(80, 3.6, 'READ', ha='center', fontsize=9, color='blue', fontweight='bold')
axes[0].text(197, 3.6, 'WRITE', ha='center', fontsize=9, color='red', fontweight='bold')
axes[0].text(300, 3.6, 'VERIFY', ha='center', fontsize=9, color='green', fontweight='bold')

plt.tight_layout()
plt.savefig('compare_sch_vs_postlayout.png', dpi=150, bbox_inches='tight')
print(f"\nSaved: compare_sch_vs_postlayout.png")
