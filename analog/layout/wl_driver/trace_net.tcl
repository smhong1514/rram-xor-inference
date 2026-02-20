tech load $env(PDK_ROOT)/sky130B/libs.tech/magic/sky130B.tech
gds read wl_driver.gds
load wl_driver_flat
flatten wl_driver_flat
load wl_driver_flat

# Move cursor to Col0 drain area at ndiff (x=57, y=213)
box 70 250 71 251
select area metal1
set bbox [box values]
puts "BOX at Col0 drain: $bbox"
puts "--- Selecting net at Col0 drain met1 ---"
select clear
box 70 250 71 251
select chunk metal1
set bbox_chunk [box values]
puts "Chunk bbox: $bbox_chunk"

# Try selecting at met1 on drain bus
select clear
box 70 500 71 501
set what [what]
puts "What at (70,500): $what"

select clear
box 70 500 71 501
select chunk
puts "Chunk from (70,500):"
set cb [box values]
puts "  box: $cb"

quit -noprompt
