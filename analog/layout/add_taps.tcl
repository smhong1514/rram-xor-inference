# add_taps.tcl — Add ntap/ptap to all 3 analog layouts
# IMPORTANT: box command uses LAMBDA coordinates (= internal/2 with magscale 1 2)
# .mag file coords are INTERNAL. lambda = internal / 2.

proc add_ntap_strip {x1 y1 x2 y2} {
    box $x1 $y1 $x2 $y2
    paint nsubstratencontact
    paint locali
    paint viali
}

proc add_ptap_strip {x1 y1 x2 y2} {
    box $x1 $y1 $x2 $y2
    paint psubstratepcontact
    paint locali
    paint viali
}

# ============================================================
# BL WRITE DRIVER
# ============================================================
puts "=== BL Write Driver ==="
load bl_write_driver

# Device lambda coords (internal/2):
#   pfet_w050_0 (200,600): nw (145.5,525)-(254.5,675)
#   pfet_w400_0 (600,600): nw (545.5,350)-(654.5,850)
#   pfet_w400_1 (1000,600): nw (945.5,350)-(1054.5,850)
#   pfet_w050_1 (1400,600): nw (1345.5,525)-(1454.5,675)
# VDD rail (lambda): y=880-908, x=120-1480
# VSS rail (lambda): y=-908 to -880, x=120-1480

# Remove old (wrong) nwell
box 291 700 2909 1760
erase nwell

# Remove old tap layers
box 300 1700 2900 1816
erase nsubstratencontact locali viali
box 300 -1876 2900 -1760
erase psubstratepcontact locali viali metal1

# 1. nwell merge strip (lambda): connect all pfet nwells + extend to VDD rail
box 145 350 1455 880
paint nwell

# 2. ntap strip (y=850-880, inside nwell, just below VDD rail)
add_ntap_strip 150 850 1450 880

# 3. met1 bridging ntap to VDD rail (y=850-908)
box 150 850 1450 908
paint metal1

# 4. ptap strip below VSS rail (y=-938 to -908)
add_ptap_strip 150 -938 1450 -908

# 5. met1 bridging ptap to VSS rail (y=-938 to -880)
box 150 -938 1450 -880
paint metal1

save bl_write_driver
puts "BL Write Driver taps done."

# ============================================================
# SENSE AMPLIFIER
# ============================================================
puts "=== Sense Amplifier ==="
load sense_amp

# Device lambda coords:
#   pfet_w050_0 (300,1000): nw (245.5,925)-(354.5,1075)
#   pfet_w050_1 (600,1000): nw (545.5,925)-(654.5,1075)
#   pfet_w050_2 (900,1000): nw (845.5,925)-(954.5,1075)
#   pfet_w100_0 (300,650): nw (245.5,550)-(354.5,750)
#   pfet_w100_1 (900,650): nw (845.5,550)-(954.5,750)
# VDD rail (lambda): y=1140-1154, x=200-1000
# VSS rail (lambda): y=-1220 to -1206, x=200-1000

# Remove old (wrong) nwell and taps
box 491 1100 1909 2280
erase nwell
box 500 2220 1900 2308
erase nsubstratencontact locali viali metal1
box 500 -2500 1900 -2412
erase psubstratepcontact locali viali metal1

# 1. nwell merge strip (lambda): connect all pfet nwells + extend to VDD rail
box 245 550 955 1140
paint nwell

# 2. ntap strip (y=1110-1140, inside nwell, just below VDD rail)
add_ntap_strip 250 1110 950 1140

# 3. met1 bridging ntap to VDD rail (y=1110-1154)
box 250 1110 950 1154
paint metal1

# 4. ptap strip below VSS rail (y=-1250 to -1220)
add_ptap_strip 250 -1250 950 -1220

# 5. met1 bridging ptap to VSS rail (y=-1250 to -1206)
box 250 -1250 950 -1206
paint metal1

save sense_amp
puts "Sense Amplifier taps done."

# ============================================================
# WL DRIVER
# ============================================================
puts "=== WL Driver ==="
load wl_driver

# Device lambda coords:
#   pfet_w100_0 (200,300): nw (145.5,200)-(254.5,400) → VDD
#   hv_pfet_w100_0 (600,300): nw (528,200)-(672,400) → VWL
#   hv_pfet_w100_1 (1000,300): nw (928,200)-(1072,400) → VWL
#   hv_pfet_w400_0 (1450,350): nw (1378,100)-(1522,600) → VWL
# VDD rail (lambda): y=420-434, x=150-260
# VWL rail (lambda): y=620-634, x=520-1520
# VSS rail (lambda): y=-470 to -456, x=140-1520

# --- VDD domain (column 1) ---
# 1a. nwell merge: extend pfet_w100_0 nwell up through VDD rail to ntap above
#     pfet nwell top = 400, VDD rail = 420-434, ntap = 436-466
#     CRITICAL: ntap ABOVE VDD rail to avoid MP0.GT at lambda (185.5,370.5)-(214.5,393.5)
box 145 200 255 466
paint nwell

# 2a. ntap strip ABOVE VDD rail (y=436-466)
add_ntap_strip 150 436 250 466

# 3a. met1 bridging VDD rail to ntap above (y=420-466)
box 150 420 260 466
paint metal1

# --- VWL domain (columns 2-4) ---
# 1b. nwell merge: connect all HV pfet nwells + extend to VWL rail
box 528 100 1522 620
paint nwell

# 2b. ntap strip for VWL (y=590-620, just below VWL rail)
# CRITICAL: stop at x=1420 to avoid MP3.GT met1 at lambda (1427,570.5)-(1473,593.5)
add_ntap_strip 530 590 1420 620

# 3b. met1 bridging ntap to VWL rail (y=590-634)
box 530 590 1420 634
paint metal1

# --- ptap for VSS ---
# 4. ptap strip below VSS rail (y=-500 to -470)
add_ptap_strip 150 -500 1510 -470

# 5. met1 bridging ptap to VSS rail (y=-500 to -456)
box 150 -500 1520 -456
paint metal1

save wl_driver
puts "WL Driver taps done."

puts "=== All taps added! ==="
