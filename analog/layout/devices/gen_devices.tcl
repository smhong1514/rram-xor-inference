# gen_devices.tcl - Generate missing device subcells for analog layout
# Usage: magic -dnull -noconsole -rcfile $PDK_ROOT/sky130B/libs.tech/magic/sky130B.magicrc < gen_devices.tcl

# --- pfet_01v8 W=1.0 L=0.15 ---
set pars [sky130::sky130_fd_pr__pfet_01v8_defaults]
dict set pars w 1.0
dict set pars l 0.15
dict set pars nf 1
dict set pars guard 0
dict set pars full_metal 1
sky130::sky130_fd_pr__pfet_01v8_draw $pars
save dev_pfet_w100
puts "Created dev_pfet_w100"

# --- nfet_01v8 W=1.0 L=0.15 ---
cellname delete "(UNNAMED)"
set pars [sky130::sky130_fd_pr__nfet_01v8_defaults]
dict set pars w 1.0
dict set pars l 0.15
dict set pars nf 1
dict set pars guard 0
dict set pars full_metal 1
sky130::sky130_fd_pr__nfet_01v8_draw $pars
save dev_nfet_w100
puts "Created dev_nfet_w100"

# --- nfet_01v8 W=2.0 L=0.15 ---
cellname delete "(UNNAMED)"
set pars [sky130::sky130_fd_pr__nfet_01v8_defaults]
dict set pars w 2.0
dict set pars l 0.15
dict set pars nf 1
dict set pars guard 0
dict set pars full_metal 1
sky130::sky130_fd_pr__nfet_01v8_draw $pars
save dev_nfet_w200
puts "Created dev_nfet_w200"

# --- pfet_g5v0d10v5 W=1.0 L=0.5 (HV) ---
cellname delete "(UNNAMED)"
set pars [sky130::sky130_fd_pr__pfet_g5v0d10v5_defaults]
dict set pars w 1.0
dict set pars l 0.5
dict set pars nf 1
dict set pars guard 0
dict set pars full_metal 1
sky130::sky130_fd_pr__pfet_g5v0d10v5_draw $pars
save dev_hv_pfet_w100
puts "Created dev_hv_pfet_w100"

# --- nfet_g5v0d10v5 W=2.0 L=0.5 (HV) ---
cellname delete "(UNNAMED)"
set pars [sky130::sky130_fd_pr__nfet_g5v0d10v5_defaults]
dict set pars w 2.0
dict set pars l 0.5
dict set pars nf 1
dict set pars guard 0
dict set pars full_metal 1
sky130::sky130_fd_pr__nfet_g5v0d10v5_draw $pars
save dev_hv_nfet_w200
puts "Created dev_hv_nfet_w200"

# --- pfet_g5v0d10v5 W=4.0 L=0.5 (HV) ---
cellname delete "(UNNAMED)"
set pars [sky130::sky130_fd_pr__pfet_g5v0d10v5_defaults]
dict set pars w 4.0
dict set pars l 0.5
dict set pars nf 1
dict set pars guard 0
dict set pars full_metal 1
sky130::sky130_fd_pr__pfet_g5v0d10v5_draw $pars
save dev_hv_pfet_w400
puts "Created dev_hv_pfet_w400"

puts "=== All 6 device subcells generated ==="
quit -noprompt
