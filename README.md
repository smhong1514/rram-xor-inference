# RRAM XOR Inference Chip (Sky130) — v3 ReLU

Sky130 PDK 기반 **2-Layer RRAM XOR 신경망 inference 칩** (v3: Analog ReLU Activation).

3×5 + 5×2 RRAM 크로스바 어레이와 23개 아날로그 매크로(WL Driver ×7, ReLU ×5, Sense Amp ×2, BL Write Driver ×7)를 사용하여 XOR 함수를 analog ReLU activation 기반 2-phase inference로 구현합니다.

## Status (v3)

| 항목 | 상태 |
|------|------|
| OpenLane PnR | **DRC=0, LVS=0, Timing clean** (`RUN_2026.02.23_18.03.08`) |
| Mixed-Signal Schematic Co-Sim | **4/4 XOR PASS** (VREF=1.25V) |
| Post-Layout Co-Sim (PEX) | **4/4 XOR PASS** (87 parasitic caps) |
| Analog Blocks | DRC=0, LVS=0 (4 blocks: WL, SA, BL_WD, ReLU) |
| Magic DRC (final GDS) | **0 real violations** |

## Architecture

```
XOR(A,B) = AND( OR(A,B), NAND(A,B) )  ← 2-layer decomposition

Layer 1 (3×5 RRAM Array):
  SL1 = {1, 1, B, A}  ← input encoding (3 rows, 5 columns)
  BL1[0..4] develops based on weight matrix W1

Phase 0: Array 1 WLs ON, SL1 driven
  BL1[i] → ReLU[i] → SL2[i]  ← analog activation (no digital latching)

Phase 1: Array 2 WLs ON (Array 1 stays ON)
  SL2 = ReLU outputs (analog path)
  SA(BL2[0] vs VREF) → z[0] = XOR result
  SA(BL2[1] vs VREF) → z[1] = XOR result (redundant)

Layer 2 (5×2 RRAM Array):
  XOR=1 path: 2×LRS active → BL2 low → SA outputs HIGH
  XOR=0 path: 1×LRS active → BL2 high → SA outputs LOW
```

## Macro Summary (23 total)

| Macro | Count | Description |
|-------|:-----:|-------------|
| RRAM 3×5 Array | 1 | Layer 1: input → hidden (15 cells) |
| RRAM 5×2 Array | 1 | Layer 2: hidden → output (10 cells) |
| WL Driver | 7 | Array1: ×5, Array2: ×2 |
| **ReLU** | **5** | **BL1[0:4] → SL2[0:4] (analog activation)** |
| Sense Amp | 2 | Array2 output only |
| BL Write Driver | 7 | Array1: ×5, Array2: ×2 |

## Quick Start

### 1. Clone

```bash
git clone https://github.com/smhong1514/rram-xor-inference.git
cd rram-xor-inference
```

### 2. Environment Setup

```bash
# Review and customize paths if needed (defaults to ~/pdk, ~/ngspice-local)
source env.sh

# Install everything (system packages, PDK, ngspice-43)
# Takes ~60-90 minutes on first run
./setup/install_all.sh
```

Or install components individually:

```bash
sudo ./setup/install_deps.sh     # System packages (apt)
./setup/install_pdk.sh           # Sky130 PDK with RRAM
./setup/install_ngspice.sh       # ngspice-43 (d_cosim + KLU)
pip3 install -r requirements.txt # Python (numpy, matplotlib)
```

### 3. Run XOR v3 Co-Simulation (Schematic)

```bash
source env.sh
cd analog/sim/cosim

# Compile Verilog controller
$NGSPICE -- $VLNGGEN -Wno-CASEINCOMPLETE verilog/xor_v3_cosim_top.v

# Run simulation
$NGSPICE -b xor_v3_cosim.spice
```

Expected output: 4/4 XOR PASS (x1x2=00→0, 01→1, 10→1, 11→0)

### 4. Run Post-Layout Co-Simulation

```bash
$NGSPICE -b xor_v3_postlayout.spice
```

### 5. Run OpenLane PnR

```bash
source env.sh
./openlane/run_openlane.sh
```

## Repository Structure

```
rram-xor-inference/
├── env.sh                    ← Environment variables (source this first)
├── requirements.txt          ← Python dependencies
│
├── setup/                    ← Environment installation scripts
│   ├── install_all.sh        ← One-click full setup
│   ├── install_deps.sh       ← System packages (apt)
│   ├── install_pdk.sh        ← Sky130 PDK with RRAM (open_pdks)
│   ├── install_ngspice.sh    ← ngspice-43 (d_cosim + KLU + OSDI)
│   └── patches/
│       └── verilator_shim.patch  ← ngspice bug fixes (4 patches)
│
├── openlane/                 ← OpenLane RTL-to-GDS integration
│   ├── src/                  ← Verilog RTL (xor_controller, input_encoder, relu_blackbox, ...)
│   ├── gds/                  ← Macro GDS files (rram_3x5, rram_5x2, relu, ...)
│   ├── lef/                  ← Macro LEF files
│   ├── lib/                  ← Macro Liberty files
│   ├── config.json           ← OpenLane configuration (v3)
│   ├── config/               ← Macro placement (23 macros)
│   ├── run_openlane.sh       ← Docker-based OpenLane runner
│   └── scripts/              ← LVS fix scripts
│
├── analog/                   ← Analog block design
│   ├── xschem/               ← Schematics (WL Driver, SA, BL WD, ReLU)
│   ├── layout/               ← Layout generation + GDS/LEF/LIB
│   │   ├── relu/             ← ReLU 5T OTA + CMOS buffer layout
│   │   ├── sense_amp/        ← StrongARM latch SA layout
│   │   ├── wl_driver/        ← Level shifter + HV buffer layout
│   │   └── bl_write_driver/  ← Tri-state BL driver layout
│   ├── pic/                  ← Schematic images
│   └── sim/                  ← Simulations
│       ├── cosim/            ← d_cosim mixed-signal co-simulation
│       │   ├── xor_v3_cosim.spice      ← v3 schematic co-sim (4/4 PASS)
│       │   ├── xor_v3_postlayout.spice ← v3 post-layout co-sim (4/4 PASS)
│       │   └── verilog/xor_v3_cosim_top.v ← v3 Verilog controller wrapper
│       └── postsim/          ← Post-layout verification results
│
├── reram_cell_fixed/         ← RRAM cell port fixes for LVS
│
└── docs/                     ← Design documentation
    ├── ARCHITECTURE.md       ← System architecture
    ├── PROJECT_GUIDE.md      ← Detailed project guide
    └── VERIFICATION.md       ← Verification methodology
```

## Environment Variables

All scripts use environment variables defined in `env.sh`:

| Variable | Default | Description |
|----------|---------|-------------|
| `PROJECT_ROOT` | (auto-detected) | Repository root directory |
| `PDK_ROOT` | `$HOME/pdk/share/pdk` | Sky130 PDK installation |
| `PDK` | `sky130B` | PDK variant |
| `NGSPICE_HOME` | `$HOME/ngspice-local` | Custom ngspice installation |
| `NGSPICE` | `$NGSPICE_HOME/bin/ngspice` | ngspice binary |
| `VLNGGEN` | `$NGSPICE_HOME/share/.../vlnggen` | Verilog-to-.so compiler |

Override defaults before sourcing:
```bash
export PDK_ROOT=/custom/path/pdk
export NGSPICE_HOME=/opt/ngspice
source env.sh
```

## Key Dependencies

| Tool | Version | Purpose |
|------|---------|---------|
| ngspice | 43 (custom build) | SPICE simulation with d_cosim + KLU + OSDI |
| Verilator | 5.x | Verilog compilation for d_cosim |
| Sky130 PDK | bdc9412b | Process design kit with RRAM |
| OpenLane | 1.1.1 (Docker) | RTL-to-GDS flow |
| Magic VLSI | 8.3+ | Layout extraction, DRC |
| Python 3 | 3.10+ | Plotting (numpy, matplotlib) |

## Analog Blocks

| Block | Transistors | Description |
|-------|:-----------:|-------------|
| WL Driver | 8 (2×1.8V + 6×5V HV) | Level shifter + HV buffer for RRAM WL |
| Sense Amplifier | 10 (all 1.8V) | StrongARM latch-type, single-ended vs VREF |
| BL Write Driver | 8 (all 1.8V) | Tri-state output buffer for RRAM BL |
| **ReLU** | **5 (all 1.8V)** | **5T OTA comparator + CMOS buffer, drives SL2** |

## ReLU Activation (v3 New)

The ReLU block implements analog activation between Layer 1 and Layer 2:

```
BL1[i] → ReLU[i] → SL2[i]

Circuit: 5T OTA (M1=VREF, M2=VBL, M3/M4=PMOS mirror, M5=tail)
         + CMOS inverter buffer (NFET W=10, PMOS W=4)

VBL < VREF  (neuron active):   OUT → HIGH (drives SL2 strong)
VBL > VREF  (neuron inactive): OUT → LOW  (SL2 near GND)

Key insight: Mixed polarity for XOR
  h_OR  path: non-swapped (VBL<VREF → SL2 HIGH = active)
  h_AND path: swapped OTA  (VBL<VREF → SL2 LOW = gives NAND behavior)
```

VREF = 1.25V (schematic and post-layout), VBIAS = 0.6V

## ngspice-43 Patches

The custom ngspice build includes 4 critical bug fixes in `verilator_shim.cpp`:

1. **Bit clear missing `~`** (line 53): `&= (1 << ...)` → `&= ~(1 << ...)`
2. **Missing `|=` operator** (line 83): `topp->name |` → `topp->name |=`
3. **Bit clear missing `~`** (line 85): Same as #1 for inout handler
4. **VerilatedContext use-after-free** (line 135): `const` → `static const`

Without these patches, d_cosim will segfault or corrupt multi-bit signals.

## Version History

| Version | Arrays | Macros | Activation | Result |
|---------|--------|--------|------------|--------|
| v1 | 4×4 + 4×4 | 21 | SA (step) | DRC=0, LVS=0 |
| v2 | 3×5 + 5×2 | 23 | SA (step) | DRC=0, LVS=0, 4/4 PASS |
| **v3** | **3×5 + 5×2** | **23** | **ReLU (analog)** | **DRC=0, LVS=0, 4/4 PASS** |

## License

This project uses the Sky130 open-source PDK by SkyWater Technology / Google.
