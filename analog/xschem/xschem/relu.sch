v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {ReLU Activation Function (5T OTA)} 220 -320 0 0 0.6 0.6 {}
T {Analog ReLU for RRAM Neural Network} 220 -290 0 0 0.3 0.3 {}
T {PMOS Current Mirror} 270 -200 0 0 0.2 0.2 {}
T {NMOS Differential Pair} 260 -10 0 0 0.2 0.2 {}
T {Tail Current Source} 290 220 0 0 0.2 0.2 {}
C {sky130_fd_pr/pfet_01v8.sym} 200 -160 0 0 {name=M3 W=2 L=0.5 nf=1 mult=1 model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet_01v8.sym} 400 -160 0 1 {name=M4 W=2 L=0.5 nf=1 mult=1 model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet_01v8.sym} 200 40 0 0 {name=M1 W=2 L=0.5 nf=1 mult=1 model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet_01v8.sym} 400 40 0 1 {name=M2 W=2 L=0.5 nf=1 mult=1 model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet_01v8.sym} 300 180 0 0 {name=M5 W=2 L=0.5 nf=1 mult=1 model=nfet_01v8 spiceprefix=X}
N 220 -220 380 -220 {lab=VDD}
N 300 -220 300 -250 {lab=VDD}
N 220 -190 220 -220 {lab=VDD}
N 380 -190 380 -220 {lab=VDD}
N 220 -160 260 -160 {lab=VDD}
N 380 -160 340 -160 {lab=VDD}
N 180 -160 180 -130 {lab=node_A}
N 180 -130 220 -130 {lab=node_A}
N 220 -130 220 10 {lab=node_A}
N 220 -100 440 -100 {lab=node_A}
N 440 -100 440 -160 {lab=node_A}
N 440 -160 420 -160 {lab=node_A}
N 380 -130 380 10 {lab=OUT}
N 380 -130 600 -130 {lab=OUT}
N 220 70 220 120 {lab=TAIL}
N 380 70 380 120 {lab=TAIL}
N 220 120 380 120 {lab=TAIL}
N 320 120 320 150 {lab=TAIL}
N 320 210 320 280 {lab=VSS}
N 220 40 260 40 {lab=VSS}
N 380 40 340 40 {lab=VSS}
N 320 180 360 180 {lab=VSS}
N 100 40 180 40 {lab=VREF}
N 500 40 420 40 {lab=VBL}
N 200 180 280 180 {lab=VBIAS}
C {lab_wire.sym} 300 -250 0 0 {name=l1 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 260 -160 0 0 {name=l2 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 340 -160 2 0 {name=l3 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 330 -100 0 0 {name=l4 sig_type=std_logic lab=node_A}
C {lab_wire.sym} 500 -130 0 0 {name=l5 sig_type=std_logic lab=OUT}
C {lab_wire.sym} 300 120 0 0 {name=l6 sig_type=std_logic lab=TAIL}
C {lab_wire.sym} 260 40 0 0 {name=l7 sig_type=std_logic lab=VSS}
C {lab_wire.sym} 340 40 2 0 {name=l8 sig_type=std_logic lab=VSS}
C {lab_wire.sym} 360 180 0 0 {name=l9 sig_type=std_logic lab=VSS}
C {lab_wire.sym} 320 280 0 0 {name=l10 sig_type=std_logic lab=VSS}
C {lab_wire.sym} 100 40 2 0 {name=l11 sig_type=std_logic lab=VREF}
C {lab_wire.sym} 500 40 0 0 {name=l12 sig_type=std_logic lab=VBL}
C {lab_wire.sym} 200 180 2 0 {name=l13 sig_type=std_logic lab=VBIAS}
C {iopin.sym} 100 40 2 0 {name=p1 lab=VREF}
C {iopin.sym} 500 40 0 0 {name=p2 lab=VBL}
C {iopin.sym} 600 -130 0 0 {name=p3 lab=OUT}
C {iopin.sym} 200 180 2 0 {name=p4 lab=VBIAS}
C {iopin.sym} 300 -250 3 0 {name=p5 lab=VDD}
C {iopin.sym} 320 280 1 0 {name=p6 lab=VSS}
