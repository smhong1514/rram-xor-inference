load test_extract2
select top cell
erase
box 91 50 91 50
getcell dev_pfet_w050
# Wire overlapping gate_bot
box 185 -100 215 100
paint metal1
save test_extract2
extract all
ext2spice lvs
ext2spice
quit -noprompt
