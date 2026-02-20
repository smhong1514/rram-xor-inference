load test_hv3
box -3000 -3000 3000 3000
select area
delete
select top cell
erase

box 0 0 0 0
getcell dev_hv_pfet_w400

save test_hv3
flatten test_hv3_flat
load test_hv3_flat
select top cell
extract all
ext2spice lvs
ext2spice

puts "=== HV PFET W400 ==="
quit -noprompt
