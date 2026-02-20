# RRAM XOR Inference Chip (Sky130)

Sky130 PDK 기반 **2-Array RRAM XOR 신경망 inference 칩**.

2개의 RRAM 4x4 크로스바 어레이와 21개 아날로그 매크로(WL Driver x8, Sense Amplifier x3, BL Write Driver x8)를 사용하여 XOR 함수를 2-phase inference로 구현합니다.

## Status

| 항목 | 상태 |
|------|------|
| OpenLane PnR | DRC=0, LVS=0, Timing clean |
| Mixed-Signal Co-Sim | 4/4 XOR truth table PASS |
| Post-Layout Verification | Schematic vs Layout 일치 |
| Analog Blocks | DRC 0, LVS PASS (3 blocks) |

## Architecture

```
XOR(A,B) = AND( OR(A,B), NAND(A,B) )

Phase 0 (Array 1):  SL1 = {1, 1, B, A}
  SA1(BL[0] vs BL[1]) → h1 (OR)
  SA2(BL[2] vs BL[3]) → h2 (NAND)

Phase 1 (Array 2):  SL2 = {1, 1, h2, h1}
  SA3(BL[0] vs BL[1]) → xor_result (AND)
```

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

### 3. Run XOR Co-Simulation

```bash
source env.sh
cd analog/sim/cosim
./run_xor_cosim.sh
```

Expected output:
```
  Test   A   B   OR  NAND  AND  Expected  Got   Status
------------------------------------------------------------
     1   0   0    0     1    0         0    0     PASS
     2   0   1    1     1    1         1    1     PASS
     3   1   0    1     1    1         1    1     PASS
     4   1   1    1     0    0         0    0     PASS
------------------------------------------------------------
  ALL 4 TESTS PASSED — XOR inference verified!
```

### 4. Run OpenLane PnR

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
│   ├── src/                  ← Verilog RTL (xor_controller, input_encoder, ...)
│   ├── gds/                  ← Macro GDS files
│   ├── lef/                  ← Macro LEF files
│   ├── lib/                  ← Macro Liberty files
│   ├── config.json           ← OpenLane configuration
│   ├── config/               ← Macro placement
│   ├── run_openlane.sh       ← Docker-based OpenLane runner
│   └── scripts/              ← LVS fix scripts
│
├── analog/                   ← Analog block design
│   ├── xschem/               ← Schematics (WL Driver, SA, BL WD)
│   ├── layout/               ← Layout generation + GDS/LEF/LIB
│   ├── pic/                  ← Schematic images
│   └── sim/                  ← Simulations
│       ├── cosim/            ← d_cosim mixed-signal co-simulation
│       ├── postsim/          ← Post-layout verification results
│       └── postlayout/       ← Schematic vs Layout comparison
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
| WL Driver | 8 (2x1.8V + 6x5V HV) | Level shifter + HV buffer |
| Sense Amplifier | 10 (all 1.8V) | StrongARM latch-type |
| BL Write Driver | 8 (all 1.8V) | Tri-state output buffer |

## ngspice-43 Patches

The custom ngspice build includes 4 critical bug fixes in `verilator_shim.cpp`:

1. **Bit clear missing `~`** (line 53): `&= (1 << ...)` → `&= ~(1 << ...)`
2. **Missing `|=` operator** (line 83): `topp->name |` → `topp->name |=`
3. **Bit clear missing `~`** (line 85): Same as #1 for inout handler
4. **VerilatedContext use-after-free** (line 135): `const` → `static const`

Without these patches, d_cosim will segfault or corrupt multi-bit signals.

## License

This project uses the Sky130 open-source PDK by SkyWater Technology / Google.
