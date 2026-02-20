#!/bin/bash
# ============================================================
# Build Sky130 PDK with RRAM support (OpenLane 1.1.1 matched)
# ============================================================
# open_pdks commit: bdc9412b3e468c102d01b7cf6337be06ec6e9c9a
# Required for: RRAM OSDI compact model, ngspice tech files
#
# Build time: ~30-60 minutes (downloads PDK sources via git)
# Disk space: ~5GB (source + installed)
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../env.sh"

PDK_PREFIX="$(dirname "$PDK_ROOT")"
OPEN_PDKS_DIR="$HOME/open_pdks_build"
OPEN_PDKS_COMMIT="bdc9412b3e468c102d01b7cf6337be06ec6e9c9a"

echo "============================================================"
echo " Building Sky130 PDK with RRAM support"
echo "============================================================"
echo "  open_pdks commit: $OPEN_PDKS_COMMIT"
echo "  Install prefix:   $PDK_PREFIX"
echo "  PDK_ROOT:         $PDK_ROOT"
echo ""

# Step 1: Clone open_pdks
if [ -d "$OPEN_PDKS_DIR" ]; then
    echo "[1/4] open_pdks directory exists, reusing: $OPEN_PDKS_DIR"
    cd "$OPEN_PDKS_DIR"
    git fetch origin
else
    echo "[1/4] Cloning open_pdks..."
    git clone https://github.com/RTimothyEdwards/open_pdks.git "$OPEN_PDKS_DIR"
    cd "$OPEN_PDKS_DIR"
fi

# Step 2: Checkout matching commit
echo "[2/4] Checking out commit $OPEN_PDKS_COMMIT..."
git checkout "$OPEN_PDKS_COMMIT"

# Step 3: Configure
echo "[3/4] Configuring..."
echo "  --enable-sky130-pdk"
echo "  --enable-reram-sky130   (RRAM compact model)"
echo "  --disable-klayout-sky130 (avoids build errors)"
echo "  --prefix=$PDK_PREFIX"
echo ""

./configure \
    --enable-sky130-pdk \
    --enable-reram-sky130 \
    --disable-klayout-sky130 \
    --prefix="$PDK_PREFIX"

# Step 4: Build + Install
# IMPORTANT: Use -j1 (sequential) to avoid git clone race conditions
echo "[4/4] Building and installing (this takes 30-60 minutes)..."
echo "  Using make -j1 (sequential build required to avoid git conflicts)"
make -j1
make install

echo ""
echo "============================================================"
echo " PDK installed successfully"
echo "============================================================"
echo "  PDK_ROOT: $PDK_ROOT"
echo "  Sky130B:  $PDK_ROOT/sky130B/"
echo ""
echo "  Verify: ls $PDK_ROOT/sky130B/libs.tech/ngspice/"
echo "  RRAM:   ls $PDK_ROOT/sky130B/libs.tech/ngspice/*reram*"
