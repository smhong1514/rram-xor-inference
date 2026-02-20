#!/usr/bin/env python3
"""Debug SA3 partial resolution in Test 1"""
import numpy as np

data = np.loadtxt('xor_cosim.csv')
t = data[:, 0] * 1e9
sa3_q = data[:, 33]
sae = data[:, 9]
a2_bl0 = data[:, 29]
a2_bl1 = data[:, 31]

# Phase 1 SAE for Test 1 (around t=203.8ns)
mask = (t >= 200) & (t <= 230)
print("=== SA3 during Test 1 Phase 1 (t=200-230ns) ===")
print(f"{'t(ns)':>8s} {'SAE':>6s} {'SA3_Q':>8s} {'BL0':>8s} {'BL1':>8s} {'diff':>8s}")
for i in np.where(mask)[0][::2]:  # every other point
    print(f"{t[i]:>8.2f} {sae[i]:>6.3f} {sa3_q[i]:>8.4f} {a2_bl0[i]:>8.4f} {a2_bl1[i]:>8.4f} {a2_bl0[i]-a2_bl1[i]:>8.4f}")

# Test 4 Phase 1 (around t=6103ns)
mask4 = (t >= 6100) & (t <= 6130)
if np.any(mask4):
    print("\n=== SA3 during Test 4 Phase 1 (t=6100-6130ns) ===")
    print(f"{'t(ns)':>8s} {'SAE':>6s} {'SA3_Q':>8s} {'BL0':>8s} {'BL1':>8s} {'diff':>8s}")
    for i in np.where(mask4)[0][::2]:
        print(f"{t[i]:>8.2f} {sae[i]:>6.3f} {sa3_q[i]:>8.4f} {a2_bl0[i]:>8.4f} {a2_bl1[i]:>8.4f} {a2_bl0[i]-a2_bl1[i]:>8.4f}")
