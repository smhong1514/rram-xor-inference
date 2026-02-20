load test_extract2
select top cell
# Flatten the hierarchy
flatten test_flat
load test_flat
select top cell
save test_flat
extract all
ext2spice lvs
ext2spice
quit -noprompt
