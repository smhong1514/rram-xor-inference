#!/bin/bash
# ============================================================
# RRAM XOR Inference Project — Environment Variables
# ============================================================
# Usage: source env.sh
#
# Override defaults by setting variables before sourcing:
#   export PDK_ROOT=/custom/path/pdk  # then source env.sh
# ============================================================

# Project root (auto-detected from this file's location)
export PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Sky130 PDK
export PDK_ROOT="${PDK_ROOT:-$HOME/pdk/share/pdk}"
export PDK=sky130B

# ngspice-43 (custom build with d_cosim + KLU + OSDI)
export NGSPICE_HOME="${NGSPICE_HOME:-$HOME/ngspice-local}"
export NGSPICE="$NGSPICE_HOME/bin/ngspice"
export VLNGGEN="$NGSPICE_HOME/share/ngspice/scripts/vlnggen"

echo "RRAM XOR Inference environment loaded:"
echo "  PROJECT_ROOT = $PROJECT_ROOT"
echo "  PDK_ROOT     = $PDK_ROOT"
echo "  NGSPICE_HOME = $NGSPICE_HOME"
