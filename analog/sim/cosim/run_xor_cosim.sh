#!/bin/bash
# ============================================================
# 2-Array XOR Inference Mixed-Signal Co-Simulation
# ============================================================
# XOR(A,B) = AND( OR(A,B), NAND(A,B) )
#   Phase 0: Array 1 → SA1(OR), SA2(NAND)
#   Phase 1: Array 2 → SA3(AND = XOR result)
#
# Requirements:
#   - ngspice-43 with d_cosim + KLU ($NGSPICE_HOME/)
#   - Verilator 5.x (for vlnggen)
#   - Sky130B PDK with RRAM OSDI model
#   - Python 3 + numpy + matplotlib (for plotting)
#
# Usage:
#   ./run_xor_cosim.sh          # Full run (compile + simulate + plot)
#   ./run_xor_cosim.sh --sim    # Skip compile, run simulation only
#   ./run_xor_cosim.sh --plot   # Skip compile+sim, plot only
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../../../env.sh"
cd "$SCRIPT_DIR"

RTL_DIR="$PROJECT_ROOT/openlane/src"
VERILOG_DIR="$SCRIPT_DIR/verilog"

# Parse arguments
SKIP_COMPILE=false
SKIP_SIM=false
case "${1:-}" in
    --sim)  SKIP_COMPILE=true ;;
    --plot) SKIP_COMPILE=true; SKIP_SIM=true ;;
esac

echo "============================================================"
echo " 2-Array XOR Inference Mixed-Signal Co-Simulation"
echo " XOR(A,B) = AND( OR(A,B), NAND(A,B) )"
echo "============================================================"
echo ""

# --------------------------------------------------------
# Step 1: Compile Verilog → .so via vlnggen (Verilator)
# --------------------------------------------------------
if [ "$SKIP_COMPILE" = false ]; then
    echo "[1/3] Compiling Verilog RTL → xor_cosim_top.so ..."
    echo "  RTL sources:"
    echo "    - $RTL_DIR/xor_controller.v"
    echo "    - $RTL_DIR/input_encoder.v"
    echo "    - $RTL_DIR/sae_control.v"
    echo "    - $VERILOG_DIR/xor_cosim_top.v (d_cosim wrapper)"
    echo ""

    cd "$VERILOG_DIR"

    # vlnggen must be invoked via ngspice with -- separator
    # to prevent -Wno-CASEINCOMPLETE from being parsed as ngspice flag
    $NGSPICE -- "$VLNGGEN" \
        -Wno-CASEINCOMPLETE \
        xor_cosim_top.v \
        "$RTL_DIR/xor_controller.v" \
        "$RTL_DIR/input_encoder.v" \
        "$RTL_DIR/sae_control.v"

    if [ ! -f xor_cosim_top.so ]; then
        echo "ERROR: xor_cosim_top.so not generated!"
        exit 1
    fi

    echo "  → Compiled: $VERILOG_DIR/xor_cosim_top.so"
    echo ""
    cd "$SCRIPT_DIR"
else
    echo "[1/3] Skipping compile (--sim or --plot)"
    echo ""
fi

# --------------------------------------------------------
# Step 2: Run ngspice simulation
# --------------------------------------------------------
if [ "$SKIP_SIM" = false ]; then
    echo "[2/3] Running ngspice mixed-signal simulation ..."
    echo "  Testbench: xor_cosim.spice"
    echo "  OSDI model: sky130_fd_pr_reram__reram_module.osdi"
    echo "  Clock: 200MHz, BL cap: 5pF, Tran: 8000ns"
    echo ""

    $NGSPICE -b xor_cosim.spice > xor_cosim.log 2>&1
    EXIT_CODE=$?

    if [ $EXIT_CODE -ne 0 ]; then
        echo "ERROR: ngspice exited with code $EXIT_CODE"
        echo "Check xor_cosim.log for details."
        exit 1
    fi

    echo "  → Simulation complete. Log: xor_cosim.log"
    echo "  → Waveform data: xor_cosim.csv"
    echo ""

    # Print measurement results
    echo "--- Measurement Results ---"
    grep -E "Test|xr[1-4]" xor_cosim.log
    echo ""
else
    echo "[2/3] Skipping simulation (--plot)"
    echo ""
fi

# --------------------------------------------------------
# Step 3: Generate plots
# --------------------------------------------------------
echo "[3/3] Generating plots ..."

if [ ! -f xor_cosim.csv ]; then
    echo "ERROR: xor_cosim.csv not found. Run simulation first."
    exit 1
fi

python3 plot_xor_cosim.py

echo ""
echo "============================================================"
echo " Results:"
echo "   xor_cosim.log          - Simulation log + measurements"
echo "   xor_cosim.csv          - Raw waveform data"
echo "   xor_cosim_full.png     - 7-panel full overview"
echo "   xor_cosim_detail.png   - Per-test zoomed view"
echo "============================================================"
