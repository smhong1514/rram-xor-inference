#!/usr/bin/env python3
"""
================================================================================
calc_weights.py — XOR Neural Network v2 Weight Matrix Calculator
================================================================================

Architecture:
  Layer 1: 3×5 array (3 inputs → 5 hidden neurons)
    Inputs:  x1, x2, x3=1 (bias)
    Outputs: h[0..4] (SA Q or QB)

  Layer 2: 5×2 array (5 hidden → 2 output neurons)
    Inputs:  h[0..4] (selected Q/QB from Layer 1 SAs)
    Outputs: z[0], z[1] (both = XOR result, redundant)

Key Design:
  - Binary weights only: HRS (0) or LRS (1)
  - Single VREF for all SAs (threshold between 1 and 2 LRS currents)
  - SA has both Q and QB outputs → can use QB for complement
  - Bias neuron (x3=1) shifts effective threshold per column

Physical mapping:
  - Array rows = SL lines (source lines, horizontal)
  - Array columns = BL lines (bit lines, vertical)
  - W[row][col] = RRAM cell at SL[row]-BL[col] intersection
  - LRS (Tfilament=4.5nm, ~34kΩ) = weight 1
  - HRS (Tfilament=3.5nm, ~286kΩ) = weight 0

================================================================================
"""

import numpy as np

# ─────────────────────────────────────────
# RRAM Physical Parameters
# ─────────────────────────────────────────
G_LRS = 1 / 34e3   # ~29.4 µS (Tfilament=4.5nm)
G_HRS = 1 / 286e3  # ~3.5 µS  (Tfilament=3.5nm)
V_READ = 1.8        # WL driver output (read voltage)

# ─────────────────────────────────────────
# Weight Matrices (binary: 0=HRS, 1=LRS)
# ─────────────────────────────────────────

# Layer 1: W1[3][5] — rows=SL(inputs), cols=BL(hidden)
# SL0=x1, SL1=x2, SL2=x3(bias=1)
# BL0→h0, BL1→h1, BL2→h2, BL3→h3, BL4→h4
W1 = np.array([
    #  BL0  BL1  BL2  BL3  BL4
    [  1,   1,   1,   0,   0  ],   # SL0 (x1)
    [  1,   1,   0,   1,   0  ],   # SL1 (x2)
    [  1,   0,   1,   1,   0  ],   # SL2 (bias=1)
])

# SA output selection: Q or QB
# Q:  fires when BL > VREF (sum >= threshold)
# QB: fires when BL < VREF (sum < threshold) = complement
SA1_USE_QB = [False, True, False, False, False]
# h0: Q  → OR(x1,x2)    [w={1,1,1}, sum=x1+x2+1, fires when ≥2]
# h1: QB → NAND(x1,x2)  [w={1,1,0}, sum=x1+x2, QB fires when <2 = NOT AND]
# h2: Q  → x1            [w={1,0,1}, sum=x1+1, fires when ≥2 = x1]
# h3: Q  → x2            [w={0,1,1}, sum=x2+1, fires when ≥2 = x2]
# h4: Q  → 0 (never)     [w={0,0,0}, sum=0, never fires]

# Layer 2: W2[5][2] — rows=SL(hidden), cols=BL(output)
# SL0=h0(OR), SL1=h1(NAND), SL2=h2(x1), SL3=h3(x2), SL4=h4(0)
# BL0→z1, BL1→z2 (same weights → z1=z2)
W2 = np.array([
    #  BL0  BL1
    [  1,   1  ],   # SL0 (h0 = OR)
    [  1,   1  ],   # SL1 (h1 = NAND)
    [  0,   0  ],   # SL2 (h2 = x1, unused in output)
    [  0,   0  ],   # SL3 (h3 = x2, unused in output)
    [  0,   0  ],   # SL4 (h4 = 0, unused)
])

SA2_USE_QB = [False, False]  # Both output SAs use Q


# ─────────────────────────────────────────
# Threshold Model
# ─────────────────────────────────────────
# VREF is set between 1 LRS current and 2 LRS current
# Effective threshold: sum >= 2 (at least 2 LRS cells active on that BL)
THRESHOLD = 2  # minimum number of LRS cells for SA to fire


def compute_layer(inputs, weights, use_qb, threshold):
    """Compute one layer of the neural network.

    Args:
        inputs: input vector (0/1)
        weights: weight matrix [rows × cols]
        use_qb: list of bool, True = use QB (complement) for that output
        threshold: minimum weighted sum for SA to fire (Q=1)

    Returns:
        output vector after step activation
    """
    # Weighted sum: each column gets sum of (input_i * weight_ij)
    sums = inputs @ weights  # matrix multiply

    outputs = []
    for j in range(weights.shape[1]):
        q = 1 if sums[j] >= threshold else 0
        qb = 1 - q
        if use_qb[j]:
            outputs.append(qb)
        else:
            outputs.append(q)

    return np.array(outputs), sums


# ─────────────────────────────────────────
# XOR Truth Table Verification
# ─────────────────────────────────────────
print("=" * 70)
print("XOR Neural Network v2 — Weight Matrix Verification")
print("=" * 70)

print("\n[Layer 1 Weight Matrix W1 (3×5)]")
print("       BL0(h0)  BL1(h1)  BL2(h2)  BL3(h3)  BL4(h4)")
row_labels = ["SL0(x1)", "SL1(x2)", "SL2(bias)"]
for i, label in enumerate(row_labels):
    vals = "    ".join(["LRS" if w == 1 else "HRS" for w in W1[i]])
    print(f"  {label:10s}  {vals}")

print(f"\n  SA polarity: ", end="")
for j in range(5):
    print(f"h{j}={'QB' if SA1_USE_QB[j] else 'Q'}  ", end="")
print()

print(f"\n  Functions (threshold={THRESHOLD}):")
print(f"    h0 (Q):  w=[1,1,1] → x1+x2+1 >= 2 → OR(x1,x2)")
print(f"    h1 (QB): w=[1,1,0] → NOT(x1+x2 >= 2) → NAND(x1,x2)")
print(f"    h2 (Q):  w=[1,0,1] → x1+1 >= 2 → x1")
print(f"    h3 (Q):  w=[0,1,1] → x2+1 >= 2 → x2")
print(f"    h4 (Q):  w=[0,0,0] → 0 >= 2 → always 0")

print("\n[Layer 2 Weight Matrix W2 (5×2)]")
print("       BL0(z1)  BL1(z2)")
row_labels2 = ["SL0(h0=OR)", "SL1(h1=NAND)", "SL2(h2=x1)", "SL3(h3=x2)", "SL4(h4=0)"]
for i, label in enumerate(row_labels2):
    vals = "    ".join(["LRS" if w == 1 else "HRS" for w in W2[i]])
    print(f"  {label:14s}  {vals}")

print(f"\n  z = AND(OR, NAND) = XOR  (threshold={THRESHOLD})")
print(f"  z1 = z2 (same weights, redundant output)")

# ─────────────────────────────────────────
# Run all 4 XOR test cases
# ─────────────────────────────────────────
print("\n" + "=" * 70)
print("XOR Truth Table Test")
print("=" * 70)

test_cases = [
    (0, 0, 0),
    (0, 1, 1),
    (1, 0, 1),
    (1, 1, 0),
]

all_pass = True
print(f"\n  {'x1':>3s} {'x2':>3s} | {'x3':>3s} | ", end="")
print(f"{'h0(OR)':>7s} {'h1(NAND)':>9s} {'h2(x1)':>7s} {'h3(x2)':>7s} {'h4':>4s} | ", end="")
print(f"{'z1':>3s} {'z2':>3s} | {'exp':>3s} | {'result':>6s}")
print("  " + "-" * 80)

for x1, x2, expected in test_cases:
    # Layer 1 input (with bias x3=1)
    inp1 = np.array([x1, x2, 1])

    # Layer 1 computation
    h, sums1 = compute_layer(inp1, W1, SA1_USE_QB, THRESHOLD)

    # Layer 2 computation
    z, sums2 = compute_layer(h, W2, SA2_USE_QB, THRESHOLD)

    z1, z2 = z[0], z[1]
    passed = (z1 == expected) and (z2 == expected)
    all_pass = all_pass and passed
    status = "PASS" if passed else "FAIL"

    print(f"  {x1:3d} {x2:3d} | {1:3d} | ", end="")
    print(f"{h[0]:7d} {h[1]:9d} {h[2]:7d} {h[3]:7d} {h[4]:4d} | ", end="")
    print(f"{z1:3d} {z2:3d} | {expected:3d} | {status:>6s}")

print("  " + "-" * 80)
print(f"\n  Overall: {'4/4 PASS' if all_pass else 'FAIL'}")

# ─────────────────────────────────────────
# Physical BL Current Analysis
# ─────────────────────────────────────────
print("\n" + "=" * 70)
print("Physical BL Current Analysis")
print("=" * 70)

print(f"\n  G_LRS = {G_LRS*1e6:.1f} µS  (R_LRS = {1/G_LRS/1e3:.0f} kΩ)")
print(f"  G_HRS = {G_HRS*1e6:.1f} µS  (R_HRS = {1/G_HRS/1e3:.0f} kΩ)")
print(f"  G_LRS/G_HRS ratio = {G_LRS/G_HRS:.1f}x")

print(f"\n  BL current when N LRS cells active (V_READ={V_READ}V):")
for n_lrs in range(4):  # 0 to 3 rows
    n_hrs = 3 - n_lrs  # remaining HRS cells (3 rows total in Array1)
    i_total = V_READ * (n_lrs * G_LRS + n_hrs * G_HRS)
    print(f"    {n_lrs} LRS + {n_hrs} HRS: I_BL = {i_total*1e6:.1f} µA")

# VREF recommendation
i_1lrs = V_READ * (1 * G_LRS + 2 * G_HRS)
i_2lrs = V_READ * (2 * G_LRS + 1 * G_HRS)
i_mid = (i_1lrs + i_2lrs) / 2
print(f"\n  VREF should produce current between:")
print(f"    1 LRS: {i_1lrs*1e6:.1f} µA")
print(f"    2 LRS: {i_2lrs*1e6:.1f} µA")
print(f"    Midpoint: {i_mid*1e6:.1f} µA")
print(f"  → VREF ≈ 0.9V (empirical, tuned in SPICE simulation)")

# ─────────────────────────────────────────
# SPICE Weight Mapping
# ─────────────────────────────────────────
print("\n" + "=" * 70)
print("SPICE Weight Mapping (Tfilament_0 values)")
print("=" * 70)

T_LRS = "4.5e-9"
T_HRS = "3.5e-9"

print("\n  [Array 1 (3×5)]")
print("  " + "-" * 50)
for i in range(3):
    for j in range(5):
        tf = T_LRS if W1[i][j] == 1 else T_HRS
        state = "LRS" if W1[i][j] == 1 else "HRS"
        print(f"  XR{i}{j}: Tfilament_0={tf}  ({state})")
    if i < 2:
        print()

print(f"\n  [Array 2 (5×2)]")
print("  " + "-" * 50)
for i in range(5):
    for j in range(2):
        tf = T_LRS if W2[i][j] == 1 else T_HRS
        state = "LRS" if W2[i][j] == 1 else "HRS"
        print(f"  XR{i}{j}: Tfilament_0={tf}  ({state})")
    if i < 4:
        print()

# ─────────────────────────────────────────
# RTL SA Wiring Summary
# ─────────────────────────────────────────
print("\n" + "=" * 70)
print("RTL SA Wiring Summary")
print("=" * 70)

print("\n  [Layer 1 SAs → Hidden neuron signals]")
print("  SA    INP      INN     Output Used    Signal     Function")
print("  " + "-" * 65)
sa1_info = [
    ("SA1_0", "BL1[0]", "VREF", "Q",  "h[0]", "OR(x1,x2)"),
    ("SA1_1", "BL1[1]", "VREF", "QB", "h[1]", "NAND(x1,x2)"),
    ("SA1_2", "BL1[2]", "VREF", "Q",  "h[2]", "x1"),
    ("SA1_3", "BL1[3]", "VREF", "Q",  "h[3]", "x2"),
    ("SA1_4", "BL1[4]", "VREF", "Q",  "h[4]", "0 (spare)"),
]
for name, inp, inn, out, sig, func in sa1_info:
    print(f"  {name:6s}  {inp:8s}  {inn:6s}  {out:2s}             {sig:6s}     {func}")

print("\n  [Layer 2 SAs → Output signals]")
print("  SA    INP      INN     Output Used    Signal     Function")
print("  " + "-" * 65)
sa2_info = [
    ("SA2_0", "BL2[0]", "VREF", "Q", "z[0]", "AND(OR,NAND) = XOR"),
    ("SA2_1", "BL2[1]", "VREF", "Q", "z[1]", "AND(OR,NAND) = XOR"),
]
for name, inp, inn, out, sig, func in sa2_info:
    print(f"  {name:6s}  {inp:8s}  {inn:6s}  {out:2s}             {sig:6s}     {func}")

print(f"\n  xor_result = z[0] = z[1] (redundant)")

print("\n" + "=" * 70)
if all_pass:
    print("VERIFICATION COMPLETE: 4/4 XOR PASS")
else:
    print("VERIFICATION FAILED")
print("=" * 70)
