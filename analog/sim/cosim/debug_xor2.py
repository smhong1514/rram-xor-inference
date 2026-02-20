#!/usr/bin/env python3
"""Debug XOR co-sim: check BL voltages at SAE time, SA resolution"""
import numpy as np

data = np.loadtxt('xor_cosim.csv')
t = data[:, 0] * 1e9  # ns

rdy = data[:, 1]
rv = data[:, 3]
xr = data[:, 5]
phase = data[:, 7]
sae = data[:, 9]
start = data[:, 11]
a1_bl0 = data[:, 17]
a1_bl1 = data[:, 19]
a1_bl2 = data[:, 21]
a1_bl3 = data[:, 23]
sa1_q = data[:, 25]
sa2_q = data[:, 27]
a2_bl0 = data[:, 29]
a2_bl1 = data[:, 31]
sa3_q = data[:, 33]

# Find SAE rising edges
sae_edges = []
for i in range(1, len(sae)):
    if sae[i] > 0.9 and sae[i-1] < 0.9:
        sae_edges.append(i)

print("=== SAE Rising Edges ===")
for idx in sae_edges[:8]:
    t_sae = t[idx]
    # Check BL voltages at SAE time and during SAE
    print(f"\nt={t_sae:.1f}ns (SAE rise):")
    print(f"  phase={phase[idx]:.1f}")

    # Look at BL during SAE window (next ~15ns at 200MHz)
    for dt in [0, 2, 5, 10, 15]:
        idx2 = np.argmin(np.abs(t - (t_sae + dt)))
        print(f"  t={t[idx2]:.1f}ns (+{dt}ns): "
              f"A1_BL0={a1_bl0[idx2]:.4f} BL1={a1_bl1[idx2]:.4f} BL2={a1_bl2[idx2]:.4f} BL3={a1_bl3[idx2]:.4f} | "
              f"A2_BL0={a2_bl0[idx2]:.4f} BL1={a2_bl1[idx2]:.4f} | "
              f"SA1Q={sa1_q[idx2]:.3f} SA2Q={sa2_q[idx2]:.3f} SA3Q={sa3_q[idx2]:.3f} SAE={sae[idx2]:.1f}")

# Find SA transitions during SAE
print("\n=== SA Output During SAE Pulses ===")
for edge_idx, sae_idx in enumerate(sae_edges[:8]):
    t_sae = t[sae_idx]
    # Find SA min/max during SAE pulse (15ns window)
    mask = (t >= t_sae) & (t <= t_sae + 20)
    sa1_min = sa1_q[mask].min()
    sa1_max = sa1_q[mask].max()
    sa2_min = sa2_q[mask].min()
    sa2_max = sa2_q[mask].max()
    sa3_min = sa3_q[mask].min()
    sa3_max = sa3_q[mask].max()
    print(f"SAE #{edge_idx+1} at t={t_sae:.1f}ns: "
          f"SA1=[{sa1_min:.3f}, {sa1_max:.3f}] "
          f"SA2=[{sa2_min:.3f}, {sa2_max:.3f}] "
          f"SA3=[{sa3_min:.3f}, {sa3_max:.3f}]")

# Check rv timing
rv_edges = []
for i in range(1, len(rv)):
    if rv[i] > 0.9 and rv[i-1] < 0.9:
        rv_edges.append(i)

print(f"\n=== result_valid edges ===")
for i, idx in enumerate(rv_edges[:4]):
    print(f"Test {i+1}: rv rises at t={t[idx]:.1f}ns, xr={xr[idx]:.3f}")
