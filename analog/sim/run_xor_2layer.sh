#!/bin/bash
source "$(cd "$(dirname "$0")" && pwd)/../../env.sh"
cd $PROJECT_ROOT/analog/sim

# 2-Layer XOR Neural Network (3 RRAM arrays)
# Layer 1: Array1(bias=0.9V)→OR, Array2(bias=1.5V)→NAND
# Layer 2: Array3(bias=1.35V)→AND(OR,NAND)=XOR
# Input encoding: logic 0=0.6V, logic 1=1.8V (offset for SA threshold)
# All arrays use SAME weight matrix (balanced: 2LRS+2HRS per column)

run_case() {
    local A=$1 B=$2 SLA=$3 SLB=$4 LOGFILE=$5

    $NGSPICE -b -o "$LOGFILE" << NGEOF
.title 2-Layer XOR A=${A} B=${B}
.lib "$PDK_ROOT/sky130B/libs.tech/ngspice/sky130.lib.spice" tt

.subckt sky130_fd_pr_reram__reram_cell TE BE Tfilament_0=3.3e-9
R1 TE BE {500k + (10k - 500k) * (Tfilament_0 - 3.3e-9) / (4.9e-9 - 3.3e-9)}
.ends sky130_fd_pr_reram__reram_cell

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

* Unified RRAM 4x4 array - same weight matrix for all instances
* Balanced columns: 2 LRS + 2 HRS per column
* SA1 signs: [+,+,-,-], SA2 signs: [-,-,+,+] (complement)
.subckt rram_4x4_balanced BL0 BL1 BL2 BL3 WL0 WL1 WL2 WL3 SL0 SL1 SL2 SL3 GND
XR00 BL0 n00 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM00 n00 WL0 SL0 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR01 BL1 n01 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM01 n01 WL0 SL0 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR02 BL2 n02 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM02 n02 WL0 SL0 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR03 BL3 n03 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM03 n03 WL0 SL0 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR10 BL0 n10 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM10 n10 WL1 SL1 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR11 BL1 n11 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM11 n11 WL1 SL1 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR12 BL2 n12 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM12 n12 WL1 SL1 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR13 BL3 n13 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM13 n13 WL1 SL1 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR20 BL0 n20 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM20 n20 WL2 SL2 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR21 BL1 n21 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM21 n21 WL2 SL2 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR22 BL2 n22 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM22 n22 WL2 SL2 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR23 BL3 n23 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM23 n23 WL2 SL2 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR30 BL0 n30 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM30 n30 WL3 SL3 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR31 BL1 n31 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM31 n31 WL3 SL3 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR32 BL2 n32 sky130_fd_pr_reram__reram_cell Tfilament_0=3.3e-9
XM32 n32 WL3 SL3 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
XR33 BL3 n33 sky130_fd_pr_reram__reram_cell Tfilament_0=4.9e-9
XM33 n33 WL3 SL3 GND sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1.5 nf=1 mult=1
.ends rram_4x4_balanced

* ===== Power Supplies =====
VDD vdd 0 1.8
VWL vwl 0 3.3
VSS vss 0 0

* ===== LAYER 1 ARRAY 1 (OR, bias=0.45V) =====
XWLD1a_0 vdd wl1a_0 vdd vwl vss wl_driver
XWLD1a_1 vdd wl1a_1 vdd vwl vss wl_driver
XWLD1a_2 vdd wl1a_2 vdd vwl vss wl_driver
XWLD1a_3 vdd wl1a_3 vdd vwl vss wl_driver
XARR1a bl1a_0 bl1a_1 bl1a_2 bl1a_3 wl1a_0 wl1a_1 wl1a_2 wl1a_3 sl1a_0 sl1a_1 sl1a_2 sl1a_3 vss rram_4x4_balanced
XSA1a_1 sae1 bl1a_0 bl1a_1 h1 h1b vdd vss sense_amp
XSA1a_2 sae1 bl1a_2 bl1a_3 h1_nr h1_nrb vdd vss sense_amp
CH1  h1  0 10f
CH1B h1b 0 10f
VSL1a_0 sl1a_0 0 ${SLA}
VSL1a_1 sl1a_1 0 ${SLB}
VSL1a_2 sl1a_2 0 0.9
VSL1a_3 sl1a_3 0 0.9

* ===== LAYER 1 ARRAY 2 (NAND via SA2, bias=1.35V) =====
XWLD1b_0 vdd wl1b_0 vdd vwl vss wl_driver
XWLD1b_1 vdd wl1b_1 vdd vwl vss wl_driver
XWLD1b_2 vdd wl1b_2 vdd vwl vss wl_driver
XWLD1b_3 vdd wl1b_3 vdd vwl vss wl_driver
XARR1b bl1b_0 bl1b_1 bl1b_2 bl1b_3 wl1b_0 wl1b_1 wl1b_2 wl1b_3 sl1b_0 sl1b_1 sl1b_2 sl1b_3 vss rram_4x4_balanced
XSA1b_1 sae1 bl1b_0 bl1b_1 h2_and h2_andb vdd vss sense_amp
XSA1b_2 sae1 bl1b_2 bl1b_3 h2 h2b vdd vss sense_amp
CH2  h2  0 10f
CH2B h2b 0 10f
VSL1b_0 sl1b_0 0 ${SLA}
VSL1b_1 sl1b_1 0 ${SLB}
VSL1b_2 sl1b_2 0 1.5
VSL1b_3 sl1b_3 0 1.5

* ===== INTERLAYER BUFFER (ideal VCVS) =====
Eh1 sl2_0 0 h1 0 1.0
Eh2 sl2_1 0 h2 0 1.0

* ===== LAYER 2 ARRAY 3 (AND, bias=1.35V) =====
XWLD2_0 vdd wl2_0 vdd vwl vss wl_driver
XWLD2_1 vdd wl2_1 vdd vwl vss wl_driver
XWLD2_2 vdd wl2_2 vdd vwl vss wl_driver
XWLD2_3 vdd wl2_3 vdd vwl vss wl_driver
XARR2 bl2_0 bl2_1 bl2_2 bl2_3 wl2_0 wl2_1 wl2_2 wl2_3 sl2_0 sl2_1 sl2_2 sl2_3 vss rram_4x4_balanced
XSA2_1 sae2 bl2_0 bl2_1 y_xor y_xorb vdd vss sense_amp
XSA2_2 sae2 bl2_2 bl2_3 y_xnor y_xnorb vdd vss sense_amp
CY1  y_xor   0 10f
CY1B y_xorb  0 10f
VSL2_2 sl2_2 0 1.35
VSL2_3 sl2_3 0 1.35

* ===== Timing =====
VSAE1 sae1 0 PULSE(0 1.8 10n 0.1n 0.1n 80n 200n)
VSAE2 sae2 0 PULSE(0 1.8 40n 0.1n 0.1n 40n 200n)

.tran 0.01n 100n

.control
run
meas tran vh1 FIND v(h1) AT=35n
meas tran vh2 FIND v(h2) AT=35n
meas tran vy_xor FIND v(y_xor) AT=70n
meas tran vy_xorb FIND v(y_xorb) AT=70n
meas tran vbl1a_0 FIND v(bl1a_0) AT=15n
meas tran vbl1a_1 FIND v(bl1a_1) AT=15n
meas tran vbl1b_2 FIND v(bl1b_2) AT=15n
meas tran vbl1b_3 FIND v(bl1b_3) AT=15n
quit
.endc
.end
NGEOF
}

echo "================================================"
echo "  2-Layer RRAM XOR Neural Network Simulation"
echo "  Layer1: Array1(0.9V)=OR + Array2(1.5V)=NAND"
echo "  Layer2: Array3(1.35V)=AND(OR,NAND)=XOR"
echo "  Input: 0→0.6V, 1→1.8V | Same weights, diff bias"
echo "================================================"

PASS=0
FAIL=0
for A in 0 1; do
  for B in 0 1; do
    if [ "$A" == "0" ]; then SLA="0.6"; else SLA="1.8"; fi
    if [ "$B" == "0" ]; then SLB="0.6"; else SLB="1.8"; fi
    EXPECTED=$(( A ^ B ))
    LOGFILE="/tmp/xor2l_${A}_${B}.log"

    run_case "$A" "$B" "$SLA" "$SLB" "$LOGFILE" 2>/dev/null

    VH1=$(grep "vh1 " "$LOGFILE" | tail -1 | awk '{print $3}')
    VH2=$(grep "vh2 " "$LOGFILE" | tail -1 | awk '{print $3}')
    VY=$(grep "vy_xor " "$LOGFILE" | tail -1 | awk '{print $3}')

    H1_VAL=$(python3 -c "v=float('${VH1}'); print('1' if v > 0.9 else '0')" 2>/dev/null)
    H2_VAL=$(python3 -c "v=float('${VH2}'); print('1' if v > 0.9 else '0')" 2>/dev/null)
    Y_VAL=$(python3 -c "v=float('${VY}'); print('1' if v > 0.9 else '0')" 2>/dev/null)

    if [ "$Y_VAL" == "$EXPECTED" ]; then
      STATUS="PASS"; PASS=$((PASS+1))
    else
      STATUS="FAIL"; FAIL=$((FAIL+1))
    fi

    printf "A=%s B=%s | h1(OR)=%s[%s] h2(NAND)=%s[%s] | XOR=%s[%s] exp=%s | %s\n" \
      "$A" "$B" "$VH1" "$H1_VAL" "$VH2" "$H2_VAL" "$VY" "$Y_VAL" "$EXPECTED" "$STATUS"
  done
done

echo ""
echo "================================================"
echo "  Result: $PASS PASS / $FAIL FAIL out of 4"
echo "================================================"
