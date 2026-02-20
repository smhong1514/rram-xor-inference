#!/usr/bin/env python3
"""Debug XOR Test 4 failure: NAND(1,1) should be 0"""
import numpy as np

data = np.loadtxt('xor_cosim.csv')
t = data[:, 0] * 1e9

rdy = data[:, 1]
rv = data[:, 3]
xr = data[:, 5]
phase = data[:, 7]
sae = data[:, 9]
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

# Focus on Test 4 (SAE #7 and #8, around t=6000ns)
print("=== All SAE edges ===")
for i, idx in enumerate(sae_edges):
    t_sae = t[idx]
    ph = phase[idx]
    print(f"SAE #{i+1}: t={t_sae:.1f}ns, phase={ph:.1f}")

# For each pair of SAE pulses, show BL and SA data
test_names = ["Test 1 (0,0)", "Test 2 (0,1)", "Test 3 (1,0)", "Test 4 (1,1)"]
for test_idx in range(min(4, len(sae_edges)//2)):
    p0_idx = sae_edges[test_idx * 2]      # Phase 0 SAE
    p1_idx = sae_edges[test_idx * 2 + 1]  # Phase 1 SAE

    print(f"\n{'='*60}")
    print(f"{test_names[test_idx]}")
    print(f"{'='*60}")

    # Phase 0 analysis
    t0 = t[p0_idx]
    # Find SA values 5ns after SAE rise (should be resolved)
    idx5 = np.argmin(np.abs(t - (t0 + 5)))
    print(f"\nPhase 0 SAE at t={t0:.1f}ns (+5ns):")
    print(f"  A1_BL0(OR+) ={a1_bl0[idx5]:.4f}  A1_BL1(OR-) ={a1_bl1[idx5]:.4f}  diff={a1_bl0[idx5]-a1_bl1[idx5]:.4f}")
    print(f"  A1_BL2(NAND+)={a1_bl2[idx5]:.4f}  A1_BL3(NAND-)={a1_bl3[idx5]:.4f}  diff={a1_bl2[idx5]-a1_bl3[idx5]:.4f}")
    print(f"  SA1_Q={sa1_q[idx5]:.3f} (OR)   SA2_Q={sa2_q[idx5]:.3f} (NAND)")

    # SA polarity: INP > INN → Q=LOW(0). So:
    # SA1: BL0 > BL1 → Q LOW → OR=0
    #      BL0 < BL1 → Q HIGH → OR=1
    sa1_val = 1 if sa1_q[idx5] > 0.9 else 0
    sa2_val = 1 if sa2_q[idx5] > 0.9 else 0
    print(f"  → OR={sa1_val}, NAND={sa2_val}")

    # Phase 1 analysis
    t1 = t[p1_idx]
    idx5p1 = np.argmin(np.abs(t - (t1 + 5)))
    print(f"\nPhase 1 SAE at t={t1:.1f}ns (+5ns):")
    print(f"  A2_BL0(AND+)={a2_bl0[idx5p1]:.4f}  A2_BL1(AND-)={a2_bl1[idx5p1]:.4f}  diff={a2_bl0[idx5p1]-a2_bl1[idx5p1]:.4f}")
    print(f"  SA3_Q={sa3_q[idx5p1]:.3f} (AND)")

    sa3_val = 1 if sa3_q[idx5p1] > 0.9 else 0
    print(f"  → AND={sa3_val} (= XOR result)")

    # Find rv time for this test
    rv_found = False
    for ri in range(1, len(rv)):
        if rv[ri] > 0.9 and rv[ri-1] < 0.9 and t[ri] > t1:
            print(f"\n  result_valid at t={t[ri]:.1f}ns, xr_a={xr[ri]:.3f}")
            rv_found = True
            break
    if not rv_found:
        print(f"\n  result_valid NOT found after Phase 1 SAE")
