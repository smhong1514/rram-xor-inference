tech load $env(PDK_ROOT)/sky130B/libs.tech/magic/sky130B.tech
drc style drc(full)
snap internal

# Generate pfet W=2.0 L=0.5
set pars [sky130::sky130_fd_pr__pfet_01v8_defaults]
dict set pars w 2.0
dict set pars l 0.5
dict set pars nf 1
dict set pars guard 0
dict set pars full_metal 1
sky130::sky130_fd_pr__pfet_01v8_draw $pars
save dev_pfet_w200_l050
puts "Created dev_pfet_w200_l050"
select top cell
set bb [box values]
puts "PFET bbox: $bb"

# Generate nfet W=2.0 L=0.5
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
select top cell
set bb [box values]
puts "NFET bbox: $bb"

quit -noprompt
