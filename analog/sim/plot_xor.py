import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

data = np.loadtxt(os.path.expandvars('$PROJECT_ROOT/analog/sim/xor_result.csv'))
print(f"Data shape: {data.shape}")

# wrdata format: time, sae, time, q1, time, qb1, time, q2, time, qb2
t = data[:, 0] * 1e9  # to ns
sae = data[:, 1]
q1 = data[:, 3]
qb1 = data[:, 5]
q2 = data[:, 7]
qb2 = data[:, 9]

print(f"t range: {t[0]:.2f} - {t[-1]:.2f} ns")

fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True,
                          gridspec_kw={'height_ratios': [1, 1.5, 1.5]})
fig.suptitle('RRAM 4x4 XOR Inference: A=0, B=1 → XOR=1\n'
             'RRAM Array + WL Driver + Sense Amplifier (Resistor Model)',
             fontsize=13, fontweight='bold')

# SAE clock
axes[0].plot(t, sae, 'g-', linewidth=2, label='SAE')
axes[0].set_ylabel('SAE (V)', fontsize=11)
axes[0].set_ylim(-0.1, 2.0)
axes[0].legend(loc='upper right', fontsize=10)
axes[0].grid(True, alpha=0.3)

# SA1 outputs (BL0 vs BL1)
axes[1].plot(t, q1, 'b-', linewidth=2, label='Q1 (SA1)')
axes[1].plot(t, qb1, 'r-', linewidth=2, label='QB1 (SA1)')
axes[1].set_ylabel('SA1 Output (V)', fontsize=11)
axes[1].set_ylim(-0.1, 2.0)
axes[1].legend(loc='center right', fontsize=10)
axes[1].grid(True, alpha=0.3)
axes[1].axhline(y=0.9, color='gray', linestyle='--', alpha=0.3)

# Phase annotations
for cycle_start in [0, 40, 80]:
    if cycle_start + 10 < t[-1]:
        axes[1].axvspan(cycle_start, cycle_start + 10, alpha=0.08, color='yellow')
        axes[1].text(cycle_start + 5, 0.15, 'Pre', fontsize=8, color='orange', ha='center')
    if cycle_start + 10 < t[-1] and cycle_start + 30 < t[-1]:
        axes[1].axvspan(cycle_start + 10, cycle_start + 30, alpha=0.08, color='cyan')
        axes[1].text(cycle_start + 20, 0.15, 'Eval', fontsize=8, color='blue', ha='center')

# SA2 outputs (BL2 vs BL3)
axes[2].plot(t, q2, 'b--', linewidth=2, label='Q2 (SA2)')
axes[2].plot(t, qb2, 'r--', linewidth=2, label='QB2 (SA2)')
axes[2].set_ylabel('SA2 Output (V)', fontsize=11)
axes[2].set_xlabel('Time (ns)', fontsize=11)
axes[2].set_ylim(-0.1, 2.0)
axes[2].legend(loc='center right', fontsize=10)
axes[2].grid(True, alpha=0.3)
axes[2].axhline(y=0.9, color='gray', linestyle='--', alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.expandvars('$PROJECT_ROOT/analog/sim/xor_inference_sim.png'), dpi=150, bbox_inches='tight')
print("Plot saved to xor_inference_sim.png")

# Summary
print("\n=== XOR Inference Results (A=0, B=1) ===")
print(f"Expected XOR output: 1 (HIGH)")

# Find evaluation point
sae_rise_idx = np.argmax(sae > 0.9)
if sae_rise_idx > 0:
    t_rise = t[sae_rise_idx]
    print(f"\nSAE rises at: {t_rise:.2f} ns")

    # Values at 28ns
    idx_28 = np.argmin(np.abs(t - 28))
    print(f"\nAt t=28ns:")
    print(f"  Q1  = {q1[idx_28]:.4f} V  ({'HIGH' if q1[idx_28] > 0.9 else 'LOW'})")
    print(f"  QB1 = {qb1[idx_28]:.6f} V  ({'HIGH' if qb1[idx_28] > 0.9 else 'LOW'})")
    print(f"  Q2  = {q2[idx_28]:.4f} V  ({'HIGH' if q2[idx_28] > 0.9 else 'LOW'})")
    print(f"  QB2 = {qb2[idx_28]:.6f} V  ({'HIGH' if qb2[idx_28] > 0.9 else 'LOW'})")

    xor_out = q1[idx_28] > 0.9
    print(f"\nXOR(0,1) = {'1 (CORRECT)' if xor_out else '0 (WRONG)'}")
