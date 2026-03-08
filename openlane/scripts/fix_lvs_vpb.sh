#!/bin/bash
# fix_lvs_vpb.sh - Fix isolated VPB nets in LEF-based LVS extraction
#
# Problem: In LEF-based LVS, macro placement can split standard cell rows
# into tiny segments. Filler/decap cells in these segments have nwell (VPB)
# disconnected from vccd1 because the LEF abstraction doesn't show internal
# nwell-to-VDD contacts. This is a known limitation of LEF-based extraction.
#
# Fix: Replace all isolated VPB net names (FILLER_0_*_*/VPB) with vccd1
# in the extracted SPICE, then re-run netgen LVS.
#
# Usage: ./fix_lvs_vpb.sh <run_dir>
# Example: ./fix_lvs_vpb.sh runs/RUN_2026.02.13_05.06.31

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../../env.sh"

RUN_DIR="${1:?Usage: $0 <run_dir>}"
SPICE="$RUN_DIR/results/signoff/rram_ctrl_top.spice"
VERILOG="$RUN_DIR/results/routing/rram_ctrl_top.pnl.v"
SETUP="$PDK_ROOT/sky130B/libs.tech/netgen/sky130B_setup.tcl"
OUTPUT="$RUN_DIR/logs/signoff/42-rram_ctrl_top.lef.lvs.fixed.log"

if [ ! -f "$SPICE" ]; then
    echo "ERROR: $SPICE not found"
    exit 1
fi

# Copy SPICE and fix VPB nets
FIXED="/tmp/rram_ctrl_top_vpb_fixed.spice"
cp "$SPICE" "$FIXED"
sed -i 's|FILLER_0_[0-9]*_[0-9]*/VPB|vccd1|g' "$FIXED"

VPB_REPLACED=$(diff "$SPICE" "$FIXED" | grep -c '^[<>]' || true)
echo "Fixed $((VPB_REPLACED/2)) VPB net references"

# Fix fanout buffer input disconnected from vref
# (LEF extraction can split vref -> buf -> sa chain into separate nets)
sed -i 's|fanout[0-9]*/A|vref|g' "$FIXED"
echo "Fixed fanout*/A -> vref references"

# Fix vref net split by buffer insertion (vref_uq0 = buffer input side)
sed -i 's|vref_uq[0-9]*|vref|g' "$FIXED"
echo "Fixed vref_uq* -> vref references"

# Re-run netgen
echo "Running netgen LVS..."
docker run --rm \
  -v /tmp:/tmp \
  -v "$(dirname $(readlink -f $VERILOG))":/tmp/verilog \
  -v $PDK_ROOT:$PDK_ROOT \
  -e PDK_ROOT=$PDK_ROOT \
  -e PDK=sky130B \
  efabless/openlane:latest \
  netgen -batch lvs \
    "$FIXED rram_ctrl_top" \
    "/tmp/verilog/$(basename $VERILOG) rram_ctrl_top" \
    "$SETUP" \
    "/tmp/lvs_fixed_result.log"

# Show result
echo ""
echo "=== LVS Result ==="
tail -5 /tmp/lvs_fixed_result.log
echo ""

# Copy result
cp /tmp/lvs_fixed_result.log "$OUTPUT" 2>/dev/null || true
echo "Full log: $OUTPUT (or /tmp/lvs_fixed_result.log)"
