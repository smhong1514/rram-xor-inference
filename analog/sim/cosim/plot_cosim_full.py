#!/usr/bin/env python3
"""Plot RRAM Full Mixed-Signal Co-Simulation Results"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Load data (wrdata format: time,val1,time,val2,...)
data = np.loadtxt('rram_cosim_full.csv')
t = data[:, 0] * 1e9  # Convert to ns

# Column mapping (each signal has its own time column):
# 0:time 1:rdy_a 2:time 3:rv_a 4:time 5:rd_a 6:time 7:wen_a 8:time 9:ren_a
# 10:time 11:wl_in0 12:time 13:wl_in1 14:time 15:wl0 16:time 17:wl1
# 18:time 19:bl0 20:time 21:bl1 22:time 23:bl2 24:time 25:bl3
# 26:time 27:sa_q0 28:time 29:sa_q1 30:time 31:sa_q2 32:time 33:sa_q3
# 34:time 35:prech_en_a 36:time 37:sl_en1 38:time 39:bl_en_a2 40:time 41:bl_data_a2
rdy   = data[:, 1]
rv    = data[:, 3]
rd    = data[:, 5]
wen   = data[:, 7]
ren   = data[:, 9]
wl_in1 = data[:, 13]
wl1   = data[:, 17]
bl0   = data[:, 19]
bl1   = data[:, 21]
bl2   = data[:, 23]
bl3   = data[:, 25]
sa_q0 = data[:, 27]
sa_q1 = data[:, 29]
sa_q2 = data[:, 31]
sa_q3 = data[:, 33]
prech = data[:, 35]
sl_en1 = data[:, 37]
bl_en2 = data[:, 39]
bl_dat2 = data[:, 41]

fig, axes = plt.subplots(7, 1, figsize=(16, 20), sharex=True)
fig.suptitle('RRAM Full Mixed-Signal Co-Simulation\n'
             'd_cosim Controller + WL Driver + RRAM 4x4 + Sense Amplifier (Closed Loop)',
             fontsize=14, fontweight='bold')

colors = {'ctrl': '#2196F3', 'rv': '#4CAF50', 'rd': '#FF9800',
          'bl0': '#E91E63', 'bl1': '#9C27B0', 'bl2': '#FF5722', 'bl3': '#795548'}

# Panel 1: Controller Status
ax = axes[0]
ax.plot(t, rdy, label='cmd_ready', color='#2196F3', linewidth=1.2)
ax.plot(t, rv, label='resp_valid', color='#4CAF50', linewidth=1.2)
ax.plot(t, rd, label='resp_data', color='#FF9800', linewidth=1.2, linestyle='--')
ax.set_ylabel('Voltage (V)')
ax.set_title('Controller Status Signals')
ax.legend(loc='upper right', fontsize=8, ncol=3)
ax.set_ylim(-0.2, 2.2)
ax.grid(True, alpha=0.3)

# Panel 2: Control Signals (WL, SAE, Write)
ax = axes[1]
ax.plot(t, wl_in1, label='wl_sel[1] (DAC out)', color='#2196F3', linewidth=1.2)
ax.plot(t, ren, label='read_en (SAE)', color='#4CAF50', linewidth=1.2)
ax.plot(t, wen, label='write_en', color='#E91E63', linewidth=1.2)
ax.plot(t, prech, label='precharge_ctrl', color='#9E9E9E', linewidth=0.8, linestyle=':')
ax.set_ylabel('Voltage (V)')
ax.set_title('Array Control Signals')
ax.legend(loc='upper right', fontsize=8, ncol=4)
ax.set_ylim(-0.2, 2.2)
ax.grid(True, alpha=0.3)

# Panel 3: WL Driver Output
ax = axes[2]
ax.plot(t, wl1, label='WL1 (3.3V level)', color='#FF5722', linewidth=1.5)
ax.plot(t, sl_en1, label='SL_EN1', color='#9C27B0', linewidth=1.2, linestyle='--')
ax.set_ylabel('Voltage (V)')
ax.set_title('WL Driver Output + SL Control')
ax.legend(loc='upper right', fontsize=8)
ax.set_ylim(-0.5, 4.0)
ax.axhline(y=3.3, color='r', linestyle=':', alpha=0.3, linewidth=0.5)
ax.grid(True, alpha=0.3)

# Panel 4: BL Write Signals
ax = axes[3]
ax.plot(t, bl_en2, label='bl_en[2]', color='#2196F3', linewidth=1.2)
ax.plot(t, bl_dat2, label='bl_data[2]', color='#FF9800', linewidth=1.2, linestyle='--')
ax.set_ylabel('Voltage (V)')
ax.set_title('BL Write Driver (Column 2)')
ax.legend(loc='upper right', fontsize=8)
ax.set_ylim(-0.2, 2.2)
ax.grid(True, alpha=0.3)

# Panel 5: Bitline Voltages
ax = axes[4]
ax.plot(t, bl0, label='BL0 (Row1:HRS)', color='#E91E63', linewidth=1.2)
ax.plot(t, bl1, label='BL1 (Row1:LRS)', color='#9C27B0', linewidth=1.2)
ax.plot(t, bl2, label='BL2 (Row1:HRS)', color='#FF5722', linewidth=1.5)
ax.plot(t, bl3, label='BL3 (Row1:LRS)', color='#795548', linewidth=1.2)
ax.axhline(y=0.9, color='gray', linestyle='--', alpha=0.5, label='VREF=0.9V')
ax.set_ylabel('Voltage (V)')
ax.set_title('Bitline Voltages (BL vs VREF)')
ax.legend(loc='upper right', fontsize=8, ncol=3)
ax.set_ylim(-0.2, 2.2)
ax.grid(True, alpha=0.3)

# Panel 6: SA Outputs
ax = axes[5]
ax.plot(t, sa_q0, label='SA_Q0 (HRS→LOW)', color='#E91E63', linewidth=1.2)
ax.plot(t, sa_q1, label='SA_Q1 (LRS→HIGH)', color='#9C27B0', linewidth=1.2)
ax.plot(t, sa_q2, label='SA_Q2 (HRS→LOW)', color='#FF5722', linewidth=1.5)
ax.plot(t, sa_q3, label='SA_Q3 (LRS→HIGH)', color='#795548', linewidth=1.2)
ax.set_ylabel('Voltage (V)')
ax.set_title('Sense Amplifier Outputs (→ bl_sense feedback)')
ax.legend(loc='upper right', fontsize=8, ncol=2)
ax.set_ylim(-0.2, 2.2)
ax.grid(True, alpha=0.3)

# Panel 7: Closed-loop feedback visualization
ax = axes[6]
ax.plot(t, sa_q2, label='SA_Q2 → bl_sense[2]', color='#FF5722', linewidth=1.5)
ax.plot(t, rd, label='resp_data (from bl_sense[col])', color='#FF9800', linewidth=1.5, linestyle='--')
ax.plot(t, rv, label='resp_valid', color='#4CAF50', linewidth=1.0, alpha=0.5)
ax.set_ylabel('Voltage (V)')
ax.set_xlabel('Time (ns)')
ax.set_title('Closed-Loop: SA Output → bl_sense[2] → Controller resp_data')
ax.legend(loc='upper right', fontsize=8, ncol=3)
ax.set_ylim(-0.2, 2.2)
ax.grid(True, alpha=0.3)

# Add phase annotations
for ax in axes:
    ax.axvspan(45, 115, alpha=0.05, color='blue')
    ax.axvspan(145, 250, alpha=0.05, color='red')
    ax.axvspan(260, 340, alpha=0.05, color='green')

# Phase labels on top panel
axes[0].text(80, 2.0, 'READ', ha='center', fontsize=9, color='blue', fontweight='bold')
axes[0].text(197, 2.0, 'WRITE', ha='center', fontsize=9, color='red', fontweight='bold')
axes[0].text(300, 2.0, 'VERIFY', ha='center', fontsize=9, color='green', fontweight='bold')

plt.tight_layout()
plt.savefig('rram_cosim_full.png', dpi=150, bbox_inches='tight')
print("Saved: rram_cosim_full.png")
