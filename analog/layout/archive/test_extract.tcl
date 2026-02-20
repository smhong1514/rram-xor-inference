# Minimal test: place one pfet_w050, connect only gate, check extraction
load test_extract
select top cell
erase

# Place device at center (200, 200)
box [expr {200-109}] [expr {200-150}] [expr {200-109}] [expr {200-150}]
getcell dev_pfet_w050

# Test 1: just a wire on gate_bot
# gate_bot: x=[171,229], y=[63,109] (absolute = center+relative: [200-29,200+29],[200-137,200-91])
box 185 -100 215 63
paint metal1

puts "=== Test extract ==="
save test_extract
extract all
ext2spice lvs
ext2spice

# Now print the SPICE file
puts "--- SPICE output ---"

quit -noprompt
