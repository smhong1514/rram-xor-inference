load test_hv
box -3000 -3000 3000 3000
select area
delete
select top cell
erase

# Place one HV nfet_w200
box 0 0 0 0
getcell dev_hv_nfet_w200

save test_hv
flatten test_hv_flat
load test_hv_flat
select top cell
extract all
ext2spice lvs
ext2spice

puts "=== HV NFET W200 extraction ==="
quit -noprompt
