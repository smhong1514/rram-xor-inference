#!/usr/bin/env python3
"""
fix_lef_pins.py - Fix power pin definitions in analog macro LEF files.

Magic's lef write often fails to set correct DIRECTION and USE for power pins
when the port properties can't be set properly (due to overlapping labels).

This script ensures:
- VDD/VWL pins have DIRECTION INOUT and USE POWER
- VSS pins have DIRECTION INOUT and USE GROUND
- Signal pins have correct DIRECTION (input/output) and USE SIGNAL
"""

import re
import shutil
import os

LEF_FILES = [
    os.path.expandvars("$PROJECT_ROOT/analog/layout/bl_write_driver/bl_write_driver.lef"),
    os.path.expandvars("$PROJECT_ROOT/analog/layout/sense_amp/sense_amp.lef"),
    os.path.expandvars("$PROJECT_ROOT/analog/layout/wl_driver/wl_driver.lef"),
]

DEST_DIR = os.path.expandvars("$PROJECT_ROOT/openlane/lef")

# Pin definitions: name -> (direction, use)
PIN_DEFS = {
    "VDD": ("INOUT", "POWER"),
    "VWL": ("INOUT", "POWER"),
    "VSS": ("INOUT", "GROUND"),
    "EN":  ("INPUT", "SIGNAL"),
    "DATA": ("INPUT", "SIGNAL"),
    "BL":  ("OUTPUT", "SIGNAL"),
    "SAE": ("INPUT", "SIGNAL"),
    "INP": ("INPUT", "SIGNAL"),
    "INN": ("INPUT", "SIGNAL"),
    "Q":   ("OUTPUT", "SIGNAL"),
    "QB":  ("OUTPUT", "SIGNAL"),
    "IN":  ("INPUT", "SIGNAL"),
    "OUT": ("OUTPUT", "SIGNAL"),
}


def fix_lef_pins(lef_path):
    with open(lef_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    fixed_count = 0

    while i < len(lines):
        line = lines[i]

        # Detect PIN <name>
        pin_match = re.match(r"^  PIN (\S+)\s*$", line)
        if pin_match:
            pin_name = pin_match.group(1)
            new_lines.append(line)
            i += 1

            if pin_name in PIN_DEFS:
                direction, use = PIN_DEFS[pin_name]

                # Collect existing lines until PORT or END
                # Remove any existing DIRECTION and USE lines
                has_direction = False
                has_use = False

                while i < len(lines):
                    curr = lines[i]

                    if re.match(r"\s+DIRECTION\s+", curr):
                        # Replace direction
                        new_lines.append(f"    DIRECTION {direction} ;\n")
                        has_direction = True
                        i += 1
                        continue
                    elif re.match(r"\s+USE\s+", curr):
                        # Replace use
                        new_lines.append(f"    USE {use} ;\n")
                        has_use = True
                        i += 1
                        continue
                    elif re.match(r"\s+PORT\s*$", curr) or re.match(r"\s+ANTENNADIFFAREA", curr) or re.match(r"\s+ANTENNAGATEAREA", curr):
                        # Before PORT block, insert missing DIRECTION/USE
                        if not has_direction:
                            new_lines.append(f"    DIRECTION {direction} ;\n")
                            has_direction = True
                        if not has_use:
                            new_lines.append(f"    USE {use} ;\n")
                            has_use = True
                        new_lines.append(curr)
                        i += 1
                        break
                    else:
                        new_lines.append(curr)
                        i += 1

                fixed_count += 1
            continue

        new_lines.append(line)
        i += 1

    macro_name = os.path.basename(lef_path).replace(".lef", "")
    print(f"  {macro_name}: fixed {fixed_count} pin definitions")

    with open(lef_path, "w") as f:
        f.writelines(new_lines)

    dest_path = os.path.join(DEST_DIR, os.path.basename(lef_path))
    shutil.copy2(lef_path, dest_path)
    return True


def main():
    print("LEF Pin Fix: Setting correct DIRECTION/USE for VDD/VSS/VWL")
    print("=" * 60)
    for lef_path in LEF_FILES:
        fix_lef_pins(lef_path)
    print("Done")


if __name__ == "__main__":
    main()
