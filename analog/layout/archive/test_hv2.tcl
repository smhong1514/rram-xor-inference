load test_hv2
box -3000 -3000 3000 3000
select area
delete
select top cell
erase

box 0 0 0 0
getcell dev_hv_pfet_w100

save test_hv2
flatten test_hv2_flat
load test_hv2_flat
select top cell
extract all
ext2spice lvs
ext2spice

puts "=== HV PFET W100 ==="
quit -noprompt
