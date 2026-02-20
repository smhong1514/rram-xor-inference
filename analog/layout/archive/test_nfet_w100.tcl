load test_nfet_w100
box -2000 -2000 2000 2000
select area
delete
select top cell
erase
proc place_dev {cellname cx cy blx_int bly_int} {
    set bx [expr {$cx + $blx_int/2.0}]
    set by [expr {$cy + $bly_int/2.0}]
    box $bx $by $bx $by
    getcell $cellname
}
place_dev dev_nfet_w100 200 200 -109 -200
save test_nfet_w100
flatten test_nfet_w100_flat
load test_nfet_w100_flat
select top cell
extract all
ext2spice lvs
ext2spice
puts "=== DONE ==="
quit -noprompt
