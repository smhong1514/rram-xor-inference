#!/usr/bin/env python3
"""
fix_lef_obs.py - Add full-area OBS for met2/met3/via/via2 to analog macro LEFs.

Keeps original per-shape OBS for li1 and met1 (PDN needs met1 access).
Adds full-area blocks for met2, met3, via, via2 to prevent the detailed
router from routing through the analog macro area.
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


def fix_lef_obs(lef_path):
    with open(lef_path, "r") as f:
        lines = f.readlines()

    # Extract SIZE
    size_x = size_y = None
    for line in lines:
        m = re.match(r"\s*SIZE\s+([\d.]+)\s+BY\s+([\d.]+)\s*;", line)
        if m:
            size_x, size_y = float(m.group(1)), float(m.group(2))
            break

    if size_x is None:
        print(f"  ERROR: No SIZE found in {lef_path}")
        return False

    macro_name = os.path.basename(lef_path).replace(".lef", "")
    print(f"  {macro_name}: SIZE {size_x} x {size_y}")

    # Find the OBS "  END" line and insert full-area met2/met3 before it
    # Strategy: find "  OBS" start, then find corresponding "  END"
    obs_start = None
    obs_end = None
    for i, line in enumerate(lines):
        if line.strip() == "OBS":
            obs_start = i
        # The "  END" after OBS (not "  END <pin_name>")
        if obs_start is not None and i > obs_start and re.match(r"^\s+END\s*$", line):
            obs_end = i
            break

    if obs_start is None or obs_end is None:
        print(f"  ERROR: No OBS section found")
        return False

    # Remove any existing met2/met3/via/via2 full-area entries from original OBS
    # (in case this script was already run)
    existing_obs = lines[obs_start+1:obs_end]

    # Filter out existing met2, met3, via, via2 LAYER entries and their RECTs
    # that are full-area (0.0 0.0 SIZE_X SIZE_Y)
    filtered_obs = []
    skip_layer = False
    for line in existing_obs:
        layer_m = re.match(r"\s+LAYER\s+(met2|met3|via|via2)\s*;", line)
        if layer_m:
            # Check if next rect is full-area - for safety, remove all met2/met3/via/via2
            skip_layer = True
            continue
        if skip_layer:
            if re.match(r"\s+RECT\s+", line):
                continue  # skip RECT under removed layer
            elif re.match(r"\s+LAYER\s+", line):
                skip_layer = False
                filtered_obs.append(line)
            else:
                skip_layer = False
                filtered_obs.append(line)
        else:
            filtered_obs.append(line)

    # Build new full-area entries
    full_area = [
        f"      LAYER met2 ;\n",
        f"        RECT 0.000 0.000 {size_x:.3f} {size_y:.3f} ;\n",
        f"      LAYER met3 ;\n",
        f"        RECT 0.000 0.000 {size_x:.3f} {size_y:.3f} ;\n",
        f"      LAYER via ;\n",
        f"        RECT 0.000 0.000 {size_x:.3f} {size_y:.3f} ;\n",
        f"      LAYER via2 ;\n",
        f"        RECT 0.000 0.000 {size_x:.3f} {size_y:.3f} ;\n",
    ]

    # Reconstruct: keep lines before OBS body, filtered OBS body, full-area, END, rest
    new_lines = lines[:obs_start+1] + filtered_obs + full_area + lines[obs_end:]

    with open(lef_path, "w") as f:
        f.writelines(new_lines)
    print(f"  Written: {lef_path}")

    dest_path = os.path.join(DEST_DIR, os.path.basename(lef_path))
    shutil.copy2(lef_path, dest_path)
    print(f"  Copied:  {dest_path}")
    return True


def main():
    print("LEF OBS Fix: Adding full-area OBS for met2/met3/via/via2")
    print("(Keeping original per-shape OBS for li1/met1)")
    print("=" * 60)

    ok = 0
    for lef_path in LEF_FILES:
        if fix_lef_obs(lef_path):
            ok += 1
    print(f"\nDone: {ok}/{len(LEF_FILES)} files processed")


if __name__ == "__main__":
    main()
