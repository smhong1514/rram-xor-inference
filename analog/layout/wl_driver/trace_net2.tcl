tech load $env(PDK_ROOT)/sky130B/libs.tech/magic/sky130B.tech
drc off
snap internal
load wl_driver

# Check what layers exist at Col0 drain area 
puts "=== Checking layers at Col0 drain bus ==="
box 70 400 71 401
set aw [what -all]
puts "All layers at (70,400): $aw"

box 60 400 61 401
set aw2 [what -all]
puts "All layers at (60,400): $aw2"

box 75 400 76 401
set aw3 [what -all]
puts "All layers at (75,400): $aw3"

# Check drain bus extent by looking at met1 at various x positions
puts "\n=== Met1 present at y=400, various x ==="
foreach x {50 55 58 60 65 70 75 80 85 87 90 100 120 150 200 250 300 350 400 420 424 430 440 450 453 460} {
    box $x 400 [expr {$x+1}] 401
    set layers [cellname list exists]
    catch {
        set tile [goto metal1 $x 400]
    }
}

# Let me just use the extraction directly
# First, check if we have wl_driver_flat.mag
puts "\n=== Loading flat layout ==="
flatten -dobox wl_driver_flat wl_driver
load wl_driver_flat

# Check met1 at various points
puts "=== Met1 check at y=500 (in gap), various x positions ==="
foreach x {50 55 58 60 65 70 75 80 85 87 90 95 100 200 300 400 420 424 430 440 450 453 460} {
    box $x 500 [expr {$x+1}] 501
    set what_here [what]
    if {$what_here != ""} {
        puts "  x=$x: $what_here"
    }
}

# Check met1 at y=300 (below gap, in NFET diff area)
puts "\n=== Met1 check at y=300 (NFET area), various x ==="
foreach x {50 55 58 60 65 70 75 80 85 87 90 95 100 200 300 400 420 424 430 440 450 453 460} {
    box $x 300 [expr {$x+1}] 301
    set what_here [what]
    if {$what_here != ""} {
        puts "  x=$x: $what_here"
    }
}

quit -noprompt
