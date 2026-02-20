#!/bin/bash
# RRAM Mixed-Signal Co-Simulation
# Compiles Verilog (iverilog) + runs ngspice with d_cosim
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../../../env.sh"
cd "$SCRIPT_DIR"

echo "============================================"
echo "RRAM Mixed-Signal Co-Simulation"
echo "============================================"

# Step 1: Compile Verilog with Icarus Verilog
echo ""
echo "[1/3] Compiling Verilog with iverilog..."
CTRL_SRC="$SCRIPT_DIR/../../openlane/src/controller.v"
COSIM_SRC="$SCRIPT_DIR/controller_cosim.v"

if [ ! -f "$CTRL_SRC" ]; then
    # Fallback: try relative to rram_openlane
    CTRL_SRC="$PROJECT_ROOT/openlane/src/controller.v"
fi

echo "  Controller: $CTRL_SRC"
echo "  Wrapper:    $COSIM_SRC"

iverilog -o controller_cosim "$COSIM_SRC" "$CTRL_SRC"
echo "  → Compiled: controller_cosim"

# Step 2: Run ngspice simulation
echo ""
echo "[2/3] Running ngspice mixed-signal simulation..."
$NGSPICE -b rram_mixed_tb.spice 2>&1 | tee cosim_output.log

# Step 3: Plot results
echo ""
echo "[3/3] Plotting results..."
if [ -f rram_mixed_tb.csv ]; then
    python3 plot_cosim.py
    echo "  → Plot saved: rram_cosim_result.png"
else
    echo "  WARNING: CSV output not found. Check cosim_output.log for errors."
fi

echo ""
echo "============================================"
echo "Done. Check cosim_output.log for details."
echo "============================================"
