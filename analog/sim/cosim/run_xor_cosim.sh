#!/bin/bash
# ============================================================
# RRAM XOR Inference Mixed-Signal Co-Simulation (v3 ReLU)
# ============================================================
# XOR(A,B) = AND( OR(A,B), NAND(A,B) )
#
# v3: Analog ReLU activation between Layer 1 and Layer 2
#   Phase 0: Array 1 WLs ON → BL1 develops → ReLU outputs settle
#   Phase 1: Array 2 WLs ON (Array 1 stays ON) → BL2 → SA latch
#
# Requirements:
#   - ngspice-43 with d_cosim + KLU ($NGSPICE_HOME/)
#   - Verilator 5.x (for vlnggen)
#   - Sky130B PDK with RRAM OSDI model
#   - Python 3 + numpy + matplotlib (for plotting)
#
# Usage:
#   ./run_xor_cosim.sh             # v3 schematic (default)
#   ./run_xor_cosim.sh --postlayout # v3 post-layout (PEX)
#   ./run_xor_cosim.sh --sim       # Skip compile, run simulation only
#   ./run_xor_cosim.sh --plot      # Skip compile+sim, plot only
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
POSTLAYOUT=false
case "${1:-}" in
    --postlayout) POSTLAYOUT=true ;;
    --sim)  SKIP_COMPILE=true ;;
    --plot) SKIP_COMPILE=true; SKIP_SIM=true ;;
esac

SPICE_FILE="xor_v3_cosim.spice"
LOG_FILE="xor_v3_cosim.log"
CSV_FILE="xor_v3_cosim.csv"
WRAPPER="xor_v3_cosim_top.v"
SO_FILE="xor_v3_cosim_top.so"

if [ "$POSTLAYOUT" = true ]; then
    SPICE_FILE="xor_v3_postlayout.spice"
    LOG_FILE="xor_v3_postlayout.log"
    CSV_FILE="xor_v3_postlayout.csv"
    echo "Mode: Post-Layout (PEX parasitic caps)"
fi

echo "============================================================"
echo " RRAM XOR Inference Mixed-Signal Co-Simulation (v3 ReLU)"
echo " XOR(A,B) = AND( OR(A,B), NAND(A,B) )"
echo " Testbench: $SPICE_FILE"
echo "============================================================"
echo ""

# --------------------------------------------------------
# Step 1: Compile Verilog → .so via vlnggen (Verilator)
# --------------------------------------------------------
if [ "$SKIP_COMPILE" = false ]; then
    echo "[1/3] Compiling Verilog RTL → $SO_FILE ..."
    echo "  RTL sources:"
    echo "    - $RTL_DIR/xor_controller.v"
    echo "    - $RTL_DIR/input_encoder.v"
    echo "    - $RTL_DIR/sae_control.v"
    echo "    - $VERILOG_DIR/$WRAPPER (d_cosim wrapper)"
    echo ""

    cd "$VERILOG_DIR"

    $NGSPICE -- "$VLNGGEN" \
        -Wno-CASEINCOMPLETE \
        "$WRAPPER" \
        "$RTL_DIR/xor_controller.v" \
        "$RTL_DIR/input_encoder.v" \
        "$RTL_DIR/sae_control.v"

    if [ ! -f "$SO_FILE" ]; then
        echo "ERROR: $SO_FILE not generated!"
        exit 1
    fi

    echo "  → Compiled: $VERILOG_DIR/$SO_FILE"
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
    echo "  OSDI model: sky130_fd_pr_reram__reram_module.osdi"
    echo "  Clock: 200MHz, VREF=1.25V"
    echo ""

    $NGSPICE -b "$SPICE_FILE" > "$LOG_FILE" 2>&1
    EXIT_CODE=$?

    if [ $EXIT_CODE -ne 0 ]; then
        echo "ERROR: ngspice exited with code $EXIT_CODE"
        echo "Check $LOG_FILE for details."
        exit 1
    fi

    echo "  → Simulation complete. Log: $LOG_FILE"
    echo "  → Waveform data: $CSV_FILE"
    echo ""

    echo "--- Measurement Results ---"
    grep -E "Test|xr[1-4]|PASS|FAIL" "$LOG_FILE" | head -20
    echo ""
else
    echo "[2/3] Skipping simulation (--plot)"
    echo ""
fi

# --------------------------------------------------------
# Step 3: Generate plots
# --------------------------------------------------------
echo "[3/3] Generating plots ..."

if [ ! -f "$CSV_FILE" ]; then
    echo "ERROR: $CSV_FILE not found. Run simulation first."
    exit 1
fi

python3 plot_xor_cosim.py

echo ""
echo "============================================================"
echo " Results:"
echo "   $LOG_FILE    - Simulation log + measurements"
echo "   $CSV_FILE    - Raw waveform data"
echo "   xor_v3_cosim_full.png  - Full overview plot"
echo "============================================================"
