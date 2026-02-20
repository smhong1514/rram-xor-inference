#!/usr/bin/env python3
"""Plot RRAM mixed-signal simulation results."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import os

def load_wrdata(filename):
    """Load ngspice wrdata CSV (format: time, val1, time, val2, ...)"""
    data = np.loadtxt(filename)
    n_cols = data.shape[1]
    n_signals = n_cols // 2
    time = data[:, 0]
    signals = [data[:, 2*i+1] for i in range(n_signals)]
    return time, signals

def main():
    csv_file = 'rram_mixed_tb.csv'
    if not os.path.exists(csv_file):
        print(f"ERROR: {csv_file} not found")
        sys.exit(1)

    time, sigs = load_wrdata(csv_file)
    t_ns = time * 1e9

    # Signal order from wrdata:
    # 0: wl_in0, 1: wl0(3.3V), 2: sae
    # 3: bl0, 4: bl1, 5: bl2, 6: bl3
    # 7: sa_q0, 8: sa_q1, 9: sa_q2, 10: sa_q3
    # 11: sa_qb0, 12: sa_qb1, 13: sa_qb2, 14: sa_qb3
    # 15: rram_sl0, 16: sl_en0

    fig, axes = plt.subplots(5, 1, figsize=(14, 14), sharex=True)
    fig.suptitle('RRAM Mixed-Signal Simulation: Read Row 0\n'
                 'WL Driver + RRAM 4x4 Array + Sense Amplifier\n'
                 'Pre-programmed: [LRS, HRS, LRS, HRS] -> Expected: [1, 0, 1, 0]',
                 fontsize=13, fontweight='bold')

    colors_bl = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    # Panel 1: WL Driver
    ax = axes[0]
    ax.plot(t_ns, sigs[0], 'b-', linewidth=1.5, label='WL_IN0 (1.8V digital)')
    ax.plot(t_ns, sigs[1], 'r-', linewidth=2, label='WL0 (3.3V output)')
    ax.axhline(y=3.3, color='red', linestyle=':', alpha=0.3)
    ax.axhline(y=1.8, color='blue', linestyle=':', alpha=0.3)
    ax.set_ylabel('Voltage (V)')
    ax.set_title('WL Driver: 1.8V -> 3.3V Level Shift', fontsize=10)
    ax.legend(loc='right', fontsize=8)
    ax.set_ylim(-0.5, 3.8)
    ax.grid(True, alpha=0.3)

    # Panel 2: SAE & SL
    ax = axes[1]
    ax.plot(t_ns, sigs[2], 'r-', linewidth=2, label='SAE (read_en)')
    ax.plot(t_ns, sigs[15], 'b-', linewidth=1.5, label='RRAM_SL0 (-> GND)')
    ax.plot(t_ns, sigs[16], 'g--', linewidth=1, label='SL_EN0 (switch ctrl)')
    ax.set_ylabel('Voltage (V)')
    ax.set_title('Control Signals: SAE & Sourceline', fontsize=10)
    ax.legend(loc='right', fontsize=8)
    ax.set_ylim(-0.2, 2.0)
    ax.grid(True, alpha=0.3)
    ax.annotate('BL Precharge OFF\n(WL activates)', xy=(80, 0.3),
                fontsize=7, color='gray', ha='center')
    ax.annotate('SA Evaluate', xy=(140, 1.5),
                fontsize=8, color='red', ha='center', fontweight='bold')

    # Panel 3: Bitline voltages
    ax = axes[2]
    labels_bl = ['BL0 (LRS, data=1)', 'BL1 (HRS, data=0)',
                 'BL2 (LRS, data=1)', 'BL3 (HRS, data=0)']
    for i in range(4):
        ax.plot(t_ns, sigs[3+i], color=colors_bl[i], linewidth=1.5,
                label=labels_bl[i])
    ax.axhline(y=0.9, color='gray', linestyle='--', alpha=0.7, label='VREF (0.9V)')
    ax.set_ylabel('Voltage (V)')
    ax.set_title('Bitline Voltages: LRS discharges fast, HRS stays high', fontsize=10)
    ax.legend(loc='right', fontsize=7)
    ax.set_ylim(-0.2, 2.0)
    ax.grid(True, alpha=0.3)
    ax.axvspan(100, 180, alpha=0.05, color='red')

    # Panel 4: SA Q outputs
    ax = axes[3]
    labels_sa = ['SA_Q0 (exp=HIGH)', 'SA_Q1 (exp=LOW)',
                 'SA_Q2 (exp=HIGH)', 'SA_Q3 (exp=LOW)']
    for i in range(4):
        ax.plot(t_ns, sigs[7+i], color=colors_bl[i], linewidth=2,
                label=labels_sa[i])
    ax.axhline(y=0.9, color='gray', linestyle='--', alpha=0.3)
    ax.set_ylabel('Voltage (V)')
    ax.set_title('Sense Amplifier Outputs: Full rail-to-rail (0V or 1.8V)', fontsize=10)
    ax.legend(loc='right', fontsize=8)
    ax.set_ylim(-0.2, 2.0)
    ax.grid(True, alpha=0.3)

    # Panel 5: SA QB outputs
    ax = axes[4]
    labels_qb = ['SA_QB0', 'SA_QB1', 'SA_QB2', 'SA_QB3']
    for i in range(4):
        ax.plot(t_ns, sigs[11+i], color=colors_bl[i], linewidth=1.5,
                linestyle='--', label=labels_qb[i])
    ax.set_ylabel('Voltage (V)')
    ax.set_xlabel('Time (ns)')
    ax.set_title('SA Complementary Outputs (QB)', fontsize=10)
    ax.legend(loc='right', fontsize=8)
    ax.set_ylim(-0.2, 2.0)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('rram_cosim_result.png', dpi=150, bbox_inches='tight')
    print("Plot saved: rram_cosim_result.png")

    # Print summary
    print("\n" + "="*50)
    print("SIMULATION RESULT SUMMARY")
    print("="*50)

    idx = np.searchsorted(t_ns, 150)
    print(f"WL Driver output (t=150ns): {sigs[1][idx]:.2f}V (expect 3.3V)")
    print()

    expected = [1, 0, 1, 0]
    state_names = ['LRS', 'HRS', 'LRS', 'HRS']
    all_pass = True
    for i in range(4):
        sa_v = sigs[7+i][idx]
        bl_v = sigs[3+i][idx]
        detected = 1 if sa_v > 0.9 else 0
        status = "PASS" if detected == expected[i] else "FAIL"
        if detected != expected[i]:
            all_pass = False
        print(f"  BL{i} ({state_names[i]}): V={bl_v:.4f}V -> "
              f"SA_Q{i}={sa_v:.3f}V -> data={detected} (exp={expected[i]}) [{status}]")

    print()
    if all_pass:
        print(">>> ALL 4 COLUMNS: PASS <<<")
    else:
        print(">>> SOME COLUMNS FAILED <<<")
    print("="*50)

if __name__ == '__main__':
    main()
