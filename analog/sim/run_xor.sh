#!/bin/bash
source "$(cd "$(dirname "$0")" && pwd)/../../env.sh"
cd $PROJECT_ROOT/analog/sim
$NGSPICE -b -o xor_sim.log << 'NGSPICE_END'
.title XOR Inference Testbench

.lib "$PDK_ROOT/sky130B/libs.tech/ngspice/sky130.lib.spice" tt

***** RRAM Cell Subcircuit (Resistor model for READ inference) *****
* LRS (Tfilament_0=4.9e-9) -> 10k ohm
* HRS (Tfilament_0=3.3e-9) -> 500k ohm
* Linear interpolation between HRS and LRS based on filament thickness
.subckt sky130_fd_pr_reram__reram_cell TE BE Tfilament_0=3.3e-9
R1 TE BE {500k + (10k - 500k) * (Tfilament_0 - 3.3e-9) / (4.9e-9 - 3.3e-9)}
.ends sky130_fd_pr_reram__reram_cell

***** WL Driver Subcircuit *****
.subckt wl_driver IN OUT VDD VWL VSS
XMP0 INB IN VDD VDD sky130_fd_pr__pfet_01v8 L=0.15 W=1 nf=1 mult=1
XMN0 INB IN VSS VSS sky130_fd_pr__nfet_01v8 L=0.15 W=0.5 nf=1 mult=1
XMP1 Q QB VWL VWL sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 mult=1
XMN1 Q IN VSS VSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=2 nf=1 mult=1
XMP2 QB Q VWL VWL sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 mult=1
XMN2 QB INB VSS VSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=2 nf=1 mult=1
XMP3 OUT Q VWL VWL sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=4 nf=1 mult=1
XMN3 OUT Q VSS VSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=2 nf=1 mult=1
.ends wl_driver

***** Sense Amplifier Subcircuit *****
.subckt sense_amp SAE INP INN Q QB VDD VSS
XMP3 Q SAE VDD VDD sky130_fd_pr__pfet_01v8 L=0.15 W=0.5 nf=1 mult=1
XMP4 QB SAE VDD VDD sky130_fd_pr__pfet_01v8 L=0.15 W=0.5 nf=1 mult=1
XMP5 QB SAE Q VDD sky130_fd_pr__pfet_01v8 L=0.15 W=0.5 nf=1 mult=1
XMP1 Q QB VDD VDD sky130_fd_pr__pfet_01v8 L=0.15 W=1 nf=1 mult=1
XMP2 QB Q VDD VDD sky130_fd_pr__pfet_01v8 L=0.15 W=1 nf=1 mult=1
XMN1 Q QB FN1 VSS sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 mult=1
XMN2 QB Q FN2 VSS sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 mult=1
XMN3 FN1 INP TAIL VSS sky130_fd_pr__nfet_01v8 L=0.15 W=2 nf=1 mult=1
XMN4 FN2 INN TAIL VSS sky130_fd_pr__nfet_01v8 L=0.15 W=2 nf=1 mult=1
XMN0 TAIL SAE VSS VSS sky130_fd_pr__nfet_01v8 L=0.15 W=2 nf=1 mult=1
.ends sense_amp

***** RRAM 4x4 Array (with XOR weights) *****
.subckt rram_4x4_xor BL0 BL1 BL2 BL3 WL0 WL1 WL2 WL3 SL0 SL1 SL2 SL3 GND
* Row 0 (SL[0]): input A first copy
XR00 BL0 n00 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM00 n00 WL0 SL0 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR01 BL1 n01 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM01 n01 WL1 SL0 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR02 BL2 n02 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM02 n02 WL2 SL0 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR03 BL3 n03 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM03 n03 WL3 SL0 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
* Row 1 (SL[1]): input A second copy
XR10 BL0 n10 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM10 n10 WL0 SL1 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR11 BL1 n11 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM11 n11 WL1 SL1 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR12 BL2 n12 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM12 n12 WL2 SL1 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR13 BL3 n13 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM13 n13 WL3 SL1 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
* Row 2 (SL[2]): input B first copy
XR20 BL0 n20 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM20 n20 WL0 SL2 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR21 BL1 n21 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM21 n21 WL1 SL2 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR22 BL2 n22 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM22 n22 WL2 SL2 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR23 BL3 n23 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM23 n23 WL3 SL2 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
* Row 3 (SL[3]): input B second copy
XR30 BL0 n30 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM30 n30 WL0 SL3 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR31 BL1 n31 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM31 n31 WL1 SL3 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR32 BL2 n32 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM32 n32 WL2 SL3 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR33 BL3 n33 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM33 n33 WL3 SL3 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
.ends rram_4x4_xor

***** Top-level *****
VDD vdd 0 1.8
VWL vwl 0 3.3
VSS vss 0 0

XWLD0 vdd wl0 vdd vwl vss wl_driver
XWLD1 vdd wl1 vdd vwl vss wl_driver
XWLD2 vdd wl2 vdd vwl vss wl_driver
XWLD3 vdd wl3 vdd vwl vss wl_driver

XARRAY bl0 bl1 bl2 bl3 wl0 wl1 wl2 wl3 sl0 sl1 sl2 sl3 vss rram_4x4_xor

XSA1 sae bl0 bl1 q1 qb1 vdd vss sense_amp
XSA2 sae bl2 bl3 q2 qb2 vdd vss sense_amp

CQ1  q1  0 10f
CQB1 qb1 0 10f
CQ2  q2  0 10f
CQB2 qb2 0 10f

VSAE sae 0 PULSE(0 1.8 10n 0.1n 0.1n 19.8n 40n)

* Test: A=0, B=1
VSL0 sl0 0 0
VSL1 sl1 0 0
VSL2 sl2 0 1.8
VSL3 sl3 0 1.8

.tran 0.1n 100n

.control
run
wrdata $PROJECT_ROOT/analog/sim/xor_result.csv v(sae) v(q1) v(qb1) v(q2) v(qb2)
meas tran vq1_eval FIND v(q1) AT=28n
meas tran vqb1_eval FIND v(qb1) AT=28n
meas tran vq2_eval FIND v(q2) AT=28n
meas tran vqb2_eval FIND v(qb2) AT=28n
quit
.endc

.end
NGSPICE_END
