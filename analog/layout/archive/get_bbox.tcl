# get_bbox.tcl - Get bounding boxes and metal1 terminal info for all device subcells

proc get_cell_info {cellname} {
    load $cellname
    select top cell
    set bb [box values]
    puts "CELL: $cellname"
    puts "  BOX: $bb"

    # Reset and get actual cell area
    select clear
    box 0 0 0 0

    # Select only metal1
    select area metal1
    set m1bb [box values]
    puts "  M1_SEL_BOX: $m1bb"
    select clear
    puts "---"
}

foreach cell {dev_nfet_w050 dev_pfet_w050 dev_nfet_w100 dev_pfet_w100 dev_nfet_w200 dev_nfet_w400 dev_pfet_w400 dev_hv_pfet_w100 dev_hv_nfet_w200 dev_hv_pfet_w400} {
    if {[file exists ${cell}.mag]} {
        get_cell_info $cell
    }
}

quit -noprompt
