# add_taps_wl.tcl — Add ntap/ptap to WL Driver only
# Fresh layout from wl_driver.tcl, no old taps to erase
# IMPORTANT: box command uses LAMBDA coordinates (= internal/2 with magscale 1 2)

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

puts "=== WL Driver Taps ==="
load wl_driver

# Device lambda coords:
#   pfet_w100_0 (200,300): nw (145.5,200)-(254.5,400) → VDD domain
#   hv_pfet_w100_0 (600,300): nw (528,200)-(672,400) → VWL domain
#   hv_pfet_w100_1 (1000,300): nw (928,200)-(1072,400) → VWL domain
#   hv_pfet_w400_0 (1450,350): nw (1378,100)-(1522,600) → VWL domain
# VDD rail (lambda): y=420-434, x=150-260
# VWL rail (lambda): y=620-634, x=520-1520
# VSS rail (lambda): y=-470 to -456, x=140-1520
# CRITICAL: MP0.GT (gate top contact) at lambda [185.5,214.5]x[370.5,393.5]
#   → ntap MUST be ABOVE VDD rail to avoid shorting VDD to IN (gate)

# --- VDD domain (column 1) ---
# 1a. nwell merge: extend pfet_w100_0 nwell up THROUGH VDD rail to ntap above
#     pfet nwell top = 400, VDD rail = 420-434, ntap = 436-466
box 145 200 255 466
paint nwell

# 2a. ntap strip ABOVE VDD rail (y=436-466)
add_ntap_strip 150 436 250 466

# 3a. met1 bridging VDD rail down to ntap above (y=420-466)
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
# Same x limit: VWL buses at x=549-572, 949-972, 1399-1422 provide connectivity
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
