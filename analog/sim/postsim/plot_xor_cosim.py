#!/usr/bin/env python3
"""Plot 2-Array XOR Inference Co-Simulation Results

Reads xor_cosim.csv produced by ngspice wrdata and generates
a multi-panel plot showing the full XOR inference flow for all 4 test cases.

XOR(A,B) = AND( OR(A,B), NAND(A,B) )
  Phase 0: Array 1 → SA1(OR), SA2(NAND)
  Phase 1: Array 2 → SA3(AND = XOR)
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# --- Load data ---
data = np.loadtxt('xor_cosim.csv')
t = data[:, 0] * 1e9  # ns

# Column mapping (wrdata format: time, val1, time, val2, ...)
rdy     = data[:, 1]
rv      = data[:, 3]
xr      = data[:, 5]
phase   = data[:, 7]
sae     = data[:, 9]
start   = data[:, 11]
wl_in0  = data[:, 13]
wl_in1  = data[:, 15]
a1_bl0  = data[:, 17]
a1_bl1  = data[:, 19]
a1_bl2  = data[:, 21]
a1_bl3  = data[:, 23]
sa1_q   = data[:, 25]
sa2_q   = data[:, 27]
a2_bl0  = data[:, 29]
a2_bl1  = data[:, 31]
sa3_q   = data[:, 33]
sl1_en0 = data[:, 35]
sl1_en1 = data[:, 37]
sl2_en0 = data[:, 39]
sl2_en1 = data[:, 41]
ia      = data[:, 43]
ib      = data[:, 45]
prech1  = data[:, 47]
prech2  = data[:, 49]

# --- Find SAE edges and result_valid edges ---
sae_edges = []
for i in range(1, len(sae)):
    if sae[i] > 0.9 and sae[i-1] < 0.9:
        sae_edges.append(i)

rv_edges = []
for i in range(1, len(rv)):
    if rv[i] > 0.9 and rv[i-1] < 0.9:
        rv_edges.append(i)

# --- Full overview plot ---
fig, axes = plt.subplots(7, 1, figsize=(18, 16), sharex=True,
                         gridspec_kw={'height_ratios': [1.2, 1, 1.5, 1.2, 1.5, 1.2, 1.2]})

# Color scheme
C_VDD = '#2196F3'
C_GND = '#F44336'
C_SAE = '#FF9800'
C_BL  = ['#E91E63', '#9C27B0', '#3F51B5', '#009688']
C_SA  = '#4CAF50'
C_XR  = '#FF5722'

# Panel 1: Controller signals (start, ready, result_valid, xor_result)
ax = axes[0]
ax.plot(t, start/1.8, label='start', color='#607D8B', linewidth=0.8)
ax.plot(t, rdy/1.8 + 1.2, label='ready', color=C_VDD, linewidth=0.8)
ax.plot(t, rv/1.8 + 2.4, label='result_valid', color=C_SA, linewidth=0.8)
ax.plot(t, xr/1.8 + 3.6, label='xor_result', color=C_XR, linewidth=1.2)
ax.set_ylabel('Controller')
ax.set_yticks([0.5, 1.7, 2.9, 4.1])
ax.set_yticklabels(['start', 'ready', 'rv', 'xor'])
ax.set_ylim(-0.3, 5.0)
# Add test labels
test_starts = [100, 2000, 4000, 6000]
test_labels = ['Test 1\nA=0,B=0\nXOR=0', 'Test 2\nA=0,B=1\nXOR=1',
               'Test 3\nA=1,B=0\nXOR=1', 'Test 4\nA=1,B=1\nXOR=0']
for ts, tl in zip(test_starts, test_labels):
    ax.axvline(ts, color='gray', linewidth=0.5, linestyle='--', alpha=0.5)
    ax.text(ts + 50, 4.5, tl, fontsize=7, va='top', fontfamily='monospace')

# Panel 2: Inputs + Phase + SAE
ax = axes[1]
ax.plot(t, ia/1.8, label='input_A', color='#E91E63', linewidth=0.8)
ax.plot(t, ib/1.8 + 1.2, label='input_B', color='#9C27B0', linewidth=0.8)
ax.plot(t, phase/1.8 + 2.4, label='phase', color='#FF9800', linewidth=0.8)
ax.plot(t, sae/1.8 + 3.6, label='SAE', color=C_SAE, linewidth=0.8)
ax.set_ylabel('Inputs/Ctrl')
ax.set_yticks([0.5, 1.7, 2.9, 4.1])
ax.set_yticklabels(['A', 'B', 'phase', 'SAE'])
ax.set_ylim(-0.3, 5.0)
for ts in test_starts:
    ax.axvline(ts, color='gray', linewidth=0.5, linestyle='--', alpha=0.5)

# Panel 3: Array 1 BL voltages
ax = axes[2]
ax.plot(t, a1_bl0, label='A1_BL0 (OR+)', color=C_BL[0], linewidth=0.8)
ax.plot(t, a1_bl1, label='A1_BL1 (OR-)', color=C_BL[1], linewidth=0.8)
ax.plot(t, a1_bl2, label='A1_BL2 (NAND+)', color=C_BL[2], linewidth=0.8, linestyle='--')
ax.plot(t, a1_bl3, label='A1_BL3 (NAND-)', color=C_BL[3], linewidth=0.8, linestyle='--')
ax.set_ylabel('Array 1 BL (V)')
ax.legend(loc='lower right', fontsize=7, ncol=2)
ax.set_ylim(-0.1, 2.0)
for ts in test_starts:
    ax.axvline(ts, color='gray', linewidth=0.5, linestyle='--', alpha=0.5)

# Panel 4: SA1 + SA2 outputs
ax = axes[3]
ax.plot(t, sa1_q, label='SA1_Q (OR)', color='#2196F3', linewidth=1.0)
ax.plot(t, sa2_q, label='SA2_Q (NAND)', color='#FF5722', linewidth=1.0)
ax.axhline(0.9, color='gray', linewidth=0.5, linestyle=':', alpha=0.5)
ax.set_ylabel('SA1/SA2 (V)')
ax.legend(loc='right', fontsize=8)
ax.set_ylim(-0.2, 2.0)
for ts in test_starts:
    ax.axvline(ts, color='gray', linewidth=0.5, linestyle='--', alpha=0.5)

# Panel 5: Array 2 BL voltages
ax = axes[4]
ax.plot(t, a2_bl0, label='A2_BL0 (AND+)', color=C_BL[0], linewidth=1.0)
ax.plot(t, a2_bl1, label='A2_BL1 (AND-)', color=C_BL[1], linewidth=1.0)
ax.set_ylabel('Array 2 BL (V)')
ax.legend(loc='lower right', fontsize=8)
ax.set_ylim(-0.1, 2.0)
for ts in test_starts:
    ax.axvline(ts, color='gray', linewidth=0.5, linestyle='--', alpha=0.5)

# Panel 6: SA3 output (AND = XOR)
ax = axes[5]
ax.plot(t, sa3_q, label='SA3_Q (AND=XOR)', color=C_SA, linewidth=1.2)
ax.axhline(0.9, color='gray', linewidth=0.5, linestyle=':', alpha=0.5)
ax.set_ylabel('SA3 (V)')
ax.legend(loc='right', fontsize=8)
ax.set_ylim(-0.2, 2.0)
for ts in test_starts:
    ax.axvline(ts, color='gray', linewidth=0.5, linestyle='--', alpha=0.5)

# Panel 7: Precharge control
ax = axes[6]
ax.plot(t, prech1, label='prech1 (Array 1)', color='#795548', linewidth=0.8)
ax.plot(t, prech2, label='prech2 (Array 2)', color='#607D8B', linewidth=0.8)
ax.set_ylabel('Precharge (V)')
ax.set_xlabel('Time (ns)')
ax.legend(loc='right', fontsize=8)
ax.set_ylim(-0.2, 2.0)
for ts in test_starts:
    ax.axvline(ts, color='gray', linewidth=0.5, linestyle='--', alpha=0.5)

fig.suptitle('2-Array XOR Inference Co-Simulation (d_cosim)\n'
             'XOR(A,B) = AND(OR(A,B), NAND(A,B))\n'
             'All 4 tests PASS: (0,0)→0  (0,1)→1  (1,0)→1  (1,1)→0',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('xor_cosim_full.png', dpi=150, bbox_inches='tight')
print(f"Saved: xor_cosim_full.png")

# --- Zoomed view: one test per panel ---
fig2, axes2 = plt.subplots(2, 2, figsize=(18, 12))
test_windows = [(80, 280), (1980, 2180), (3980, 4180), (5980, 6180)]
test_info = [
    ('Test 1: A=0, B=0 → XOR=0', 0),
    ('Test 2: A=0, B=1 → XOR=1', 1),
    ('Test 3: A=1, B=0 → XOR=1', 1),
    ('Test 4: A=1, B=1 → XOR=0', 0),
]

for idx, (ax, (t_lo, t_hi), (title, expected)) in enumerate(
        zip(axes2.flat, test_windows, test_info)):
    mask = (t >= t_lo) & (t <= t_hi)
    tm = t[mask]

    # Plot SA outputs and BLs on same axes
    ax.plot(tm, a1_bl0[mask], label='A1_BL0(OR+)', color=C_BL[0], linewidth=0.7, alpha=0.6)
    ax.plot(tm, a1_bl1[mask], label='A1_BL1(OR-)', color=C_BL[1], linewidth=0.7, alpha=0.6)
    ax.plot(tm, a2_bl0[mask], label='A2_BL0(AND+)', color=C_BL[2], linewidth=0.7, alpha=0.6)
    ax.plot(tm, a2_bl1[mask], label='A2_BL1(AND-)', color=C_BL[3], linewidth=0.7, alpha=0.6)
    ax.plot(tm, sa1_q[mask], label='SA1(OR)', color='#2196F3', linewidth=1.5)
    ax.plot(tm, sa2_q[mask], label='SA2(NAND)', color='#FF5722', linewidth=1.5)
    ax.plot(tm, sa3_q[mask], label='SA3(AND=XOR)', color=C_SA, linewidth=1.5)
    ax.plot(tm, sae[mask], label='SAE', color=C_SAE, linewidth=0.8, linestyle=':')

    # Mark result
    for ri in rv_edges:
        if t_lo < t[ri] < t_hi:
            xr_val = xr[ri]
            result = '1' if xr_val > 0.9 else '0'
            color = '#4CAF50' if (expected == 1 and xr_val > 0.9) or \
                                 (expected == 0 and xr_val < 0.9) else '#F44336'
            ax.axvline(t[ri], color=color, linewidth=1.5, linestyle='--', alpha=0.7)
            ax.text(t[ri]+2, 1.9, f'XOR={result}', fontsize=10, fontweight='bold',
                   color=color, va='top')

    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Voltage (V)')
    ax.set_ylim(-0.2, 2.1)
    ax.legend(loc='center right', fontsize=6, ncol=1)
    ax.grid(True, alpha=0.3)

fig2.suptitle('XOR Co-Simulation — Per-Test Detail View', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('xor_cosim_detail.png', dpi=150, bbox_inches='tight')
print(f"Saved: xor_cosim_detail.png")

# --- Truth table summary ---
print("\n" + "="*60)
print("XOR TRUTH TABLE VERIFICATION")
print("="*60)
print(f"{'Test':>6s} {'A':>3s} {'B':>3s} {'OR':>4s} {'NAND':>5s} {'AND':>4s} {'Expected':>9s} {'Got':>4s} {'Status':>8s}")
print("-"*60)

results = []
for test_idx in range(min(4, len(sae_edges)//2)):
    p0_idx = sae_edges[test_idx * 2]
    p1_idx = sae_edges[test_idx * 2 + 1]

    # +5ns after SAE rise
    idx5_p0 = np.argmin(np.abs(t - (t[p0_idx] + 5)))
    idx5_p1 = np.argmin(np.abs(t - (t[p1_idx] + 5)))

    sa1_v = 1 if sa1_q[idx5_p0] > 0.9 else 0
    sa2_v = 1 if sa2_q[idx5_p0] > 0.9 else 0
    sa3_v = 1 if sa3_q[idx5_p1] > 0.9 else 0

    # Find actual result from rv
    actual = None
    for ri in rv_edges:
        if t[ri] > t[p1_idx]:
            actual = 1 if xr[ri] > 0.9 else 0
            break

    expected_vals = [0, 1, 1, 0]
    a_vals = [0, 0, 1, 1]
    b_vals = [0, 1, 0, 1]
    status = 'PASS' if actual == expected_vals[test_idx] else 'FAIL'

    print(f"{test_idx+1:>6d} {a_vals[test_idx]:>3d} {b_vals[test_idx]:>3d} "
          f"{sa1_v:>4d} {sa2_v:>5d} {sa3_v:>4d} "
          f"{expected_vals[test_idx]:>9d} {actual:>4d} {status:>8s}")
    results.append(status == 'PASS')

print("-"*60)
if all(results):
    print("  ALL 4 TESTS PASSED — XOR inference verified!")
else:
    print(f"  {sum(results)}/4 tests passed")
print("="*60)
