#!/bin/bash
# ============================================================
# Install system dependencies for RRAM XOR Inference project
# ============================================================
# Tested on: Ubuntu 22.04+ / WSL2
# Run as: sudo ./install_deps.sh  (or without sudo for non-apt parts)
# ============================================================
set -e

echo "============================================================"
echo " Installing system dependencies"
echo "============================================================"
echo ""

# Build tools
echo "[1/5] Build tools..."
sudo apt-get update
sudo apt-get install -y \
    build-essential gcc g++ \
    autoconf automake libtool \
    bison flex \
    git wget curl

# ngspice build dependencies
echo "[2/5] ngspice build dependencies..."
sudo apt-get install -y \
    libx11-dev libxaw7-dev libxmu-dev libxt-dev libxext-dev \
    libxft-dev libfreetype6-dev libfontconfig1-dev libxrender-dev \
    libreadline-dev \
    libsuitesparse-dev \
    libfftw3-dev

# EDA tools
echo "[3/5] EDA tools (verilator, magic)..."
sudo apt-get install -y \
    verilator \
    magic \
    netgen-lvs \
    tcl-dev tk-dev

# Python
echo "[4/5] Python dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv
pip3 install --user numpy matplotlib

# Docker
echo "[5/5] Docker..."
if ! command -v docker &> /dev/null; then
    sudo apt-get install -y docker.io
    sudo usermod -aG docker "$USER"
    echo "  Docker installed. Log out and back in for group changes."
else
    echo "  Docker already installed: $(docker --version)"
fi

echo ""
echo "============================================================"
echo " System dependencies installed successfully"
echo "============================================================"
echo ""
echo "Verilator: $(verilator --version 2>/dev/null || echo 'not found')"
echo "Magic:     $(magic --version 2>/dev/null | head -1 || echo 'not found')"
echo "Python3:   $(python3 --version 2>/dev/null || echo 'not found')"
echo "Docker:    $(docker --version 2>/dev/null || echo 'not found')"
