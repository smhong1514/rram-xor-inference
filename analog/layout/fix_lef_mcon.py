#!/usr/bin/env python3
"""Fix LEF files to prevent router from placing mcon contacts on signal pins.

Root cause: When LEF pin PORT exposes li1 layer, the router places its own
mcon (li1-to-met1 via) contacts which conflict with macro-internal mcon.

Fix: Move li1 shapes from signal pin PORTs to OBS section. The router will
connect via met1/met2 instead, avoiding mcon spacing violations.
"""

import os
import re
import sys
from pathlib import Path

# Signal pins whose li1 should be moved to OBS
# Power pins (VDD, VSS, VWL) keep li1 in PORT
SIGNAL_PINS = {"IN", "OUT", "EN", "DATA", "BL", "SAE", "INP", "INN", "Q", "QB"}


def fix_lef(lef_path):
    text = Path(lef_path).read_text()

    # Parse: extract li1 rects from signal pin PORTs
    li1_to_obs = []  # li1 rects to move to OBS

    lines = text.split('\n')
    result = []
    in_pin = False
    in_port = False
    in_li1 = False
    current_pin = None
    is_signal_pin = False
    skip_li1_layer_header = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Track PIN blocks
        if stripped.startswith('PIN '):
            pin_name = stripped.split()[1]
            current_pin = pin_name
            is_signal_pin = pin_name in SIGNAL_PINS
            in_pin = True
            result.append(line)
            i += 1
            continue

        if stripped == 'END' and in_pin and i + 1 < len(lines):
            # Check if next non-empty line starts a new section
            pass

        if in_pin and re.match(r'\s*END\s+' + re.escape(current_pin) + r'\s*$', stripped):
            in_pin = False
            is_signal_pin = False
            result.append(line)
            i += 1
            continue

        # Track PORT blocks
        if stripped == 'PORT':
            in_port = True
            result.append(line)
            i += 1
            continue

        if stripped == 'END' and in_port:
            in_port = False
            in_li1 = False
            result.append(line)
            i += 1
            continue

        # Inside a signal pin's PORT: skip li1 layer and its rects
        if in_port and is_signal_pin:
            if stripped.startswith('LAYER li1'):
                in_li1 = True
                # Don't output this line
                i += 1
                continue

            if in_li1:
                if stripped.startswith('RECT '):
                    # Move this rect to OBS
                    li1_to_obs.append(stripped)
                    i += 1
                    continue
                elif stripped.startswith('LAYER ') or stripped == 'END':
                    # End of li1 section
                    in_li1 = False
                    # Fall through to output this line
                else:
                    in_li1 = False

        result.append(line)
        i += 1

    if not li1_to_obs:
        print(f"  No li1 shapes to move in {lef_path}")
        return

    # Add the moved li1 rects to OBS section
    text_out = '\n'.join(result)

    # Find OBS section and add li1 rects
    obs_match = re.search(r'(\s*OBS\n)', text_out)
    if obs_match:
        # Check if OBS already has LAYER li1
        obs_start = obs_match.end()
        obs_section = text_out[obs_start:]

        # Add after existing li1 shapes in OBS, or create new li1 section
        if 'LAYER li1' in obs_section.split('END')[0]:
            # Find the last li1 RECT in OBS and add after it
            # Insert before the next LAYER or END in OBS
            insert_pos = obs_start
            found_li1 = False
            for m in re.finditer(r'(      LAYER li1 ;\n)', text_out[obs_start:]):
                found_li1 = True
                # Find the end of li1 rects
                after_li1 = obs_start + m.end()
                while after_li1 < len(text_out):
                    next_line = text_out[after_li1:text_out.index('\n', after_li1)]
                    if next_line.strip().startswith('RECT'):
                        after_li1 = text_out.index('\n', after_li1) + 1
                    else:
                        break
                insert_pos = after_li1
                break

            if found_li1:
                extra = ''.join(f'        {r}\n' for r in li1_to_obs)
                text_out = text_out[:insert_pos] + extra + text_out[insert_pos:]
            else:
                # Shouldn't happen but handle it
                extra = '      LAYER li1 ;\n' + ''.join(f'        {r}\n' for r in li1_to_obs)
                text_out = text_out[:obs_start] + extra + text_out[obs_start:]
        else:
            # No li1 in OBS yet, add it
            extra = '      LAYER li1 ;\n' + ''.join(f'        {r}\n' for r in li1_to_obs)
            text_out = text_out[:obs_start] + extra + text_out[obs_start:]
    else:
        # No OBS section - create one before END MACRO
        macro_end = text_out.rfind('END ')
        extra = '  OBS\n      LAYER li1 ;\n' + ''.join(f'        {r}\n' for r in li1_to_obs) + '  END\n'
        text_out = text_out[:macro_end] + extra + text_out[macro_end:]

    Path(lef_path).write_text(text_out)
    print(f"  Fixed {lef_path}: moved {len(li1_to_obs)} li1 rects from signal pins to OBS")


if __name__ == '__main__':
    base = Path(os.path.expandvars("$PROJECT_ROOT/analog/layout"))
    openlane_lef = Path(os.path.expandvars("$PROJECT_ROOT/openlane/lef"))

    for block in ["wl_driver", "bl_write_driver", "sense_amp"]:
        lef_src = base / block / f"{block}.lef"
        lef_dst = openlane_lef / f"{block}.lef"

        if lef_src.exists():
            print(f"\nProcessing {block}:")
            fix_lef(str(lef_src))

            # Copy to openlane
            import shutil
            shutil.copy2(lef_src, lef_dst)
            print(f"  Copied to {lef_dst}")
