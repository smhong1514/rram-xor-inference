tech load $env(PDK_ROOT)/sky130B/libs.tech/magic/sky130B.tech
drc off
snap internal

load wl_driver
flatten wl_driver_flat
load wl_driver_flat

# Try to extract and check connectivity
puts "=== Extracting flat cell ==="
extract all
ext2spice lvs
ext2spice

# Check what paint exists between Col0 drain and Col1 drain
# by using "select area" which selects all paint in the box
puts "\n=== Checking paint at key locations ==="

# Check Col0 drain bus met1 area
select clear
box 58 400 87 401
select area metal1
set sb [select bbox]
puts "Col0 drain met1 at y=400: bbox=$sb"

# Check Col1 drain bus met1 area 
select clear
box 424 400 453 401
select area metal1
set sb2 [select bbox]
puts "Col1 drain met1 at y=400: bbox=$sb2"

# Key: check if any met1 exists between Col0 drain (x=87) and Col1 drain (x=424)
# at various y levels in the gap region (Y_GAP_B=322 to Y_GAP_T=622)
puts "\n=== Searching for bridging met1 between x=87 and x=424 ==="
foreach y {340 360 380 400 420 440 460 470 480 490 500 510 520 540 560 580 600} {
    select clear
    box 87 $y 424 [expr {$y+2}]
    select area metal1
    set sb [select bbox]
    if {$sb != "0 0 0 0" && $sb != ""} {
        puts "  met1 found at y=$y: bbox=$sb"
    }
}

# Also check locali (li1)
puts "\n=== Searching for bridging locali between x=87 and x=424 ==="
foreach y {340 360 380 400 420 440 460 470 480 490 500 510 520 540 560 580 600} {
    select clear
    box 87 $y 424 [expr {$y+2}]
    select area locali
    set sb [select bbox]
    if {$sb != "0 0 0 0" && $sb != ""} {
        puts "  li1 found at y=$y: bbox=$sb"
    }
}

# Check poly
puts "\n=== Searching for bridging poly between x=87 and x=424 ==="
foreach y {340 360 380 400 420 440 460 470 480 490 500 510 520 540 560 580 600} {
    select clear
    box 87 $y 424 [expr {$y+2}]
    select area polysilicon
    set sb [select bbox]
    if {$sb != "0 0 0 0" && $sb != ""} {
        puts "  poly found at y=$y: bbox=$sb"
    }
}

quit -noprompt
