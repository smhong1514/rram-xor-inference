#!/usr/bin/env python3
"""Quick debug: check XOR co-sim waveform data"""
import numpy as np

data = np.loadtxt('xor_cosim.csv')
t = data[:, 0] * 1e9  # ns

# wrdata format: time,val1,time,val2,...
# Signals (from wrdata order):
# 0:time 1:rdy_a 2:time 3:rv_a 4:time 5:xr_a 6:time 7:phase_a
# 8:time 9:sae_a 10:time 11:start_a
# 12:time 13:wl_in0 14:time 15:wl_in1
# 16:time 17:a1_bl0 18:time 19:a1_bl1 20:time 21:a1_bl2 22:time 23:a1_bl3
# 24:time 25:sa1_q_a 26:time 27:sa2_q_a
# 28:time 29:a2_bl0 30:time 31:a2_bl1
# 32:time 33:sa3_q_a
# 34:time 35:sl1_en0 36:time 37:sl1_en1 38:time 39:sl2_en0 40:time 41:sl2_en1
# 42:time 43:ia_a 44:time 45:ib_a

rdy = data[:, 1]
rv = data[:, 3]
xr = data[:, 5]
phase = data[:, 7]
sae = data[:, 9]
start = data[:, 11]
wl_in0 = data[:, 13]
wl_in1 = data[:, 15]
a1_bl0 = data[:, 17]
a1_bl1 = data[:, 19]
a1_bl2 = data[:, 21]
a1_bl3 = data[:, 23]
sa1_q = data[:, 25]
sa2_q = data[:, 27]
a2_bl0 = data[:, 29]
a2_bl1 = data[:, 31]
sa3_q = data[:, 33]
sl1_en0 = data[:, 35]
sl1_en1 = data[:, 37]
sl2_en0 = data[:, 39]
sl2_en1 = data[:, 41]
ia = data[:, 43]
ib = data[:, 45]

# Print key signals at various times
check_times = [50, 100, 120, 200, 300, 400, 500, 600, 700, 800, 1000, 1200, 1500, 1800]

print(f"{'Time':>8s} {'rdy':>6s} {'rv':>6s} {'xr':>6s} {'phase':>6s} {'sae':>6s} {'start':>6s} {'wl0':>6s} {'sl1_0':>6s} {'sl2_0':>6s} {'sa1q':>6s} {'sa2q':>6s} {'sa3q':>6s}")
print("-" * 100)
for ct in check_times:
    idx = np.argmin(np.abs(t - ct))
    print(f"{ct:>7.0f}ns {rdy[idx]:>6.3f} {rv[idx]:>6.3f} {xr[idx]:>6.3f} {phase[idx]:>6.3f} {sae[idx]:>6.3f} {start[idx]:>6.3f} {wl_in0[idx]:>6.3f} {sl1_en0[idx]:>6.3f} {sl2_en0[idx]:>6.3f} {sa1_q[idx]:>6.3f} {sa2_q[idx]:>6.3f} {sa3_q[idx]:>6.3f}")

# Check BL voltages around test 1 SAE time
print("\n--- BL voltages around expected sensing window (test 1) ---")
for ct in [200, 250, 300, 350, 400, 450, 500]:
    idx = np.argmin(np.abs(t - ct))
    print(f"t={ct}ns: A1_BL0={a1_bl0[idx]:.4f} A1_BL1={a1_bl1[idx]:.4f} A1_BL2={a1_bl2[idx]:.4f} A1_BL3={a1_bl3[idx]:.4f} | A2_BL0={a2_bl0[idx]:.4f} A2_BL1={a2_bl1[idx]:.4f}")

# Find when rv goes high (if ever)
rv_high = np.where(rv > 0.9)[0]
if len(rv_high) > 0:
    print(f"\nresult_valid first goes HIGH at t={t[rv_high[0]]:.1f}ns")
    for i in rv_high[:5]:
        print(f"  t={t[i]:.1f}ns: rv={rv[i]:.3f} xr={xr[i]:.3f}")
else:
    print("\nresult_valid NEVER goes HIGH!")

# Find when SAE fires
sae_high = np.where(sae > 0.9)[0]
if len(sae_high) > 0:
    # Find transitions
    sae_edges = []
    for i in range(1, len(sae)):
        if sae[i] > 0.9 and sae[i-1] < 0.9:
            sae_edges.append(t[i])
    print(f"\nSAE rising edges: {sae_edges[:8]}")
else:
    print("\nSAE NEVER fires!")

# Check phase transitions
phase_high = np.where(phase > 0.9)[0]
if len(phase_high) > 0:
    phase_edges = []
    for i in range(1, len(phase)):
        if phase[i] > 0.9 and phase[i-1] < 0.9:
            phase_edges.append(t[i])
    print(f"Phase 0→1 transitions: {phase_edges[:8]}")
else:
    print("\nPhase NEVER goes to 1!")
