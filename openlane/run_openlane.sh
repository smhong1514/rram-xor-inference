#!/bin/bash
# ============================================================
# Run OpenLane RTL-to-GDS flow for RRAM XOR Inference chip
# ============================================================
# Uses Docker image efabless/openlane:latest (contains OpenLane v1.1.1)
# Produces: GDS, DEF, netlist, timing reports
#
# Prerequisites:
#   - source ../env.sh (PDK_ROOT, PROJECT_ROOT)
#   - Docker installed and running
#   - PDK built (setup/install_pdk.sh)
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../env.sh"

OPENLANE_TAG="latest"  # Contains OpenLane v1.1.1 (Nix-based)

echo "============================================================"
echo " OpenLane RTL-to-GDS: RRAM XOR Inference"
echo "============================================================"
echo "  Docker image: efabless/openlane:$OPENLANE_TAG"
echo "  Design dir:   $SCRIPT_DIR"
echo "  PDK_ROOT:     $PDK_ROOT"
echo ""

docker run --rm \
    -v "$SCRIPT_DIR":/openlane/designs/rram_ctrl \
    -v "$PDK_ROOT":"$PDK_ROOT" \
    -e PDK_ROOT="$PDK_ROOT" \
    -e PDK=sky130B \
    efabless/openlane:"$OPENLANE_TAG" \
    flow.tcl -design /openlane/designs/rram_ctrl

echo ""
echo "============================================================"
echo " OpenLane flow complete"
echo " Check runs/ directory for results"
echo "============================================================"
