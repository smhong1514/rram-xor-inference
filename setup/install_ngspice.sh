#!/bin/bash
# ============================================================
# Build ngspice-43 with d_cosim + KLU + OSDI
# ============================================================
# This builds a CUSTOM ngspice with features not in stock builds:
#   - d_cosim: Verilog-SPICE co-simulation via Verilator
#   - KLU: Fast sparse solver (better than default Sparse)
#   - OSDI: Open Source Device Interface (RRAM compact models)
#   - XSPICE: Extended SPICE (ADC/DAC bridges, digital gates)
#
# The build also patches verilator_shim.cpp to fix 4 bugs:
#   1. Bit clear missing ~ operator (input handler)
#   2. Missing |= operator (inout handler)
#   3. Bit clear missing ~ operator (inout handler)
#   4. VerilatedContext use-after-free (must be static)
#
# Build time: ~5-10 minutes
# Disk space: ~200MB (source + build + install)
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../env.sh"

NGSPICE_SRC="$HOME/ngspice-src"
NGSPICE_TAG="ngspice-43"

echo "============================================================"
echo " Building ngspice-43 (d_cosim + KLU + OSDI)"
echo "============================================================"
echo "  Source:  $NGSPICE_SRC"
echo "  Install: $NGSPICE_HOME"
echo ""

# Step 1: Clone ngspice source
if [ -d "$NGSPICE_SRC" ]; then
    echo "[1/5] ngspice source exists, reusing: $NGSPICE_SRC"
    cd "$NGSPICE_SRC"
    git fetch origin
else
    echo "[1/5] Cloning ngspice source..."
    git clone https://git.code.sf.net/p/ngspice/ngspice "$NGSPICE_SRC"
    cd "$NGSPICE_SRC"
fi

# Step 2: Checkout ngspice-43
echo "[2/5] Checking out $NGSPICE_TAG..."
git checkout "$NGSPICE_TAG"

# Step 3: Apply verilator_shim.cpp patch
echo "[3/5] Applying verilator_shim.cpp bugfix patch..."
PATCH_FILE="$PROJECT_ROOT/setup/patches/verilator_shim.patch"
if [ -f "$PATCH_FILE" ]; then
    # Reset any previous patch before applying
    git checkout -- src/xspice/verilog/verilator_shim.cpp 2>/dev/null || true
    patch -p1 < "$PATCH_FILE"
    echo "  Patch applied successfully."
else
    echo "  WARNING: Patch file not found: $PATCH_FILE"
    echo "  d_cosim may have bugs (segfault, multi-bit signal corruption)"
fi

# Step 4: Configure
echo "[4/5] Configuring..."
./autogen.sh
mkdir -p release
cd release

../configure \
    --enable-xspice \
    --enable-osdi \
    --enable-klu \
    --with-readline=yes \
    --enable-openmp \
    --disable-debug \
    --prefix="$NGSPICE_HOME"

# Step 5: Build + Install
echo "[5/5] Building and installing..."
make -j"$(nproc)"
make install

echo ""
echo "============================================================"
echo " ngspice-43 installed successfully"
echo "============================================================"
echo "  Binary:  $NGSPICE"
echo "  vlnggen: $VLNGGEN"
echo ""
echo "  Verify: $NGSPICE --version"
echo "  Test:   $NGSPICE -b -c 'echo hello ; quit'"
