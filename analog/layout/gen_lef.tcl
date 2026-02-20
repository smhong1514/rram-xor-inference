# gen_lef.tcl - Generate LEF files for 3 analog blocks
# Run from: ~/rram_openlane/analog/layout/
# Usage: magic -noconsole -dnull -rcfile $PDK_ROOT/sky130B/libs.tech/magic/sky130B.magicrc < gen_lef.tcl

proc set_port_props {label_name class use llx lly urx ury} {
    select clear
    box $llx $lly $urx $ury
    select area label
    port class $class
    port use $use
    puts "  Port $label_name: class=$class, use=$use"
}

proc gen_lef_for_block {dir cell port_list} {
    puts "=== Generating LEF for $cell ==="
    cd $dir
    load $cell

    foreach {name class use llx lly urx ury} $port_list {
        set_port_props $name $class $use $llx $lly $urx $ury
    }

    lef write ${cell}.lef
    save
    puts "  Written: ${cell}.lef"
    puts ""
}

set base_dir [pwd]

# -------------------------------------------------------
# BL Write Driver (5 ports, all metal1)
# .mag internal coords / 2 = lambda coords for box
# -------------------------------------------------------
gen_lef_for_block "$base_dir/bl_write_driver" bl_write_driver {
    EN      input  signal  1392 -20 1402 20
    DATA    input  signal   192 -20  202 20
    BL      output signal   557 -20  567 20
    VDD     inout  power    700 885  800 903
    VSS     inout  ground   700 -903 800 -885
}

# -------------------------------------------------------
# Sense Amplifier (7 ports, metal1 + metal2)
# -------------------------------------------------------
cd $base_dir
gen_lef_for_block "$base_dir/sense_amp" sense_amp {
    SAE     input  signal   592  938  608  950
    INP     input  signal   340 -380  356 -365
    INN     input  signal   940 -380  956 -365
    Q       output signal   315  400  331  416
    QB      output signal   915  400  931  416
    VDD     inout  power    550 1143  650 1151
    VSS     inout  ground   550 -1217 650 -1209
}

# -------------------------------------------------------
# WL Driver (5 ports, all metal1)
# -------------------------------------------------------
cd $base_dir
gen_lef_for_block "$base_dir/wl_driver" wl_driver {
    IN      input  signal   190 -100  206  -86
    OUT     output signal  1483   50 1497   64
    VDD     inout  power    190  423  210  431
    VWL     inout  power   1010  623 1030  631
    VSS     inout  ground   800 -467  820 -459
}

puts "=== All LEF files generated ==="
quit -noprompt
