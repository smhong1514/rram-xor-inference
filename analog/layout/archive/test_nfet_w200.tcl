# Test: extract one nfet_w200 device by itself
load test_nfet_w200
box -2000 -2000 2000 2000
select area
delete
select top cell
erase

# Place one nfet_w200 at (200, 200)
proc place_dev {cellname cx cy blx_int bly_int} {
    set bx [expr {$cx + $blx_int/2.0}]
    set by [expr {$cy + $bly_int/2.0}]
    box $bx $by $bx $by
    getcell $cellname
}

place_dev dev_nfet_w200 200 200 -109 -288

# Add simple met1 labels on G, S, D
box 185.5 82 214.5 88
label G_TEST 0 metal1
port make 0

box 166.5 100 189.5 300
label S_TEST 0 metal1
port make 1

box 210.5 100 233.5 300
label D_TEST 0 metal1
port make 2

save test_nfet_w200

# Flatten and extract
flatten test_nfet_w200_flat
load test_nfet_w200_flat
select top cell
extract all
ext2spice lvs
ext2spice

puts "=== DONE ==="
quit -noprompt
