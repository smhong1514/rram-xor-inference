# bl_write_driver.tcl - BL Write Driver Layout (8T, all 1.8V)
# Fixed: place_dev divides bbox by 2 for magscale 1 2
# Fixed: BL uses met1 (no met2 to avoid DATA_B met2 conflict)

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

load bl_write_driver
box -5000 -5000 5000 5000
select area
delete
select top cell
erase

puts "=== BL Write Driver Layout ==="

# ============================================================
# Place devices (centers in lambda)
# ============================================================
puts "Placing devices..."

place_dev dev_pfet_w050 200 600 -109 -150     ;# MP3 DATA inv
place_dev dev_pfet_w400 600 600 -109 -500     ;# MP2 BL out
place_dev dev_pfet_w400 1000 600 -109 -500    ;# MP1 EN out
place_dev dev_pfet_w050 1400 600 -109 -150    ;# MP0 EN inv

place_dev dev_nfet_w050 200 -600 -73 -138     ;# MN3 DATA inv
place_dev dev_nfet_w400 600 -600 -73 -488     ;# MN2 BL out
place_dev dev_nfet_w400 1000 -600 -73 -488    ;# MN1 EN out
place_dev dev_nfet_w050 1400 -600 -73 -138    ;# MN0 EN inv

# Terminal positions (lambda = center + internal_offset/2):
# pfet_w400@(cx,cy): LD=[cx-33.5,cx-10.5]x[cy-200,cy+200]
#                    RD=[cx+10.5,cx+33.5]x[cy-200,cy+200]
#                    GT=[cx-14.5,cx+14.5]x[cy+220.5,cy+243.5]
#                    GB=[cx-14.5,cx+14.5]x[cy-243.5,cy-220.5]
# nfet_w400@(cx,cy): same diffs, GT=cy+[216,239], GB=cy+[-239,-216]
# pfet_w050@(cx,cy): LD=[cx-33.5,cx-10.5]x[cy-25,cy+25]
#                    RD=[cx+10.5,cx+33.5]x[cy-25,cy+25]
#                    GT=[cx-14.5,cx+14.5]x[cy+45.5,cy+68.5]
#                    GB=[cx-14.5,cx+14.5]x[cy-68.5,cy-45.5]
# nfet_w050@(cx,cy): same diffs, GT=cy+[41,64], GB=cy+[-64,-41]

# ============================================================
# Power rails
# ============================================================
puts "Routing power rails..."
m1 120 880 1480 908     ;# VDD
m1 120 -908 1480 -880   ;# VSS

# ============================================================
# VDD: PMOS right_diff(S) -> VDD via met2
# ============================================================
puts "Routing VDD/VSS..."

# MP3.S RD center=(222,600)
via1_at 222 600;  via1_at 222 894
m2 209 587 235 907

# MP1.S RD center=(1022,600)
via1_at 1022 700;  via1_at 1022 894
m2 1009 687 1035 907

# MP0.S RD center=(1422,600)
via1_at 1422 600;  via1_at 1422 894
m2 1409 587 1435 907

# ============================================================
# VSS: NMOS right_diff(S) -> VSS via met2
# ============================================================
# MN3.S RD center=(222,-600)
via1_at 222 -600;  via1_at 222 -894
m2 209 -907 235 -587

# MN1.S RD center=(1022,-600)
via1_at 1022 -700;  via1_at 1022 -894
m2 1009 -907 1035 -687

# MN0.S RD center=(1422,-600)
via1_at 1422 -600;  via1_at 1422 -894
m2 1409 -907 1435 -587

# ============================================================
# NET_P: MP2.RD(S) <-> MP1.LD(D)
# MP2.RD right edge=633.5, MP1.LD left edge=966.5
# ============================================================
puts "Routing NET_P, NET_N, BL..."
m1 633.5 560 966.5 580

# ============================================================
# NET_N: MN2.RD(S) <-> MN1.LD(D)
# ============================================================
m1 633.5 -580 966.5 -560

# ============================================================
# BL: MP2.LD(D) <-> MN2.LD(D) via met1
# MP2.LD: [566.5,589.5]x[400,800], MN2.LD: [566.5,589.5]x[-800,-400]
# Route met1 at x=[555,569] through gap, touching left_diff at y=400/-400
# Gap to gate(x=585.5): 585.5-569=16.5>=14 OK
# ============================================================
m1 555 -400 569 400

# ============================================================
# DATA_B: MP3.LD + MN3.LD -> MP2.gate + MN2.gate (via met2)
# MP3.LD: [166.5,189.5]x[575,625], MN3.LD: [166.5,189.5]x[-625,-575]
# ============================================================
puts "Routing DATA_B..."

# Extensions from offset wire to left_diffs
m1 140 580 189.5 608     ;# to MP3.LD
m1 140 -608 189.5 -580   ;# to MN3.LD

# Offset wire connecting extensions
# Gap to MP3 gate_bot(y=531.5..554.5): 580-554.5=25.5>=14 OK
# Gap to MN3 gate_top(y=-559..-536): -536-(-580)=44>=14 OK
m1 140 -580 154 580

# Via on offset wire
via1_at 147 0

# Via on MP2 gate_top center=(600,832)
via1_at 600 832

# Via on MN2 gate_bot center=(600,-827.5)
via1_at 600 -827.5

# Met2 horizontal from offset via to gate column
m2 134 -13 613 13

# Met2 vertical connecting gate vias
m2 587 -840.5 613 845

# ============================================================
# DATA: MP3.gate + MN3.gate
# MP3 gate_bot: [185.5,214.5]x[531.5,554.5]
# MN3 gate_top: [185.5,214.5]x[-559,-536]
# ============================================================
m1 190 -536 204 531.5

# ============================================================
# EN_B: MP0.LD + MN0.LD -> MP1.gate
# MP0.LD: [1366.5,1389.5]x[575,625]
# MN0.LD: [1366.5,1389.5]x[-625,-575]
# ============================================================
puts "Routing EN_B..."

m1 1340 580 1389.5 608     ;# to MP0.LD
m1 1340 -608 1389.5 -580   ;# to MN0.LD
m1 1340 -580 1354 580      ;# offset wire

# L-route to MP1 gate_bot: [985.5,1014.5]x[356.5,379.5]
# Horizontal at y=[310,324], gap to gate = 356.5-324=32.5>=14 OK
m1 1004 310 1340 324

# Vertical bridge to gate_bot
# x=[1004,1018] gap to MP1.LD(989.5): 1004-989.5=14.5>=14 OK
m1 1004 310 1018 379.5

# ============================================================
# EN: MP0.gate + MN0.gate -> MN1.gate
# MP0 gate_bot: [1385.5,1414.5]x[531.5,554.5]
# MN0 gate_top: [1385.5,1414.5]x[-559,-536]
# ============================================================
puts "Routing EN..."

# EN vertical wire
m1 1390 -536 1404 531.5

# Via on EN wire
via1_at 1397 -280

# Via on MN1 gate_top center=(1000,-372.5)
# Met1 pad [987.5,1012.5]x[-385,-360] overlaps gate_top [985.5,1014.5]x[-384,-361]
via1_at 1000 -372.5

# Met2 horizontal connecting EN to MN1 gate
m2 987 -385.5 1410 -267

# ============================================================
# Port labels
# ============================================================
puts "Adding port labels..."

add_label EN 1392 -20 1402 20 metal1 0
add_label DATA 192 -20 202 20 metal1 1
add_label BL 557 -20 567 20 metal1 2
add_label VDD 700 885 800 903 metal1 3
add_label VSS 700 -903 800 -885 metal1 4

# ============================================================
# Save and verify
# ============================================================
puts "Saving..."
save bl_write_driver

puts "Running DRC..."
select top cell
drc catchup
drc check
puts "DRC count:"
drc count

puts "Flattening for extraction..."
flatten bl_write_driver_flat
load bl_write_driver_flat
select top cell

puts "Extracting (flat)..."
extract all
ext2spice lvs
ext2spice

puts "Writing GDS..."
load bl_write_driver
gds write bl_write_driver.gds

puts "=== DONE ==="
quit -noprompt
