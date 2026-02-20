tech load $env(PDK_ROOT)/sky130B/libs.tech/magic/sky130B.tech
drc off
snap internal

# Flatten the hierarchical cell
load wl_driver
flatten wl_driver_flat
load wl_driver_flat

# Use getnode to find which net is at specific locations
puts "=== getnode at key locations ==="

# Col0 drain met1 bus should be around x=58..87
box 70 500 71 501
set n1 [getnode]
puts "Col0 drain bus (70,500): $n1"

# Col1 drain met1 bus should be around x=424..453
box 440 500 441 501
set n2 [getnode]
puts "Col1 drain bus (440,500): $n2"

# Check if there's anything connecting them in the gap
# The gap is Y_GAP_B to Y_GAP_T

# Check various y levels through the gap
puts "\n=== Scanning met1 horizontally through the gap at y=500 ==="
puts "(looking for met1 bridging Col0 drain to Col1 drain)"
for {set x 58} {$x <= 460} {incr x 5} {
    box $x 500 [expr {$x+1}] 501
    set n [getnode]
    if {$n != ""} {
        puts "  x=$x y=500: node=$n"
    }
}

# Check at the polycont level
puts "\n=== Scanning at polycont level y=470 ==="
for {set x 0} {$x <= 460} {incr x 5} {
    box $x 470 [expr {$x+1}] 471
    set n [getnode]
    if {$n != ""} {
        puts "  x=$x y=470: node=$n"
    }
}

# Check at met2 track level
puts "\n=== Scanning met2 at track Y1 level ==="
for {set x 0} {$x <= 780} {incr x 10} {
    box $x 486 [expr {$x+1}] 487
    set n [getnode]
    if {$n != ""} {
        puts "  x=$x y=486: node=$n"
    }
}

quit -noprompt
