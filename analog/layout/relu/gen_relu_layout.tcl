tech load /home/hsm/pdk_matched/share/pdk/sky130B/libs.tech/magic/sky130B.tech
drc style drc(full)
drc off
snap internal

# ============================================================
# Step 1: Generate device subcells (L=0.5um for wider linear range)
# ============================================================

# --- pfet_01v8 W=2.0 L=0.5 ---
set pars [sky130::sky130_fd_pr__pfet_01v8_defaults]
dict set pars w 2.0
dict set pars l 0.5
dict set pars nf 1
dict set pars guard 0
dict set pars full_metal 1
sky130::sky130_fd_pr__pfet_01v8_draw $pars
save dev_pfet_w200_l050
puts "Created dev_pfet_w200_l050"

# --- nfet_01v8 W=2.0 L=0.5 ---
cellname delete "(UNNAMED)"
set pars [sky130::sky130_fd_pr__nfet_01v8_defaults]
dict set pars w 2.0
dict set pars l 0.5
dict set pars nf 1
dict set pars guard 0
dict set pars full_metal 1
sky130::sky130_fd_pr__nfet_01v8_draw $pars
save dev_nfet_w200_l050
puts "Created dev_nfet_w200_l050"

# ============================================================
# Step 2: Get device bounding boxes for coordinate calculation
# ============================================================
load dev_pfet_w200_l050
select top cell
set pfet_bb [box values]
puts "PFET bbox: $pfet_bb"

load dev_nfet_w200_l050
select top cell
set nfet_bb [box values]
puts "NFET bbox: $nfet_bb"

# ============================================================
# Step 3: Create ReLU top cell with subcell placement
# ============================================================
cellname delete relu
edit

# Layout plan (2 columns, 3 rows):
#   Row 1 (top, PMOS nwell): M3 (left), M4 (right)
#   Gap: wiring space + gate contacts
#   Row 0 (bottom, NMOS): M1 (left), M2 (right)
#   Below: M5 (center, tail current)

# Spacing constants (lambda = 10nm)
set COL_SP 120      ;# column spacing between devices
set ROW_SP 200      ;# row spacing between PMOS and NMOS
set TAIL_SP 160     ;# spacing between diff pair and tail
set MARGIN 40       ;# edge margin
set RAIL_H 50       ;# power rail height
set TAP_H 50        ;# tap cell height
set NW_ENC 18       ;# nwell enclosure of pdiff

# X coordinates
set x_left $MARGIN
set x_right [expr {$x_left + 200 + $COL_SP}]  ;# rough device width ~200
set x_center [expr {($x_left + $x_right) / 2}]

# Y coordinates (bottom to top)
set y_vss_b 0
set y_vss_t [expr {$y_vss_b + $RAIL_H}]

set y_tail_b [expr {$y_vss_t + 60}]        ;# M5 tail

set y_nmos_b [expr {$y_tail_b + 350 + $TAIL_SP}] ;# M1, M2 diff pair

set y_pmos_b [expr {$y_nmos_b + 350 + $ROW_SP}]  ;# M3, M4 mirror

set y_vdd_b [expr {$y_pmos_b + 350 + 120}]
set y_vdd_t [expr {$y_vdd_b + $RAIL_H}]

set cell_w [expr {$x_right + 200 + $MARGIN}]
set cell_h $y_vdd_t

# --- Place M5 (NMOS, tail current source, center) ---
getcell dev_nfet_w200_l050 child 0 0 $x_center $y_tail_b
identify M5
puts "Placed M5 at ($x_center, $y_tail_b)"

# --- Place M1 (NMOS, VREF input, left) ---
getcell dev_nfet_w200_l050 child 0 0 $x_left $y_nmos_b
identify M1
puts "Placed M1 at ($x_left, $y_nmos_b)"

# --- Place M2 (NMOS, VBL input, right) ---
getcell dev_nfet_w200_l050 child 0 0 $x_right $y_nmos_b
identify M2
puts "Placed M2 at ($x_right, $y_nmos_b)"

# --- Place M3 (PMOS, diode-connected mirror, left) ---
getcell dev_pfet_w200_l050 child 0 0 $x_left $y_pmos_b
identify M3
puts "Placed M3 at ($x_left, $y_pmos_b)"

# --- Place M4 (PMOS, mirror output, right) ---
getcell dev_pfet_w200_l050 child 0 0 $x_right $y_pmos_b
identify M4
puts "Placed M4 at ($x_right, $y_pmos_b)"

# ============================================================
# Step 4: NWELL for PMOS region
# ============================================================
set nw_x0 [expr {$x_left - $NW_ENC - 20}]
set nw_x1 [expr {$x_right + 200 + $NW_ENC + 20}]
set nw_y0 [expr {$y_pmos_b - $NW_ENC - 20}]
set nw_y1 [expr {$y_pmos_b + 350 + $NW_ENC + 20}]
box $nw_x0 $nw_y0 $nw_x1 $nw_y1
paint nwell

# ============================================================
# Step 5: Power rails (VDD top, VSS bottom) using metal1
# ============================================================
# VSS rail
box 0 $y_vss_b $cell_w $y_vss_t
paint metal1

# VDD rail
box 0 $y_vdd_b $cell_w $y_vdd_t
paint metal1

# ============================================================
# Step 6: Save, DRC, Extract
# ============================================================
save relu
drc on
drc check
drc catchup
select top cell
drc why
drc count

# Extract for LVS
extract all
ext2spice lvs
ext2spice

# Write GDS
gds write relu.gds

puts "=== ReLU layout generation complete ==="
puts "Cell size: $cell_w x $cell_h lambda = [expr {$cell_w * 0.01}] x [expr {$cell_h * 0.01}] um"
quit -noprompt
