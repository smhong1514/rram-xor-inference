#!/usr/bin/env python3
"""Post-layout vs Schematic comparison plots for all analog blocks."""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys

SIMDIR = os.path.dirname(os.path.abspath(__file__))

def load_wrdata(filename, ncols):
    """Load ngspice wrdata CSV. Format: time, val1, time, val2, ..."""
    data = np.loadtxt(filename)
    t = data[:, 0]
    signals = []
    for i in range(ncols):
        signals.append(data[:, 2*i + 1])
    return t, signals

def plot_sa():
    """Sense Amplifier comparison."""
    f = os.path.join(SIMDIR, 'sa_compare.csv')
    if not os.path.exists(f):
        print(f"[SKIP] {f} not found")
        return False

    # wrdata: v(sae) v(q_sch) v(qb_sch) v(q_lay) v(qb_lay) v(inp) v(inn)
    data = np.loadtxt(f)
    t = data[:, 0] * 1e9  # to ns
    sae    = data[:, 1]
    q_sch  = data[:, 3]
    qb_sch = data[:, 5]
    q_lay  = data[:, 7]
    qb_lay = data[:, 9]
    inp    = data[:, 11]
    inn    = data[:, 13]

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    fig.suptitle('Sense Amplifier: Schematic vs Layout', fontsize=14, fontweight='bold')

    # SAE + Input
    axes[0].plot(t, sae, 'k-', label='SAE', linewidth=1.5)
    axes[0].plot(t, inp, 'r--', label='INP (0.925V)', linewidth=1)
    axes[0].plot(t, inn, 'b--', label='INN (0.875V)', linewidth=1)
    axes[0].set_ylabel('Voltage (V)')
    axes[0].legend(loc='upper right')
    axes[0].set_title('Stimulus')
    axes[0].grid(True, alpha=0.3)

    # Q output
    axes[1].plot(t, q_sch, 'r-', label='Q (Schematic)', linewidth=1.5)
    axes[1].plot(t, q_lay, 'b--', label='Q (Layout)', linewidth=1.5)
    axes[1].set_ylabel('Voltage (V)')
    axes[1].legend(loc='upper right')
    axes[1].set_title('Q Output')
    axes[1].grid(True, alpha=0.3)

    # QB output
    axes[2].plot(t, qb_sch, 'r-', label='QB (Schematic)', linewidth=1.5)
    axes[2].plot(t, qb_lay, 'b--', label='QB (Layout)', linewidth=1.5)
    axes[2].set_ylabel('Voltage (V)')
    axes[2].set_xlabel('Time (ns)')
    axes[2].legend(loc='upper right')
    axes[2].set_title('QB Output')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    out = os.path.join(SIMDIR, 'sa_compare.png')
    plt.savefig(out, dpi=150)
    print(f"[SA] Saved: {out}")

    # Numeric comparison
    idx_28 = np.argmin(np.abs(t - 28.0))
    print(f"  @28ns: Q_sch={q_sch[idx_28]:.4f}V  Q_lay={q_lay[idx_28]:.4f}V  diff={abs(q_sch[idx_28]-q_lay[idx_28])*1000:.1f}mV")
    print(f"  @28ns: QB_sch={qb_sch[idx_28]:.4f}V QB_lay={qb_lay[idx_28]:.4f}V  diff={abs(qb_sch[idx_28]-qb_lay[idx_28])*1000:.1f}mV")
    plt.close()
    return True

def plot_wl():
    """WL Driver comparison."""
    f = os.path.join(SIMDIR, 'wl_compare.csv')
    if not os.path.exists(f):
        print(f"[SKIP] {f} not found")
        return False

    # wrdata: v(in) v(out_sch) v(out_lay)
    data = np.loadtxt(f)
    t = data[:, 0] * 1e9
    vin     = data[:, 1]
    out_sch = data[:, 3]
    out_lay = data[:, 5]

    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    fig.suptitle('WL Driver: Schematic vs Layout', fontsize=14, fontweight='bold')

    axes[0].plot(t, vin, 'k-', label='IN (1.8V)', linewidth=1.5)
    axes[0].set_ylabel('Voltage (V)')
    axes[0].legend(loc='upper right')
    axes[0].set_title('Input')
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t, out_sch, 'r-', label='OUT (Schematic)', linewidth=1.5)
    axes[1].plot(t, out_lay, 'b--', label='OUT (Layout)', linewidth=1.5)
    axes[1].set_ylabel('Voltage (V)')
    axes[1].set_xlabel('Time (ns)')
    axes[1].legend(loc='upper right')
    axes[1].set_title('Output (should reach VWL=3.3V)')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    out = os.path.join(SIMDIR, 'wl_compare.png')
    plt.savefig(out, dpi=150)
    print(f"[WL] Saved: {out}")

    idx_25 = np.argmin(np.abs(t - 25.0))
    idx_45 = np.argmin(np.abs(t - 45.0))
    print(f"  @25ns (IN=1): OUT_sch={out_sch[idx_25]:.4f}V  OUT_lay={out_lay[idx_25]:.4f}V  diff={abs(out_sch[idx_25]-out_lay[idx_25])*1000:.1f}mV")
    print(f"  @45ns (IN=0): OUT_sch={out_sch[idx_45]:.4f}V  OUT_lay={out_lay[idx_45]:.4f}V  diff={abs(out_sch[idx_45]-out_lay[idx_45])*1000:.1f}mV")
    plt.close()
    return True

def plot_blwd():
    """BL Write Driver comparison."""
    f = os.path.join(SIMDIR, 'blwd_compare.csv')
    if not os.path.exists(f):
        print(f"[SKIP] {f} not found")
        return False

    # wrdata: v(en) v(data) v(bl_sch) v(bl_lay)
    data = np.loadtxt(f)
    t = data[:, 0] * 1e9
    en     = data[:, 1]
    dat    = data[:, 3]
    bl_sch = data[:, 5]
    bl_lay = data[:, 7]

    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    fig.suptitle('BL Write Driver: Schematic vs Layout', fontsize=14, fontweight='bold')

    axes[0].plot(t, en, 'k-', label='EN', linewidth=1.5)
    axes[0].plot(t, dat, 'g--', label='DATA', linewidth=1.5)
    axes[0].set_ylabel('Voltage (V)')
    axes[0].legend(loc='upper right')
    axes[0].set_title('Stimulus')
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t, bl_sch, 'r-', label='BL (Schematic)', linewidth=1.5)
    axes[1].plot(t, bl_lay, 'b--', label='BL (Layout)', linewidth=1.5)
    axes[1].set_ylabel('Voltage (V)')
    axes[1].set_xlabel('Time (ns)')
    axes[1].legend(loc='upper right')
    axes[1].set_title('BL Output')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    out = os.path.join(SIMDIR, 'blwd_compare.png')
    plt.savefig(out, dpi=150)
    print(f"[BL_WD] Saved: {out}")

    for t_ns, label in [(40, "EN=1,DATA=1"), (80, "EN=1,DATA=0"), (120, "EN=0,Hi-Z"), (160, "EN=1,DATA=1")]:
        idx = np.argmin(np.abs(t - t_ns))
        d = abs(bl_sch[idx] - bl_lay[idx]) * 1000
        print(f"  @{t_ns}ns ({label}): BL_sch={bl_sch[idx]:.4f}V  BL_lay={bl_lay[idx]:.4f}V  diff={d:.1f}mV")
    plt.close()
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Post-Layout vs Schematic Comparison")
    print("=" * 60)
    results = []
    results.append(("Sense Amp", plot_sa()))
    results.append(("WL Driver", plot_wl()))
    results.append(("BL Write Driver", plot_blwd()))
    print()
    print("=" * 60)
    for name, ok in results:
        status = "DONE" if ok else "SKIP"
        print(f"  [{status}] {name}")
    print("=" * 60)
