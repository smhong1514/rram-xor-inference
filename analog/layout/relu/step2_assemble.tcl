tech load /home/hsm/pdk_matched/share/pdk/sky130B/libs.tech/magic/sky130B.tech
drc style drc(full)
drc off
snap internal

# Device bbox (from step1): -144 to 144 x, -300 to 300 y (internal units)
# Device size: 288 x 600 internal

# ============================================================
# Create fresh relu cell
# ============================================================
cellname delete relu 2>/dev/null
cellname create relu
load relu
edit

# ============================================================
# Layout plan (internal units, 1 int = 5nm):
#   Row0 (bottom): M5 (tail NMOS)
#   Row1 (middle): M1 (left, NMOS), M2 (right, NMOS)
#   Row2 (top):    M3 (left, PMOS), M4 (right, PMOS)
# ============================================================
# Column spacing: 150 int (75 lambda)
# Row spacing: 250 int (125 lambda)
# Margins: 200 int

set DEV_W 288
set DEV_H 600
set COL_SP 150
set ROW_SP 250
set MARGIN_X 200
set MARGIN_Y 300

# X positions for LL corner of each device
set X_LEFT $MARGIN_X
set X_RIGHT [expr {$MARGIN_X + $DEV_W + $COL_SP}]
set X_M5 [expr {($X_LEFT + $X_RIGHT + $DEV_W) / 2 - $DEV_W / 2}]

# Y positions for LL corner of each device
set Y_M5 $MARGIN_Y
set Y_NMOS [expr {$Y_M5 + $DEV_H + $ROW_SP}]
set Y_PMOS [expr {$Y_NMOS + $DEV_H + $ROW_SP}]

set CELL_W [expr {$X_RIGHT + $DEV_W + $MARGIN_X}]
set CELL_H [expr {$Y_PMOS + $DEV_H + $MARGIN_Y}]

puts "Layout: ${CELL_W}x${CELL_H} internal = [expr {$CELL_W * 0.005}]x[expr {$CELL_H * 0.005}] um"
puts "M5 at ($X_M5, $Y_M5)"
puts "M1 at ($X_LEFT, $Y_NMOS), M2 at ($X_RIGHT, $Y_NMOS)"
puts "M3 at ($X_LEFT, $Y_PMOS), M4 at ($X_RIGHT, $Y_PMOS)"

# ============================================================
# Place device subcells using getcell
# ============================================================
# M5 - tail current source (NMOS, center-bottom)
box $X_M5 $Y_M5 [expr {$X_M5 + 1}] [expr {$Y_M5 + 1}]
getcell dev_nfet_w200_l050 child ll
puts "Placed M5"

# M1 - VREF input (NMOS, left-middle)
box $X_LEFT $Y_NMOS [expr {$X_LEFT + 1}] [expr {$Y_NMOS + 1}]
getcell dev_nfet_w200_l050 child ll
puts "Placed M1"

# M2 - VBL input (NMOS, right-middle)
box $X_RIGHT $Y_NMOS [expr {$X_RIGHT + 1}] [expr {$Y_NMOS + 1}]
getcell dev_nfet_w200_l050 child ll
puts "Placed M2"

# M3 - mirror diode (PMOS, left-top)
box $X_LEFT $Y_PMOS [expr {$X_LEFT + 1}] [expr {$Y_PMOS + 1}]
getcell dev_pfet_w200_l050 child ll
puts "Placed M3"

# M4 - mirror output (PMOS, right-top)
box $X_RIGHT $Y_PMOS [expr {$X_RIGHT + 1}] [expr {$Y_PMOS + 1}]
getcell dev_pfet_w200_l050 child ll
puts "Placed M4"

# ============================================================
# Flatten everything (so we can wire freely)
# ============================================================
select top cell
flatten relu_flat
load relu_flat
edit

# ============================================================
# NWELL for PMOS region
# ============================================================
set NW_ENC 40
set nw_x0 [expr {$X_LEFT - $NW_ENC}]
set nw_x1 [expr {$X_RIGHT + $DEV_W + $NW_ENC}]
set nw_y0 [expr {$Y_PMOS - $NW_ENC}]
set nw_y1 [expr {$Y_PMOS + $DEV_H + $NW_ENC}]
box $nw_x0 $nw_y0 $nw_x1 $nw_y1
paint nwell

# ============================================================
# Substrate taps
# ============================================================
# PTAP (VSS) - below NMOS region
set ptap_y0 [expr {$MARGIN_Y - 120}]
set ptap_y1 [expr {$MARGIN_Y - 40}]
set tap_x0 40
set tap_x1 [expr {$CELL_W - 40}]
box $tap_x0 $ptap_y0 $tap_x1 $ptap_y1
paint psubstratepcontact
box [expr {$tap_x0 - 16}] [expr {$ptap_y0 - 16}] [expr {$tap_x1 + 16}] [expr {$ptap_y1 + 16}]
paint locali

# NTAP (VDD) - above PMOS region
set ntap_y0 [expr {$Y_PMOS + $DEV_H + 40}]
set ntap_y1 [expr {$ntap_y0 + 80}]
box $tap_x0 $ntap_y0 $tap_x1 $ntap_y1
paint nsubstratencontact
box [expr {$tap_x0 - 16}] [expr {$ntap_y0 - 16}] [expr {$tap_x1 + 16}] [expr {$ntap_y1 + 16}]
paint locali

# Extend nwell to cover NTAP
box $nw_x0 $nw_y0 $nw_x1 [expr {$ntap_y1 + 40}]
paint nwell

# ============================================================
# Power rails (met1)
# ============================================================
set rail_h 80
set vss_y0 [expr {$ptap_y0 - $rail_h - 20}]
set vss_y1 [expr {$ptap_y0 - 20}]
set vdd_y0 [expr {$ntap_y1 + 20}]
set vdd_y1 [expr {$vdd_y0 + $rail_h}]

# VSS rail
box 0 $vss_y0 $CELL_W $vss_y1
paint metal1

# VDD rail
box 0 $vdd_y0 $CELL_W $vdd_y1
paint metal1

# MCON from taps to rails
for {set x [expr {$tap_x0 + 10}]} {$x < [expr {$tap_x1 - 34}]} {incr x 72} {
    # ptap to VSS
    box $x $ptap_y0 [expr {$x + 34}] [expr {$ptap_y0 + 34}]
    paint mcon
    # ntap to VDD
    box $x $ntap_y0 [expr {$x + 34}] [expr {$ntap_y0 + 34}]
    paint mcon
}

# Connect ptap to VSS rail (met1 strip)
box $tap_x0 $vss_y1 $tap_x1 $ptap_y1
paint metal1

# Connect ntap to VDD rail (met1 strip)
box $tap_x0 $ntap_y0 $tap_x1 $vdd_y0
paint metal1

# ============================================================
# Labels & Ports
# ============================================================
# For now just add basic labels on power rails
box 0 $vss_y0 $CELL_W $vss_y1
label VSS s metal1
port make 6

box 0 $vdd_y0 $CELL_W $vdd_y1
label VDD s metal1
port make 5

# Signal pins will be added after we identify exact met1/met2 pad locations
# For now, label areas around device gate contacts

# ============================================================
# Save + DRC + Extract + GDS
# ============================================================
save relu_flat
drc on
drc check
drc catchup
select top cell
drc why
drc count total

extract all
ext2spice lvs
ext2spice
gds write relu.gds

puts "=== ReLU assembly complete ==="
puts "Cell: $CELL_W x [expr {$vdd_y1}] internal"
quit -noprompt
