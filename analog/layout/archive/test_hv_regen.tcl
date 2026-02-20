# Test HV nfet
load test_hv_n
box -3000 -3000 3000 3000
select area
delete
select top cell
erase
box 0 0 0 0
getcell dev_hv_nfet_w200
save test_hv_n
flatten test_hv_n_flat
load test_hv_n_flat
select top cell
extract all
ext2spice lvs
ext2spice

# Test HV pfet w100
load test_hv_p1
box -3000 -3000 3000 3000
select area
delete
select top cell
erase
box 0 0 0 0
getcell dev_hv_pfet_w100
save test_hv_p1
flatten test_hv_p1_flat
load test_hv_p1_flat
select top cell
extract all
ext2spice lvs
ext2spice

# Test HV pfet w400
load test_hv_p4
box -3000 -3000 3000 3000
select area
delete
select top cell
erase
box 0 0 0 0
getcell dev_hv_pfet_w400
save test_hv_p4
flatten test_hv_p4_flat
load test_hv_p4_flat
select top cell
extract all
ext2spice lvs
ext2spice

puts "=== DONE ==="
quit -noprompt
