# probe_devices.tcl - Get bounding box and metal1 terminal info for all device subcells
# Usage: magic -dnull -noconsole -rcfile ... < probe_devices.tcl

proc probe_cell {cellname} {
    puts "=== $cellname ==="
    load $cellname
    select top cell
    set bbox [box values]
    puts "BBOX: $bbox"

    # Get metal1 regions
    select top cell
    set m1box [select area metal1]
    puts "Metal1 selection: $m1box"

    # Just dump the bbox
    box 0 0 0 0
    select clear
    select top cell
    set bb [property FIXED_BBOX]
    puts "FIXED_BBOX: $bb"

    # Get cell bbox
    cellname list allcells
    puts "---"
}

# All devices we need for the layout
foreach cell {dev_nfet_w050 dev_pfet_w050 dev_nfet_w100 dev_pfet_w100 dev_nfet_w200 dev_nfet_w400 dev_pfet_w400 dev_hv_pfet_w100 dev_hv_nfet_w200 dev_hv_pfet_w400} {
    if {[file exists ${cell}.mag]} {
        probe_cell $cell
    } else {
        puts "=== $cell === NOT FOUND"
    }
}

quit -noprompt
