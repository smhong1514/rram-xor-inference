v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {WL Driver - Single Channel} 300 -380 0 0 0.6 0.6 {}
T {Level Shifter (1.8V to VWL) + HV Buffer} 250 -340 0 0 0.3 0.3 {}
T {Input Inv} -30 -240 0 0 0.25 0.25 {}
T {Level Shifter} 300 -240 0 0 0.25 0.25 {}
T {HV Buffer} 680 -240 0 0 0.25 0.25 {}
C {sky130_fd_pr/pfet_01v8.sym} 0 -100 0 0 {name=MP0 W=1 L=0.15 nf=1 mult=1 model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet_01v8.sym} 0 100 0 0 {name=MN0 W=0.5 L=0.15 nf=1 mult=1 model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 250 -100 0 0 {name=MP1 W=1 L=0.5 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 250 100 0 0 {name=MN1 W=2 L=0.5 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 450 -100 0 0 {name=MP2 W=1 L=0.5 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 450 100 0 0 {name=MN2 W=2 L=0.5 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 700 -100 0 0 {name=MP3 W=4 L=0.5 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 700 100 0 0 {name=MN3 W=2 L=0.5 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X}
N 20 -70 20 70 {lab=INB}
N 20 -130 20 -200 {lab=VDD}
N 20 130 20 200 {lab=VSS}
N -20 -100 -50 -100 {lab=IN}
N -50 -100 -50 100 {lab=IN}
N -50 100 -20 100 {lab=IN}
N -50 0 -100 0 {lab=IN}
N 20 -100 50 -100 {lab=VDD}
N 20 100 50 100 {lab=VSS}
N 270 -70 270 70 {lab=Q}
N 270 -130 270 -200 {lab=VWL}
N 270 130 270 200 {lab=VSS}
N 230 -100 200 -100 {lab=QB}
N 230 100 200 100 {lab=IN}
N 270 -100 290 -100 {lab=VWL}
N 270 100 290 100 {lab=VSS}
N 470 -70 470 70 {lab=QB}
N 470 -130 470 -200 {lab=VWL}
N 470 130 470 200 {lab=VSS}
N 430 -100 400 -100 {lab=Q}
N 430 100 400 100 {lab=INB}
N 470 -100 490 -100 {lab=VWL}
N 470 100 490 100 {lab=VSS}
N 720 -70 720 70 {lab=OUT}
N 720 -130 720 -200 {lab=VWL}
N 720 130 720 200 {lab=VSS}
N 680 -100 650 -100 {lab=Q}
N 680 100 650 100 {lab=Q}
N 720 -100 740 -100 {lab=VWL}
N 720 100 740 100 {lab=VSS}
N 720 0 780 0 {lab=OUT}
N 150 -200 720 -200 {lab=VWL}
N 20 200 720 200 {lab=VSS}
N 20 -200 20 -220 {lab=VDD}
N 150 -200 150 -220 {lab=VWL}
N 370 200 370 220 {lab=VSS}
C {lab_wire.sym} 20 0 0 0 {name=l1 sig_type=std_logic lab=INB}
C {lab_wire.sym} 270 0 0 0 {name=l2 sig_type=std_logic lab=Q}
C {lab_wire.sym} 470 0 0 0 {name=l3 sig_type=std_logic lab=QB}
C {lab_wire.sym} 200 -100 2 0 {name=l4 sig_type=std_logic lab=QB}
C {lab_wire.sym} 200 100 2 0 {name=l5 sig_type=std_logic lab=IN}
C {lab_wire.sym} 400 -100 2 0 {name=l6 sig_type=std_logic lab=Q}
C {lab_wire.sym} 400 100 2 0 {name=l7 sig_type=std_logic lab=INB}
C {lab_wire.sym} 650 -100 2 0 {name=l8 sig_type=std_logic lab=Q}
C {lab_wire.sym} 650 100 2 0 {name=l9 sig_type=std_logic lab=Q}
C {lab_wire.sym} 50 -100 0 0 {name=l10 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 50 100 0 0 {name=l11 sig_type=std_logic lab=VSS}
C {lab_wire.sym} 290 -100 0 0 {name=l12 sig_type=std_logic lab=VWL}
C {lab_wire.sym} 290 100 0 0 {name=l13 sig_type=std_logic lab=VSS}
C {lab_wire.sym} 490 -100 0 0 {name=l14 sig_type=std_logic lab=VWL}
C {lab_wire.sym} 490 100 0 0 {name=l15 sig_type=std_logic lab=VSS}
C {lab_wire.sym} 740 -100 0 0 {name=l16 sig_type=std_logic lab=VWL}
C {lab_wire.sym} 740 100 0 0 {name=l17 sig_type=std_logic lab=VSS}
C {lab_wire.sym} -100 0 2 0 {name=l18 sig_type=std_logic lab=IN}
C {lab_wire.sym} 780 0 0 0 {name=l19 sig_type=std_logic lab=OUT}
C {lab_wire.sym} 20 -220 0 0 {name=l20 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 150 -220 0 0 {name=l21 sig_type=std_logic lab=VWL}
C {lab_wire.sym} 370 220 0 0 {name=l22 sig_type=std_logic lab=VSS}
C {iopin.sym} -100 0 2 0 {name=p1 lab=IN}
C {iopin.sym} 780 0 0 0 {name=p2 lab=OUT}
C {iopin.sym} 20 -220 3 0 {name=p3 lab=VDD}
C {iopin.sym} 150 -220 3 0 {name=p4 lab=VWL}
C {iopin.sym} 370 220 1 0 {name=p5 lab=VSS}
