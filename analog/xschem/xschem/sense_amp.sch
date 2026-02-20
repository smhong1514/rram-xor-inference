v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Latch-type Sense Amplifier} 280 -460 0 0 0.6 0.6 {}
T {Differential SA for RRAM BL/BLB sensing} 250 -420 0 0 0.3 0.3 {}
T {Precharge} 280 -370 0 0 0.2 0.2 {}
T {Equalize} 380 -260 0 0 0.2 0.2 {}
T {Cross-coupled Latch} 280 -110 0 0 0.2 0.2 {}
T {Input Pair} 300 130 0 0 0.2 0.2 {}
T {Tail} 330 270 0 0 0.2 0.2 {}
C {sky130_fd_pr/pfet_01v8.sym} 200 -320 0 0 {name=MP3 W=0.5 L=0.15 nf=1 mult=1 model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet_01v8.sym} 500 -320 0 1 {name=MP4 W=0.5 L=0.15 nf=1 mult=1 model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet_01v8.sym} 350 -240 0 0 {name=MP5 W=0.5 L=0.15 nf=1 mult=1 model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet_01v8.sym} 200 -160 0 0 {name=MP1 W=1 L=0.15 nf=1 mult=1 model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet_01v8.sym} 500 -160 0 1 {name=MP2 W=1 L=0.15 nf=1 mult=1 model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet_01v8.sym} 200 40 0 0 {name=MN1 W=1 L=0.15 nf=1 mult=1 model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet_01v8.sym} 500 40 0 1 {name=MN2 W=1 L=0.15 nf=1 mult=1 model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet_01v8.sym} 200 180 0 0 {name=MN3 W=2 L=0.15 nf=1 mult=1 model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet_01v8.sym} 500 180 0 1 {name=MN4 W=2 L=0.15 nf=1 mult=1 model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet_01v8.sym} 350 310 0 0 {name=MN0 W=2 L=0.15 nf=1 mult=1 model=nfet_01v8 spiceprefix=X}
N 220 -390 480 -390 {lab=VDD}
N 350 -390 350 -420 {lab=VDD}
N 220 -350 220 -390 {lab=VDD}
N 220 -290 220 -270 {lab=Q}
N 180 -320 120 -320 {lab=SAE}
N 220 -320 260 -320 {lab=VDD}
N 480 -350 480 -390 {lab=VDD}
N 480 -290 480 -270 {lab=QB}
N 520 -320 580 -320 {lab=SAE}
N 480 -320 440 -320 {lab=VDD}
N 370 -270 220 -270 {lab=Q}
N 370 -210 510 -210 {lab=QB}
N 330 -240 270 -240 {lab=SAE}
N 370 -240 410 -240 {lab=VDD}
N 220 -270 190 -270 {lab=Q}
N 190 -270 190 -130 {lab=Q}
N 190 -130 220 -130 {lab=Q}
N 480 -270 510 -270 {lab=QB}
N 510 -270 510 -130 {lab=QB}
N 510 -130 480 -130 {lab=QB}
N 220 -130 220 10 {lab=Q}
N 480 -130 480 10 {lab=QB}
N 220 -190 260 -190 {lab=VDD}
N 220 -160 260 -160 {lab=VDD}
N 480 -190 440 -190 {lab=VDD}
N 480 -160 440 -160 {lab=VDD}
N 220 -60 520 -60 {lab=Q}
N 520 -160 520 40 {lab=Q}
N 480 -40 180 -40 {lab=QB}
N 180 -160 180 40 {lab=QB}
N 220 -50 100 -50 {lab=Q}
N 480 -50 600 -50 {lab=QB}
N 220 40 260 40 {lab=VSS}
N 480 40 440 40 {lab=VSS}
N 220 70 220 150 {lab=FN1}
N 480 70 480 150 {lab=FN2}
N 180 180 100 180 {lab=INP}
N 220 180 260 180 {lab=VSS}
N 520 180 600 180 {lab=INN}
N 480 180 440 180 {lab=VSS}
N 220 210 480 210 {lab=TAIL}
N 370 280 370 210 {lab=TAIL}
N 370 340 370 380 {lab=VSS}
N 330 310 270 310 {lab=SAE}
N 370 310 410 310 {lab=VSS}
N 370 380 370 410 {lab=VSS}
C {lab_wire.sym} 350 -420 0 0 {name=l1 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 120 -320 2 0 {name=l2 sig_type=std_logic lab=SAE}
C {lab_wire.sym} 260 -320 0 0 {name=l3 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 580 -320 0 0 {name=l4 sig_type=std_logic lab=SAE}
C {lab_wire.sym} 440 -320 2 0 {name=l5 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 270 -240 2 0 {name=l6 sig_type=std_logic lab=SAE}
C {lab_wire.sym} 410 -240 0 0 {name=l7 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 260 -190 0 0 {name=l8 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 260 -160 0 0 {name=l9 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 440 -190 2 0 {name=l10 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 440 -160 2 0 {name=l11 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 100 -50 2 0 {name=l12 sig_type=std_logic lab=Q}
C {lab_wire.sym} 600 -50 0 0 {name=l13 sig_type=std_logic lab=QB}
C {lab_wire.sym} 260 40 0 0 {name=l14 sig_type=std_logic lab=VSS}
C {lab_wire.sym} 440 40 2 0 {name=l15 sig_type=std_logic lab=VSS}
C {lab_wire.sym} 220 110 0 0 {name=l16 sig_type=std_logic lab=FN1}
C {lab_wire.sym} 480 110 0 0 {name=l17 sig_type=std_logic lab=FN2}
C {lab_wire.sym} 100 180 2 0 {name=l18 sig_type=std_logic lab=INP}
C {lab_wire.sym} 260 180 0 0 {name=l19 sig_type=std_logic lab=VSS}
C {lab_wire.sym} 600 180 0 0 {name=l20 sig_type=std_logic lab=INN}
C {lab_wire.sym} 440 180 2 0 {name=l21 sig_type=std_logic lab=VSS}
C {lab_wire.sym} 350 210 0 0 {name=l22 sig_type=std_logic lab=TAIL}
C {lab_wire.sym} 270 310 2 0 {name=l23 sig_type=std_logic lab=SAE}
C {lab_wire.sym} 410 310 0 0 {name=l24 sig_type=std_logic lab=VSS}
C {lab_wire.sym} 370 410 0 0 {name=l25 sig_type=std_logic lab=VSS}
C {iopin.sym} 120 -320 2 0 {name=p1 lab=SAE}
C {iopin.sym} 100 180 2 0 {name=p2 lab=INP}
C {iopin.sym} 600 180 0 0 {name=p3 lab=INN}
C {iopin.sym} 100 -50 2 0 {name=p4 lab=Q}
C {iopin.sym} 600 -50 0 0 {name=p5 lab=QB}
C {iopin.sym} 350 -420 3 0 {name=p6 lab=VDD}
C {iopin.sym} 370 410 1 0 {name=p7 lab=VSS}
