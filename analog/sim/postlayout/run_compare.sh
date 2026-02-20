#!/bin/bash
# Post-Layout vs Schematic comparison simulation
# Runs all 3 analog blocks and generates comparison plots

SIMDIR="$(cd "$(dirname "$0")" && pwd)"
source "$SIMDIR/../../../env.sh"

echo "============================================================"
echo "Post-Layout vs Schematic Comparison"
echo "============================================================"
echo ""

cd "$SIMDIR"

echo "[1/3] Sense Amplifier..."
$NGSPICE -b sa_compare.spice 2>&1 | grep -E "(===|---|\bsch_|\blay_|resolve|Error|error)"
echo ""

echo "[2/3] WL Driver..."
$NGSPICE -b wl_compare.spice 2>&1 | grep -E "(===|---|\bsch_|\blay_|tpd|Error|error)"
echo ""

echo "[3/3] BL Write Driver..."
$NGSPICE -b blwd_compare.spice 2>&1 | grep -E "(===|---|\bsch_|\blay_|rise|fall|Error|error)"
echo ""

echo "[Plot] Generating comparison plots..."
python3 plot_compare.py
echo ""
echo "Done. Check PNG files in: $SIMDIR"
