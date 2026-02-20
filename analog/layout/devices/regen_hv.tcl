puts "Regenerating HV devices with full_metal 0..."

# HV NFET W=2, L=0.5
load dev_hv_nfet_w200
select top cell
erase
set pars [sky130::sky130_fd_pr__nfet_g5v0d10v5_defaults]
dict set pars w 2.0
dict set pars l 0.5
dict set pars nf 1
dict set pars guard 0
dict set pars full_metal 0
sky130::sky130_fd_pr__nfet_g5v0d10v5_draw $pars
save dev_hv_nfet_w200

# HV PFET W=1, L=0.5
load dev_hv_pfet_w100
select top cell
erase
set pars [sky130::sky130_fd_pr__pfet_g5v0d10v5_defaults]
dict set pars w 1.0
dict set pars l 0.5
dict set pars nf 1
dict set pars guard 0
dict set pars full_metal 0
sky130::sky130_fd_pr__pfet_g5v0d10v5_draw $pars
save dev_hv_pfet_w100

# HV PFET W=4, L=0.5
load dev_hv_pfet_w400
select top cell
erase
set pars [sky130::sky130_fd_pr__pfet_g5v0d10v5_defaults]
dict set pars w 4.0
dict set pars l 0.5
dict set pars nf 1
dict set pars guard 0
dict set pars full_metal 0
sky130::sky130_fd_pr__pfet_g5v0d10v5_draw $pars
save dev_hv_pfet_w400

puts "=== Done regenerating ==="
quit -noprompt
