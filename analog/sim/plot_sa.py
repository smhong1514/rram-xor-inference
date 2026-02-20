import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Read ngspice wrdata output (space-separated, two header lines)
data = np.loadtxt(os.path.expandvars('$PROJECT_ROOT/analog/sim/sa_result.csv'))
print(f"Data shape: {data.shape}")

# ngspice wrdata format: time, sae, time, q, time, qb, time, inp, time, inn (10 columns)
t = data[:, 0] * 1e9  # to ns
sae = data[:, 1]
q = data[:, 3]
qb = data[:, 5]
inp = data[:, 7]
inn = data[:, 9]

print(f"t range: {t[0]:.2f} - {t[-1]:.2f} ns")
print(f"SAE: {sae[0]:.2f} -> {sae[-1]:.2f}")
print(f"Q: {q[0]:.4f} -> {q[-1]:.6f}")
print(f"QB: {qb[0]:.4f} -> {qb[-1]:.4f}")

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8), sharex=True,
                                      gridspec_kw={'height_ratios': [1, 1.5, 1]})
fig.suptitle('StrongARM Latch-type Sense Amplifier\nInput: INP=0.925V, INN=0.875V (ΔV=50mV)',
             fontsize=14, fontweight='bold')

# SAE clock
ax1.plot(t, sae, 'g-', linewidth=2, label='SAE')
ax1.set_ylabel('SAE (V)', fontsize=11)
ax1.set_ylim(-0.1, 2.0)
ax1.legend(loc='upper right', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.axhline(y=0.9, color='gray', linestyle='--', alpha=0.3)

# Q and QB outputs
ax2.plot(t, q, 'b-', linewidth=2, label='Q')
ax2.plot(t, qb, 'r-', linewidth=2, label='QB')
ax2.set_ylabel('Output (V)', fontsize=11)
ax2.set_ylim(-0.1, 2.0)
ax2.legend(loc='center right', fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0.9, color='gray', linestyle='--', alpha=0.3)

# Add annotations for precharge and evaluate phases
for cycle_start in [0, 40, 80]:
    if cycle_start + 10 < t[-1]:
        ax2.axvspan(cycle_start, cycle_start + 10, alpha=0.08, color='yellow')
        ax2.text(cycle_start + 3, 0.1, 'Pre', fontsize=8, color='orange', ha='center')
    if cycle_start + 10 < t[-1] and cycle_start + 30 < t[-1]:
        ax2.axvspan(cycle_start + 10, cycle_start + 30, alpha=0.08, color='cyan')
        ax2.text(cycle_start + 20, 0.1, 'Eval', fontsize=8, color='blue', ha='center')

# Input voltages
ax3.plot(t, inp, 'm-', linewidth=2, label='INP (0.925V)')
ax3.plot(t, inn, 'c-', linewidth=2, label='INN (0.875V)')
ax3.set_ylabel('Input (V)', fontsize=11)
ax3.set_xlabel('Time (ns)', fontsize=11)
ax3.set_ylim(0.8, 1.0)
ax3.legend(loc='upper right', fontsize=10)
ax3.grid(True, alpha=0.3)

# Add delta annotation
ax3.annotate('ΔV = 50mV', xy=(50, 0.9), fontsize=11, color='red',
            ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.expandvars('$PROJECT_ROOT/analog/sim/sense_amp_sim.png'), dpi=150, bbox_inches='tight')
print("Plot saved to sense_amp_sim.png")

# Print summary
print("\n=== Simulation Summary ===")
# Find evaluate phase (first SAE rise)
sae_rise_idx = np.argmax(sae > 0.9)
if sae_rise_idx > 0:
    t_rise = t[sae_rise_idx]
    print(f"SAE rises at: {t_rise:.2f} ns")

    # Find when Q falls below 0.9V
    eval_mask = t > t_rise
    q_eval = q[eval_mask]
    t_eval = t[eval_mask]
    q_fall_idx = np.argmax(q_eval < 0.9)
    if q_fall_idx > 0:
        t_resolve = t_eval[q_fall_idx] - t_rise
        print(f"Q resolves at: {t_eval[q_fall_idx]:.2f} ns")
        print(f"Resolution time: {t_resolve*1000:.1f} ps")

    # Final values at end of first evaluate
    t_end_eval = t_rise + 15  # 15ns into evaluate
    end_idx = np.argmin(np.abs(t - t_end_eval))
    print(f"Q final: {q[end_idx]:.4f} V")
    print(f"QB final: {qb[end_idx]:.4f} V")
    print(f"Output swing: {abs(qb[end_idx] - q[end_idx]):.4f} V")
