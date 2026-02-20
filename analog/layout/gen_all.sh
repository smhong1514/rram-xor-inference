#!/bin/bash
# gen_all.sh - Generate LEF and LIB files for all 3 analog blocks
# Run from: analog/layout/
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../../env.sh"
cd "$SCRIPT_DIR"

echo "============================================"
echo " Generating LEF + LIB for Analog Blocks"
echo "============================================"
echo ""

# 1. LEF generation via Magic
echo "--- Step 1: LEF Generation (Magic) ---"
magic -noconsole -dnull \
  -rcfile $PDK_ROOT/sky130B/libs.tech/magic/sky130B.magicrc \
  < gen_lef.tcl
echo ""

# 2. LIB generation via Python
echo "--- Step 2: LIB Generation (Python) ---"
python3 gen_lib.py
echo ""

# 3. Summary
echo "============================================"
echo " Generated Files Summary"
echo "============================================"
for block in bl_write_driver sense_amp wl_driver; do
    echo ""
    echo "[$block]"
    if [ -f "$block/${block}.lef" ]; then
        size=$(wc -c < "$block/${block}.lef")
        echo "  LEF: ${block}/${block}.lef ($size bytes)"
        grep -E "^  SIZE|MACRO|PIN " "$block/${block}.lef" 2>/dev/null | head -20
    else
        echo "  LEF: MISSING!"
    fi
    if [ -f "$block/${block}.lib" ]; then
        size=$(wc -c < "$block/${block}.lib")
        echo "  LIB: ${block}/${block}.lib ($size bytes)"
    else
        echo "  LIB: MISSING!"
    fi
done
echo ""
echo "Done."
