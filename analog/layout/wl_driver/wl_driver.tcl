# wl_driver.tcl - WL Driver Layout (8T, mixed 1.8V + HV)
# [Input Inv] | [Level Shifter] | [HV Buffer]
# Columns: x=200 (1.8V) | x=600,1000 (LS) | x=1450 (Buffer)

proc place_dev {cellname cx cy blx_int bly_int} {
    set bx [expr {$cx + $blx_int/2.0}]
    set by [expr {$cy + $bly_int/2.0}]
    box $bx $by $bx $by
    getcell $cellname
}

proc m1 {x1 y1 x2 y2} { box $x1 $y1 $x2 $y2; paint metal1 }
proc m2 {x1 y1 x2 y2} { box $x1 $y1 $x2 $y2; paint metal2 }

proc via1_at {cx cy} {
    m1 [expr {$cx-13}] [expr {$cy-13}] [expr {$cx+13}] [expr {$cy+13}]
    m2 [expr {$cx-13}] [expr {$cy-13}] [expr {$cx+13}] [expr {$cy+13}]
    box [expr {$cx-7.5}] [expr {$cy-7.5}] [expr {$cx+7.5}] [expr {$cy+7.5}]
    paint via1
}

proc add_label {name x1 y1 x2 y2 layer portnum} {
    box $x1 $y1 $x2 $y2
    label $name 0 $layer
    port make $portnum
}

load wl_driver
box -6000 -6000 6000 6000
select area
delete
select top cell
erase

puts "=== WL Driver Layout ==="

# ============================================================
# Device placement
# ============================================================
puts "Placing devices..."

# Column 1: Input Inverter (1.8V)
place_dev dev_pfet_w100  200  300  -109 -200    ;# MP0 pfet_01v8 W=1
place_dev dev_nfet_w050  200 -300  -73  -138    ;# MN0 nfet_01v8 W=0.5

# Column 2: Level Shifter Left (HV)
place_dev dev_hv_pfet_w100  600  300  -144 -200  ;# MP1 pfet_g5v0d10v5 W=1
place_dev dev_hv_nfet_w200  600 -300  -108 -288  ;# MN1 nfet_g5v0d10v5 W=2

# Column 3: Level Shifter Right (HV)
place_dev dev_hv_pfet_w100 1000  300  -144 -200  ;# MP2 pfet_g5v0d10v5 W=1
place_dev dev_hv_nfet_w200 1000 -300  -108 -288  ;# MN2 nfet_g5v0d10v5 W=2

# Column 4: HV Buffer
place_dev dev_hv_pfet_w400 1450  350  -144 -500  ;# MP3 pfet_g5v0d10v5 W=4
place_dev dev_hv_nfet_w200 1450 -300  -108 -288  ;# MN3 nfet_g5v0d10v5 W=2

# Net assignments (LD=S, RD=D):
# MP0@(200,300):   S=VDD,  D=INB,  G=IN     pfet_01v8 W=1
# MN0@(200,-300):  S=VSS,  D=INB,  G=IN     nfet_01v8 W=0.5
# MP1@(600,300):   S=VWL,  D=Q,    G=QB     pfet_g5v0d10v5 W=1
# MN1@(600,-300):  S=VSS,  D=Q,    G=IN     nfet_g5v0d10v5 W=2
# MP2@(1000,300):  S=VWL,  D=QB,   G=Q      pfet_g5v0d10v5 W=1
# MN2@(1000,-300): S=VSS,  D=QB,   G=INB    nfet_g5v0d10v5 W=2
# MP3@(1450,350):  S=VWL,  D=OUT,  G=Q      pfet_g5v0d10v5 W=4
# MN3@(1450,-300): S=VSS,  D=OUT,  G=Q      nfet_g5v0d10v5 W=2

# ============================================================
# Power rails (met1, 14 lambda wide)
# ============================================================
puts "Routing power..."
m1 150 420 260 434     ;# VDD rail (column 1 only)
m1 520 620 1520 634    ;# VWL rail (columns 2-4)
m1 140 -470 1520 -456  ;# VSS rail (all columns)

# VDD bus (column 1): route LEFT of LS to avoid MP0.GT[185.5,214.5]x[370.5,393.5]
m1 152 295 166 420    ;# VDD bus (left of LS, width=14)
m1 152 335 189 349    ;# horizontal stub to MP0.LS

# VWL buses: from LS to VWL rail
m1 549 350 572 620    ;# column 2: MP1.LS
m1 949 350 972 620    ;# column 3: MP2.LS
m1 1399 550 1422 620  ;# column 4: MP3.LS (top at 550)

# VSS buses: from VSS rail to LS
# Column 1: route LEFT of LS to avoid MN0 gate
m1 152 -470 166 -295   ;# VSS bus (left of MN0.LS)
m1 152 -295 189 -276   ;# horizontal to MN0.LS
# Columns 2-4: direct connection (LS extends to cy-100)
m1 549 -470 572 -200   ;# column 2: MN1.LS
m1 949 -470 972 -200   ;# column 3: MN2.LS
m1 1399 -470 1422 -200 ;# column 4: MN3.LS

# ============================================================
# INB routing: MP0.RD + MN0.RD → MN2.GT
# ============================================================
puts "Routing INB..."
# INB vertical bus (column 1 drains) - shifted RIGHT to avoid IN bus overlap
# MP0.RD[210.5,233.5]x[250,350], MN0.RD[210.5,233.5]x[-325,-275]
# Gap to IN bus (x≤210): 228-210=18 >= 14
m1 228 -325 242 350

# Met2 horizontal to MN2.GT[977,1023]x[-184,-161]
via1_at 242 -130
m1 987 -184 1013 -117   ;# stub from via to MN2.GT
via1_at 1000 -130
m2 229 -143 1013 -117

# ============================================================
# IN routing: MP0.GB + MN0.GT → MN1.GT
# ============================================================
puts "Routing IN..."
# IN vertical bus (column 1 gates) - narrowed to avoid INB bus overlap
# MP0.GB[185.5,214.5]x[206.5,229.5], MN0.GT[185.5,214.5]x[-259,-236]
# Narrow to x=[186,210], gap to INB bus(x=228): 228-210=18 >= 14
m1 186 -259 210 229

# Met2 horizontal to MN1.GT[577,623]x[-184,-161]
via1_at 200 -200
m1 587 -213 613 -161   ;# stub from via to MN1.GT
via1_at 600 -200
m2 187 -213 613 -187

# ============================================================
# Q routing: MP1.RD + MN1.RD → MP2.GB + MP3.GB + MN3.GT + MN3.GB
# ============================================================
puts "Routing Q..."
# Q vertical bus (column 2 drains)
# MP1.RD[628,651]x[250,350], MN1.RD[628,651]x[-400,-200]
m1 628 -400 651 350

# Q met2 horizontal at y=160 to columns 3 and 4
via1_at 640 160
m2 627 147 1463 173

# Column 3: stub to MP2.GB[977,1023]x[206.5,229.5]
via1_at 1000 160
m1 987 147 1013 229

# Column 4: met1 strip connecting MP3.GB + MN3.GT + MN3.GB
# MP3.GB[1427,1473]x[106.5,129.5], MN3.GT[1427,1473]x[-184,-161], MN3.GB[1427,1473]x[-439,-416]
via1_at 1450 160
m1 1437 -439 1463 173

# ============================================================
# QB routing: MP2.RD + MN2.RD → MP1.GB
# ============================================================
puts "Routing QB..."
# QB vertical bus (column 3 drains)
# MP2.RD[1028,1051]x[250,350], MN2.RD[1028,1051]x[-400,-200]
m1 1028 -400 1051 350

# QB met2 horizontal at y=100 to column 2 MP1.GB
via1_at 1040 100
m2 587 87 1053 113

# Column 2: stub to MP1.GB[577,623]x[206.5,229.5]
via1_at 600 100
m1 587 87 613 229

# ============================================================
# OUT routing: MP3.RD + MN3.RD
# ============================================================
puts "Routing OUT..."
# OUT vertical bus (column 4 drains)
# MP3.RD[1478,1501]x[150,550], MN3.RD[1478,1501]x[-400,-200]
m1 1478 -400 1501 550

# ============================================================
# Port labels
# ============================================================
puts "Adding port labels..."
add_label IN   190 -100 206 -86 metal1 0
add_label OUT  1483 50 1497 64 metal1 1
add_label VDD  190 423 210 431 metal1 2
add_label VWL  1010 623 1030 631 metal2 3
add_label VSS  800 -467 820 -459 metal1 4

# ============================================================
# Save and verify
# ============================================================
puts "Saving..."
save wl_driver

puts "Running DRC..."
select top cell
drc catchup
drc check
puts "DRC count:"
drc count

puts "Flattening for extraction..."
flatten wl_driver_flat
load wl_driver_flat
select top cell

puts "Extracting (flat)..."
extract all
ext2spice lvs
ext2spice

puts "Writing GDS..."
load wl_driver
gds write wl_driver.gds

puts "=== DONE ==="
quit -noprompt
