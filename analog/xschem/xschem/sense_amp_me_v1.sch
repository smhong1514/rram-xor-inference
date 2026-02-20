v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -90 -40 -90 30 {lab=BL}
N 90 -40 90 30 {lab=VDD}
N -50 -70 -30 -70 {lab=VDD}
N -30 -70 -30 60 {lab=VDD}
N -50 60 -30 60 {lab=VDD}
N 30 -70 50 -70 {lab=BL}
N 30 -70 30 60 {lab=BL}
N 30 60 50 60 {lab=BL}
N -30 -20 90 -20 {lab=VDD}
N -90 20 30 20 {lab=BL}
N -90 -140 -90 -100 {lab=#net1}
N -90 -140 90 -140 {lab=#net1}
N 90 -140 90 -100 {lab=#net1}
N -120 -70 -90 -70 {lab=VDD}
N 90 -70 120 -70 {lab=VDD}
N -120 60 -90 60 {lab=VSS}
N 90 60 120 60 {lab=VSS}
N -90 90 -90 120 {lab=#net2}
N -90 120 90 120 {lab=#net2}
N 90 90 90 120 {lab=#net2}
N -220 -120 -220 180 {lab=BL}
N -220 180 -220 210 {lab=BL}
N 0 -170 0 -140 {lab=#net1}
N 0 -260 -0 -230 {lab=#net3}
N 200 -120 200 190 {lab=VDD}
N 200 190 200 210 {lab=VDD}
N -180 240 160 240 {lab=#net4}
N -30 -200 0 -200 {lab=VDD}
N 200 240 230 240 {lab=VSS}
N -250 240 -220 240 {lab=VSS}
N 90 -0 200 0 {lab=VDD}
N -220 -0 -90 -0 {lab=BL}
N 40 -200 70 -200 {lab=SAEB}
N -220 270 -220 290 {lab=VSS}
N 200 270 200 290 {lab=VSS}
N -220 -300 -220 -120 {lab=BL}
N 200 -300 200 -120 {lab=VDD}
N 200 -30 310 -30 {lab=VDD}
N 310 -130 310 -30 {lab=VDD}
N 280 -160 310 -160 {lab=VSS}
N 350 -160 370 -160 {lab=REFE}
N 310 -230 310 -190 {lab=VREF}
N -0 120 0 130 {lab=#net2}
N -0 190 0 210 {lab=VSS}
N -20 160 -0 160 {lab=VSS}
N 40 160 60 160 {lab=SAE}
C {sky130_fd_pr/nfet_01v8.sym} 70 60 0 0 {name=M1
W=1
L=0.15
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 70 -70 0 0 {name=M2
W=1
L=0.15
nf=1
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} -70 -70 0 1 {name=M3
W=1
L=0.15
nf=1
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} -70 60 0 1 {name=M4
W=1
L=0.15
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} -200 240 0 1 {name=M6
W=1
L=0.15
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 20 -200 0 1 {name=M7
W=1
L=0.15
nf=1
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 180 240 0 0 {name=M9
W=1
L=0.15
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {lab_pin.sym} -120 -70 0 0 {name=p1 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 120 -70 2 0 {name=p2 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -30 -200 0 0 {name=p3 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -120 60 0 0 {name=p4 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 120 60 2 0 {name=p5 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -250 240 0 0 {name=p8 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 230 240 2 0 {name=p9 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -220 290 0 0 {name=p10 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 200 290 0 0 {name=p11 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/nfet_01v8.sym} 330 -160 0 1 {name=M5
W=1
L=0.15
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {lab_pin.sym} 280 -160 0 0 {name=p6 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 310 -230 0 0 {name=p7 sig_type=std_logic lab=VREF}
C {lab_pin.sym} 370 -160 2 0 {name=p12 sig_type=std_logic lab=REFE}
C {sky130_fd_pr/nfet_01v8.sym} 20 160 0 1 {name=M8
W=1
L=0.15
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {lab_pin.sym} 0 210 0 0 {name=p13 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -20 160 0 0 {name=p14 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 60 160 2 0 {name=p15 sig_type=std_logic lab=SAE}
C {lab_pin.sym} 70 -200 2 0 {name=p16 sig_type=std_logic lab=SAEB}
C {iopin.sym} -350 -450 0 0 {name=p17 lab=VDD
}
C {iopin.sym} -350 -420 0 0 {name=p18 lab=VSS
}
C {iopin.sym} -350 -390 0 0 {name=p19 lab=VREF
}
C {iopin.sym} -350 -360 0 0 {name=p20 lab=REFE
}
C {iopin.sym} -350 -330 0 0 {name=p21 lab=SAEB
}
C {iopin.sym} -350 -300 0 0 {name=p22 lab=SAE

}
C {iopin.sym} -350 -270 0 0 {name=p23 lab=BL

}
C {iopin.sym} -350 -240 0 0 {name=p24 lab=BLB

}
C {lab_pin.sym} -220 -300 0 0 {name=p25 sig_type=std_logic lab=BL
}
C {lab_pin.sym} 200 -300 0 0 {name=p26 sig_type=std_logic lab=BLB}
