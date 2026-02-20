#!/bin/bash
# ============================================================
# One-click full environment setup
# ============================================================
# Installs everything needed for the RRAM XOR Inference project:
#   1. System packages (apt)
#   2. Sky130 PDK with RRAM support
#   3. ngspice-43 with d_cosim + KLU
#   4. Python dependencies
#
# Total time: ~60-90 minutes (mostly PDK build)
# Total disk: ~6GB
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../env.sh"

echo "============================================================"
echo " RRAM XOR Inference — Full Environment Setup"
echo "============================================================"
echo ""
echo "This will install:"
echo "  1. System packages (requires sudo)"
echo "  2. Sky130 PDK with RRAM  → $PDK_ROOT"
echo "  3. ngspice-43 (d_cosim)  → $NGSPICE_HOME"
echo "  4. Python packages       → numpy, matplotlib"
echo ""
read -p "Continue? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "========== [1/4] System Dependencies =========="
bash "$SCRIPT_DIR/install_deps.sh"

echo ""
echo "========== [2/4] Sky130 PDK =========="
bash "$SCRIPT_DIR/install_pdk.sh"

echo ""
echo "========== [3/4] ngspice-43 =========="
bash "$SCRIPT_DIR/install_ngspice.sh"

echo ""
echo "========== [4/4] Python Packages =========="
pip3 install --user -r "$PROJECT_ROOT/requirements.txt"

echo ""
echo "============================================================"
echo " Setup complete!"
echo "============================================================"
echo ""
echo " Add to your ~/.bashrc:"
echo "   source $PROJECT_ROOT/env.sh"
echo ""
echo " Quick test:"
echo "   cd $PROJECT_ROOT/analog/sim/cosim"
echo "   ./run_xor_cosim.sh"
echo "============================================================"
