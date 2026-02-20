#!/usr/bin/env python3
"""gen_lib.py - Generate blackbox Liberty (.lib) stubs for 3 analog blocks.

These are placeholder LIB files for OpenLane synthesis (blackbox recognition).
Dummy capacitance values; replace with ngspice characterization later.

Run from: ~/rram_openlane/analog/layout/
"""

import os
import textwrap

BLOCKS = {
    "bl_write_driver": {
        "inputs": ["EN", "DATA"],
        "outputs": ["BL"],
        "power": [("VDD", "primary_power", 1.8),
                  ("VSS", "primary_ground", 0.0)],
    },
    "sense_amp": {
        "inputs": ["SAE", "INP", "INN"],
        "outputs": ["Q", "QB"],
        "power": [("VDD", "primary_power", 1.8),
                  ("VSS", "primary_ground", 0.0)],
    },
    "wl_driver": {
        "inputs": ["IN"],
        "outputs": ["OUT"],
        "power": [("VDD", "primary_power", 1.8),
                  ("VWL", "primary_power", 3.3),
                  ("VSS", "primary_ground", 0.0)],
    },
}


def gen_lib(cell_name, info):
    """Generate a blackbox Liberty file for one analog block."""

    lines = []
    lines.append(f'library ({cell_name}) {{')
    lines.append(textwrap.dedent("""\
      comment : "Blackbox stub for OpenLane integration";
      technology (cmos);
      delay_model : table_lookup;
      time_unit : "1ns";
      voltage_unit : "1v";
      current_unit : "1uA";
      pulling_resistance_unit : "1kohm";
      capacitive_load_unit (1, pF);
      nom_process : 1.0;
      nom_temperature : 25.0;
      nom_voltage : 1.80;
      default_cell_leakage_power : 0;
      default_fanout_load : 1;
      default_output_pin_cap : 0.0;
      default_input_pin_cap : 0.0;
      default_inout_pin_cap : 0.0;
    """).rstrip())

    # operating_conditions
    lines.append(textwrap.dedent("""\
      operating_conditions (typical) {
        process : 1.0;
        temperature : 25.0;
        voltage : 1.80;
      }
      default_operating_conditions : typical;
    """).rstrip())

    # cell
    lines.append(f'  cell ({cell_name}) {{')
    lines.append('    is_macro_cell : true;')
    lines.append('    dont_touch : true;')
    lines.append('    dont_use : true;')
    lines.append('')

    # Power / ground pins
    for pin_name, pg_type, voltage in info["power"]:
        direction = "inout"
        use_type = "power" if "power" in pg_type else "ground"
        lines.append(f'    pin ({pin_name}) {{')
        lines.append(f'      direction : {direction};')
        lines.append(f'    }}')
        lines.append(f'    pg_pin ({pin_name}) {{')
        lines.append(f'      voltage_name : {pin_name};')
        lines.append(f'      pg_type : {pg_type};')
        lines.append(f'    }}')
        lines.append('')

    # Input pins (dummy capacitance ~2fF)
    for pin_name in info["inputs"]:
        lines.append(f'    pin ({pin_name}) {{')
        lines.append(f'      direction : input;')
        lines.append(f'      capacitance : 0.002;')
        lines.append(f'    }}')
        lines.append('')

    # Output pins (dummy max_capacitance 0.5pF)
    for pin_name in info["outputs"]:
        lines.append(f'    pin ({pin_name}) {{')
        lines.append(f'      direction : output;')
        lines.append(f'      max_capacitance : 0.5;')
        lines.append(f'    }}')
        lines.append('')

    lines.append('  }')  # end cell
    lines.append('}')     # end library
    lines.append('')

    return '\n'.join(lines)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    for cell_name, info in BLOCKS.items():
        lib_content = gen_lib(cell_name, info)
        out_dir = os.path.join(base_dir, cell_name)
        out_path = os.path.join(out_dir, f'{cell_name}.lib')

        os.makedirs(out_dir, exist_ok=True)
        with open(out_path, 'w') as f:
            f.write(lib_content)

        print(f"  Written: {out_path}")

    print("\n=== All LIB files generated ===")


if __name__ == '__main__':
    main()
