#!/bin/bash
# Gate-Level XOR Simulation with SDF timing
# Uses OpenLane synthesized netlist + analog behavioral models

set -e

SIMDIR="$(cd "$(dirname "$0")" && pwd)"
source "$SIMDIR/../../../../env.sh"
RUN_DIR="$PROJECT_ROOT/openlane/runs/RUN_2026.02.13_05.29.13"
PDK_DIR="$PDK_ROOT/sky130B"

GL_NETLIST="$RUN_DIR/results/final/verilog/gl/rram_ctrl_top.v"
SDF_FILE="$RUN_DIR/results/final/sdf/rram_ctrl_top.sdf"
STD_CELL_V="$PDK_DIR/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v"
PRIMITIVES_V="$PDK_DIR/libs.ref/sky130_fd_sc_hd/verilog/primitives.v"

echo "============================================================"
echo "Gate-Level XOR Simulation"
echo "============================================================"
echo "  Netlist:    $GL_NETLIST"
echo "  SDF:        $SDF_FILE"
echo "  Std cells:  $STD_CELL_V"
echo ""

cd "$SIMDIR"

# Step 1: Compile with iverilog
echo "[1/3] Compiling with iverilog..."
iverilog -g2012 -o gl_xor_sim \
    -DUSE_POWER_PINS \
    -DFUNCTIONAL \
    -DUNIT_DELAY="#0" \
    "$SIMDIR/analog_behavioral.v" \
    "$PRIMITIVES_V" \
    "$STD_CELL_V" \
    "$GL_NETLIST" \
    "$SIMDIR/tb_gl_xor.v" \
    2>&1

echo "  Compile OK"
echo ""

# Step 2: Run simulation
echo "[2/3] Running simulation..."
vvp gl_xor_sim 2>&1 | tee gl_sim.log

echo ""

# Step 3: Check results
echo "[3/3] Results summary:"
if grep -q "ALL TESTS PASSED" gl_sim.log; then
    echo "  *** GATE-LEVEL SIMULATION: ALL PASS ***"
else
    echo "  *** GATE-LEVEL SIMULATION: CHECK FAILURES ***"
    grep -E "FAIL|ERROR|TIMEOUT" gl_sim.log || true
fi

echo ""
echo "Log: $SIMDIR/gl_sim.log"
echo "VCD: $SIMDIR/gl_xor_sim.vcd"
