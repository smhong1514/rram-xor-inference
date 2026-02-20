# sense_amp.tcl - Sense Amplifier Layout (10T StrongARM, all 1.8V)
# Column layout: Left(Q-side x=300) | Center(x=600) | Right(QB-side x=900)

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

load sense_amp
box -6000 -6000 6000 6000
select area
delete
select top cell
erase

puts "=== Sense Amplifier Layout ==="

# ============================================================
# Device placement
# ============================================================
puts "Placing devices..."

place_dev dev_pfet_w050 300  1000 -109 -150    ;# MP3 precharge Q
place_dev dev_pfet_w050 600  1000 -109 -150    ;# MP5 equalize
place_dev dev_pfet_w050 900  1000 -109 -150    ;# MP4 precharge QB

place_dev dev_pfet_w100 300  650  -109 -200    ;# MP1 latch Q
place_dev dev_pfet_w100 900  650  -109 -200    ;# MP2 latch QB

place_dev dev_nfet_w100 300  0    -109 -200    ;# MN1 latch Q
place_dev dev_nfet_w100 900  0    -109 -200    ;# MN2 latch QB

place_dev dev_nfet_w200 300  -500 -109 -288    ;# MN3 input INP
place_dev dev_nfet_w200 900  -500 -109 -288    ;# MN4 input INN

place_dev dev_nfet_w200 600  -1000 -109 -288   ;# MN0 tail

# Net assignments (LD=S, RD=D in subcell):
# MP3@(300,1000):  S=VDD, D=Q,    G=SAE
# MP4@(900,1000):  S=VDD, D=QB,   G=SAE
# MP5@(600,1000):  S=Q,   D=QB,   G=SAE
# MP1@(300,650):   S=VDD, D=Q,    G=QB
# MP2@(900,650):   S=VDD, D=QB,   G=Q
# MN1@(300,0):     S=FN1, D=Q,    G=QB
# MN2@(900,0):     S=FN2, D=QB,   G=Q
# MN3@(300,-500):  S=FN1, D=TAIL, G=INP
# MN4@(900,-500):  S=FN2, D=TAIL, G=INN
# MN0@(600,-1000): S=VSS, D=TAIL, G=SAE

# ============================================================
# Power rails (met1, 14 lambda wide)
# ============================================================
puts "Routing power..."
m1 200 1140 1000 1154   ;# VDD rail
m1 200 -1220 1000 -1206 ;# VSS rail

# VDD left bus: x=[252,271] overlaps MP3.LD[266.5,289.5] and MP1.LD[266.5,289.5]
# Gap to gate(285.5) = 14.5. OK.
m1 252 600 271 1140

# VDD right bus: x=[852,871] overlaps MP4.LD[866.5,889.5] and MP2.LD[866.5,889.5]
# Gap to gate(885.5) = 14.5. OK.
m1 852 600 871 1140

# VSS bus: x=[552,571] overlaps MN0.LD[566.5,589.5]
m1 552 -1220 571 -900

# ============================================================
# FN1 bus: MN1.LD[266.5,289.5]x[-50,50] <-> MN3.LD[266.5,289.5]x[-600,-400]
# ============================================================
puts "Routing FN1, FN2..."
m1 252 -600 271 50

# FN2 bus: MN2.LD[866.5,889.5]x[-50,50] <-> MN4.LD[866.5,889.5]x[-600,-400]
m1 852 -600 871 50

# ============================================================
# TAIL: MN3.RD + MN4.RD + MN0.RD
# ============================================================
puts "Routing TAIL..."
# Horizontal met1 from MN3.RD to before FN2 bus
m1 310.5 -507 838 -493

# Met2 bridge over FN2 bus
via1_at 825 -500
via1_at 922 -500
m2 812 -513 935 -487

# Vertical met1 to MN0.RD (x=[629,643], gap to MN0 gate at 614.5 = 14.5)
m1 629 -1100 643 -493

# ============================================================
# Q routing (met2)
# ============================================================
puts "Routing Q..."
via1_at 322 1000   ;# MP3.RD
via1_at 322 650    ;# MP1.RD
via1_at 322 0      ;# MN1.RD
via1_at 578 1000   ;# MP5.LD

# Q spine (met2 vertical, stops at y=663 to avoid SAE met2 at y=930+)
m2 309 -13 335 663

# Q met1 bridge from spine to precharge (right of SAE via pad[287,313])
# Bridge at x=[328,342], gap to SAE pad = 328-313 = 15 >= 14
m1 328 663 342 987

# Q precharge horizontal at y=1000 (separate met2 segment)
m2 309 987 591 1013

# Q cross-coupling vias on right column gates
via1_at 873 568     ;# MP2.GB
via1_at 873 80      ;# MN2.GT
m2 860 67 886 581   ;# cross-coupling vertical

# Q horizontal to right column
m2 309 287 886 313

# ============================================================
# QB routing (met2)
# ============================================================
puts "Routing QB..."
via1_at 922 1000   ;# MP4.RD
via1_at 922 650    ;# MP2.RD
via1_at 922 0      ;# MN2.RD
via1_at 622 1000   ;# MP5.RD

# QB spine (met2 vertical, stops at y=663)
m2 909 -13 935 663

# QB met1 bridge from spine to precharge (right of SAE via pad[887,913])
# Bridge at x=[928,942], gap to SAE pad = 928-913 = 15 >= 14
m1 928 663 942 987

# QB precharge horizontal at y=1000 (separate met2 segment)
m2 609 987 935 1013

# QB cross-coupling to left column gates
# Via LEFT of VDD bus: x=225 (pad [212,238], gap to VDD bus[252]=14)
via1_at 225 568
m1 238 561 285.5 575   ;# stub to MP1.GB

via1_at 225 80
m1 238 73 285.5 87     ;# stub to MN1.GT

m2 212 67 238 581      ;# cross-coupling vertical

# QB horizontal: must cross Q spine met2 [309,335] via met1 transition
m2 212 187 295 213     ;# segment 1: left of Q spine (gap to 309 = 14)
via1_at 282 200        ;# transition to met1
m1 269 193 349 207     ;# met1 through Q spine area (Q spine is met2)
via1_at 349 200        ;# transition back to met2
m2 336 187 846 213     ;# segment 2a: right of Q spine to before Q cross-coupling [860,886]

# QB must also cross Q cross-coupling vertical met2 [860,886]x[67,581]
via1_at 833 200        ;# transition to met1
m1 820 193 926 207     ;# met1 through Q cross-coupling area (Q xc is met2)
via1_at 913 200        ;# transition back to met2
m2 900 187 935 213     ;# segment 2b: after Q cross-coupling to QB spine

# ============================================================
# SAE routing
# ============================================================
puts "Routing SAE..."
via1_at 300 943    ;# MP3.GB
via1_at 600 943    ;# MP5.GB
via1_at 900 943    ;# MP4.GB

m2 287 930 913 956 ;# SAE horizontal

# SAE vertical to MN0.GT: must cross Q(y=300) and QB(y=200) met2 horizontals
m2 587 327 613 956 ;# met2 down to above Q crossing

via1_at 600 340    ;# transition to met1
m1 587 160 613 327 ;# met1 through crossing zone
via1_at 600 160    ;# transition back to met2

via1_at 600 -872   ;# MN0.GT
m2 587 -885 613 147 ;# met2 from below crossing to MN0.GT

# ============================================================
# INP, INN
# ============================================================
puts "Routing INP, INN..."
# INP: extend MN3 gate RIGHT (away from FN1 bus)
m1 314.5 -384 360 -361

# INN: extend MN4 gate RIGHT (away from FN2 bus)
m1 914.5 -384 960 -361

# ============================================================
# Port labels
# ============================================================
puts "Adding port labels..."
add_label SAE 592 938 608 950 metal2 0
add_label INP 340 -380 356 -365 metal1 1
add_label INN 940 -380 956 -365 metal1 2
add_label Q 315 400 331 416 metal2 3
add_label QB 915 400 931 416 metal2 4
add_label VDD 550 1143 650 1151 metal1 5
add_label VSS 550 -1217 650 -1209 metal1 6

# ============================================================
# Save and verify
# ============================================================
puts "Saving..."
save sense_amp

puts "Running DRC..."
select top cell
drc catchup
drc check
puts "DRC count:"
drc count

puts "Flattening for extraction..."
flatten sense_amp_flat
load sense_amp_flat
select top cell

puts "Extracting (flat)..."
extract all
ext2spice lvs
ext2spice

puts "Writing GDS..."
load sense_amp
gds write sense_amp.gds

puts "=== DONE ==="
quit -noprompt
