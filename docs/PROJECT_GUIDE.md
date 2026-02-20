# RRAM 4x4 XOR Neural Network - Sky130 PDK

Sky130 PDK 기반 RRAM 4x4 크로스바 어레이를 이용한 XOR 신경망 inference 칩 설계.
디지털 컨트롤러(OpenLane RTL-to-GDS) + 아날로그 CIM 블록(Magic VLSI layout) + Mixed-Signal co-simulation 완료.

## 검증 결과 요약

| 구분 | 항목 | 결과 |
|------|------|------|
| 디지털 | OpenLane DRC/LVS | **PASS** (0 errors, 179 devices, 175 nets) |
| 아날로그 | 3블록 레이아웃 DRC/LVS | **PASS** (WL Driver, SA, BL Write Driver 모두 0 errors) |
| 아날로그 | Liberty characterization | **완료** (ngspice 7×7 sweep, 3블록 .lib 생성) |
| 시뮬레이션 | SA 단독 | **PASS** (50mV→1.8V full-swing, 230ps) |
| 시뮬레이션 | 2-Layer XOR inference | **4/4 PASS** (3개 RRAM array + 12 WL Driver + 6 SA) |
| Mixed-Signal | d_cosim co-simulation | **PASS** (FSM↔아날로그 closed-loop) |

---

## 전체 프로젝트 흐름 (Phase 0 ~ 9)

이 프로젝트는 아래 순서로 진행되었습니다. 새 서버에서 재현할 때도 이 순서를 따르면 됩니다.

### Phase 0: 환경 설정 & PDK 빌드

#### 0-1. 시스템 요구사항

```bash
# Ubuntu 22.04+
sudo apt-get update && sudo apt-get install -y \
  build-essential python3 python3-pip python3-venv \
  tcl-dev tk-dev tcsh csh \
  libx11-dev libcairo2-dev libncurses-dev \
  m4 git docker.io \
  libxpm-dev libxaw7-dev libreadline-dev

# Docker 권한
sudo usermod -aG docker $USER
# → 재로그인 필요

# Python 패키지
pip3 install matplotlib numpy gdsfactory klayout
```

#### 0-2. PDK 빌드 (open_pdks → pdk)

> **PDK 버전 매칭이 핵심입니다.** OpenLane 1.1.1은 특정 open_pdks 커밋을 기대합니다.
> 불일치 시 `-ignore_mismatches` 플래그가 필요하거나, 미묘한 DRC/설정 차이가 발생합니다.

**PDK 변천사 (실제 경험):**

| 시도 | 방법 | 결과 |
|------|------|------|
| 1차 | volare (PDK 패키지 매니저) | 문제 발생 → 포기 |
| 2차 | open_pdks master branch | RRAM 라이브러리 누락 (`--enable-reram-sky130` 미사용) |
| 3차 | open_pdks master + RRAM flag | OpenLane 1.1.1과 버전 불일치 |
| **최종** | **open_pdks commit `bdc9412b` + RRAM flag** | **OpenLane 1.1.1 정확히 매칭, RRAM 포함** |

**빌드 방법:**

```bash
# 1. open_pdks 클론 및 버전 고정
git clone https://github.com/RTimothyEdwards/open_pdks.git ~/open_pdks_matched
cd ~/open_pdks_matched
git checkout bdc9412b3e468c102d01b7cf6337be06ec6e9c9a

# 2. 빌드 설정
./configure --enable-sky130-pdk \
            --enable-reram-sky130 \
            --disable-klayout-sky130 \
            --prefix=$HOME/pdk

# 옵션 설명:
#   --enable-sky130-pdk      : Sky130 PDK 빌드 (필수)
#   --enable-reram-sky130    : RRAM 라이브러리 포함 (기본값에서 빠짐! 반드시 필요)
#   --disable-klayout-sky130 : klayout 관련 빌드 에러 회피
#   --prefix                 : 시스템 PDK와 분리 설치

# 3. 빌드 & 설치 (1~2시간 소요)
#    make -j1: git clone 충돌 방지를 위해 순차 빌드 권장
make -j1 2>&1 | tee ~/pdk_build.log
make install
# → ~/pdk/share/pdk/ 에 sky130A, sky130B 설치 (~7.3 GB)
```

**환경변수 설정 (~/.bashrc에 추가):**

```bash
export PDK_ROOT=$HOME/pdk/share/pdk
export PDK=sky130B
export SKYWATER_MODELS=$PDK_ROOT/$PDK/libs.tech/ngspice
```

**PDK 설치 확인:**

```bash
# Sky130B 확인
ls $PDK_ROOT/sky130B/libs.tech/ngspice/sky130.lib.spice

# RRAM 라이브러리 확인 (이것이 없으면 --enable-reram-sky130 빠진 것)
ls $PDK_ROOT/sky130B/libs.ref/sky130_fd_pr_reram/

# OSDI 모델 확인
ls $PDK_ROOT/sky130B/libs.tech/combined/sky130_fd_pr_reram__reram_module.osdi
```

**핵심 주의사항: sky130B→sky130A 절대경로 심볼릭 링크**

sky130B 내부 파일들이 sky130A로 **절대경로 심볼릭 링크** 되어 있습니다:
```
sky130B/libs.ref/sky130_fd_pr/ → /home/user/pdk/share/pdk/sky130A/libs.ref/...
```
따라서:
- Docker에서 PDK를 마운트할 때 **호스트와 동일한 경로**를 사용해야 합니다
- 다른 사용자/경로에서 사용하려면 PDK를 해당 prefix로 **재빌드** 해야 합니다

#### 0-3. 추가 도구 설치

```bash
# Magic VLSI (레이아웃 + DRC + SPICE 추출)
# Ubuntu 패키지 또는 소스 빌드
sudo apt-get install magic    # 또는 소스에서 빌드 (8.3.x 권장)
magic --version               # → 8.3 revision 599+

# netgen (LVS 검증)
sudo apt-get install netgen-lvs
# 또는 소스: https://github.com/RTimothyEdwards/netgen

# ngspice-43 (d_cosim co-simulation, OSDI 모델에 필요)
# 자동 설치: ./setup/install_ngspice.sh
# 수동 빌드: setup/patches/verilator_shim.patch 참조

# Verilator (d_cosim용 Verilog→C++ 컴파일러, co-sim에만 필요)
sudo apt-get install verilator    # >= 5.x

# xschem (회로도 편집, GUI 필요 시에만)
```

---

### Phase 1: RRAM 셀 DRC 수정

PDK 원본 `sky130_fd_pr_reram__reram_cell.gds`에 **DRC 위반 160개** 존재.

**문제:**
```
ReRAM marker (201/20): 320×320 nm
Metal1 (68/20):        320×260 nm ← Y방향 30nm surround 미충족
Metal2 (69/20):        260×320 nm ← X방향 30nm surround 미충족
DRC 룰: surround reram *m1 30 (사방 30nm 이상 감싸야 함)
```

**해결:** Metal1/2를 390×390nm으로 확장 (35nm overlap 확보)

```bash
cd $PROJECT_ROOT/reram_cell_fixed/scripts

# Python 가상환경 (gdsfactory, klayout 필요)
python3 -m venv ~/venv_gds && source ~/venv_gds/bin/activate
pip install gdsfactory klayout

# 1. DRC 수정된 ReRAM 셀 생성
python3 01_generate_reram_cell.py
# → sky130_fd_pr_reram__reram_cell_new.gds

# 2. 기존 1T1R 셀의 RRAM 부분 교체
python3 02_fix_1t1r_cell.py
# → RRAM_1T1R_new_fixed.gds (DRC clean)

# 3. 4x4 배열 생성
python3 03_generate_array.py
# → rram_4x4_array_fixed.gds
```

---

### Phase 2: RRAM 4×4 Array GDS/LEF 생성

수정된 1T1R 셀로 최종 매크로 GDS + LEF를 생성합니다.

```bash
cd $PROJECT_ROOT/openlane
python3 generate_array_and_lef_v1.py
# → gds/rram_4x4_array.gds (17.83 × 21.77 um)
# → lef/rram_4x4_array.lef
```

**`generate_array_and_lef_v1.py` (594줄) 핵심:**

| 항목 | 값 |
|------|-----|
| 셀 수 | 16개 1T1R (4×4) |
| Pitch | X=4.0um, Y=5.5um |
| Margin | 3.0um |
| 최종 크기 | 17.83 × 21.77 um |
| Grid | 0.005um (Sky130 제조 grid) |

**배선 구조:**
```
WL[3:0] — Metal3, 수직 (via2 스택으로 각 행 연결)
BL[3:0] — Metal3, 수직 (via2 스택으로 각 행 연결)
SL[3:0] — Metal2, 수평 (via1으로 각 열 연결)
GND     — Metal1, 수평 bar (행별) + 수직 bus (좌측)
```

**핵심 처리:**
- GDS 원점 (0,0) 정렬 필수 (LEF 좌표 일치)
- LEF OBS: 핀 영역을 제외하여 라우터 접근 허용
- Met3 핀 패드 0.5×0.5um ≥ Sky130 minimum area 0.24um²

---

### Phase 3: RRAM 셀 LVS 포트 수정 (.mag 파일)

Phase 2에서 DRC는 통과했지만 **LVS 68개 에러** 발생 (52 NET + 16 DEVICE).

**원인:** PDK의 `sky130_fd_pr_reram__reram_cell.mag` 파일에 **포트 정의 없음**
→ Magic이 SPICE 추출 시 `TE, BE` 대신 `1, 2`로 추출 → 넷리스트 불일치

**해결:** 포트 정의가 포함된 `.mag` 파일 작성 (22줄)

```
sky130_fd_pr_reram__reram_cell.mag:

<< labels >>
flabel metal2 s -39 -39 39 39 0 FreeSans 160 0 0 0 TE
port 0 nsew                  ← TE (Top Electrode) = port 0, metal2
flabel metal1 s -39 -39 39 39 0 FreeSans 160 0 0 0 BE
port 1 nsew                  ← BE (Bottom Electrode) = port 1, metal1
```

**사용법:** Magic 추출 전에 이 `.mag` 파일을 작업 디렉토리에 복사
```bash
cp openlane/sky130_fd_pr_reram__reram_cell.mag /path/to/extraction/directory/
```

→ **68개 에러 전부 해결, LVS PASS**

---

### Phase 4: 디지털 RTL 설계 (Verilog)

RRAM 4×4 어레이를 제어하는 FSM 컨트롤러 + Top 모듈.

```
openlane/src/
├── rram_ctrl_top.v     (82줄)  — Top 모듈, BL tristate bus 관리
├── controller.v        (162줄) — 6-state FSM (IDLE→DECODE→READ/WRITE→DONE)
├── row_decoder.v       (15줄)  — 2→4 디코더 (shift 기반)
├── col_decoder.v       (15줄)  — 2→4 디코더
└── rram_blackbox.v     (15줄)  — RRAM 매크로 blackbox 선언
```

**FSM 핵심:**
- `wl_sel <= (4'b0001 << row_reg)` — shift 기반 implicit row decoder
- `sl_sel <= (4'b0001 << row_reg)` — 개별 SL 제어 (v19 수정)
- READ: 4 cycle 대기 (SA settling), WRITE: 8 cycle 대기 (RRAM programming)
- BL tristate: `bl_bus[i] = bl_en[i] ? bl_data[i] : 1'bz`

**v18→v19 수정 (중요):**
v18에서 `sl_sel <= 4'b1111`으로 모든 SL을 동시 활성화 → 합성기가 단일 신호로 최적화.
v19에서 `sl_sel <= (4'b0001 << row_reg)`으로 개별 제어 수정.

---

### Phase 5: OpenLane 빌드 & DRC/LVS PASS

```bash
cd $PROJECT_ROOT/openlane

# OpenLane 실행 (Docker)
# ⚠️ PDK 마운트: 호스트와 동일 경로 필수 (sky130B→sky130A 심볼릭 링크 때문)
docker run --rm \
  -v $(pwd):/openlane/designs/rram_ctrl \
  -v $PDK_ROOT:$PDK_ROOT \
  -e PDK_ROOT=$PDK_ROOT \
  -e PDK=sky130B \
  efabless/openlane:v1.1.1 \
  flow.tcl -design /openlane/designs/rram_ctrl

# 결과 확인
cat runs/*/reports/signoff/drc.rpt          # DRC 0 errors
cat runs/*/reports/signoff/*lvs.rpt         # Total errors = 0
ls runs/*/results/final/gds/rram_ctrl_top.gds  # 최종 GDS
```

**config.json 핵심 설정:**

| 설정 | 값 | 설명 |
|------|-----|------|
| DIE_AREA | 0 0 160 160 | 160×160um |
| CLOCK_PERIOD | 50 | 20MHz |
| EXTRA_LEFS | rram_4x4_array.lef | RRAM 매크로 |
| EXTRA_GDS_FILES | rram_4x4_array.gds | RRAM 매크로 |
| MACRO_PLACEMENT_CFG | `u_rram_array 70 60 N` | 매크로 위치 |

**빌드 결과:**

| 항목 | 결과 |
|------|------|
| DRC (Magic) | 0 errors |
| LVS | Circuits match uniquely (179 devices, 175 nets) |
| Timing (Setup) | Slack +37.51ns (50ns period) |
| Hold / Antenna | No violations |

---

### Phase 6: 아날로그 블록 설계 (xschem + ngspice)

3개 아날로그 블록 schematic 설계 및 시뮬레이션 검증.

| 블록 | 파일 | 트랜지스터 | 핀 | 기능 |
|------|------|-----------|-----|------|
| WL Driver | `xschem/wl_driver.sch` | 8T (2×1.8V + 6×HV) | IN,OUT,VDD,VWL,VSS | 1.8V→VWL 레벨시프터 + HV 버퍼 |
| Sense Amp | `xschem/sense_amp.sch` | 10T (all 1.8V) | SAE,INP,INN,Q,QB,VDD,VSS | StrongARM latch, 50mV→1.8V |
| BL Write Driver | `xschem/bl_write_driver.sch` | 8T (all 1.8V) | EN,DATA,BL,VDD,VSS | Tri-state buffer, 1.774V |

**시뮬레이션:**
```bash
cd $PROJECT_ROOT/analog/sim

# SA 단독 (50mV differential → full-swing)
ngspice -b sense_amp_tb.spice

# BL Write Driver (EN=1→BL=DATA, EN=0→Hi-Z)
ngspice -b bl_write_driver_tb.spice

# 2-Layer XOR inference (4/4 PASS)
bash run_xor_2layer.sh
```

**2-Layer XOR 아키텍처:**
```
XOR(A,B) = AND( OR(A,B), NAND(A,B) )

Layer 1: Array1(bias=0.9V) → SA1 → h1(OR)
         Array2(bias=1.5V) → SA2 → h2(NAND)
Layer 2: Array3(bias=1.35V, inputs=h1,h2) → SA1 → y_xor
```

- 3개 RRAM 4×4 어레이, 12개 WL Driver, 6개 SA
- Input encoding: logic 0 = 0.6V (0V 아님, SA input pair Vth 확보)
- Balanced column 필수 (각 BL 컬럼 = 2 LRS + 2 HRS)
- 상세: [analog/README.md](analog/README.md)

---

### Phase 7: d_cosim Mixed-Signal Co-Simulation

디지털 FSM(Verilog)과 아날로그 블록(SPICE)의 closed-loop co-simulation.
ngspice `d_cosim` XSPICE 코드모델 + Verilator 사용.

```bash
cd $PROJECT_ROOT/analog/sim/cosim

# 1. Verilog → .so 컴파일 (vlnggen)
cd verilog
$NGSPICE -- "$VLNGGEN" \
  -Wno-CASEINCOMPLETE controller_cosim.v controller.v
cp controller_cosim.so ../
cd ..

# 2. Co-sim 실행
$NGSPICE -b rram_cosim_full.spice

# 3. 파형 플롯
python3 plot_cosim_full.py
```

**검증 시나리오:** READ → WRITE → Verify READ (전체 FSM closed-loop)

**주의:** ngspice-43 소스 빌드 필요 (d_cosim + KLU + OSDI), verilator_shim.cpp 버그 2개 수정 포함.
상세: [analog/README.md](analog/README.md) (d_cosim 섹션)

---

### Phase 8: 아날로그 레이아웃 (Magic VLSI)

3개 블록 전부 Magic Tcl batch scripting으로 레이아웃 생성.
Sky130B PDK `_draw` 함수로 디바이스 생성, 수동 배선 + tap 추가.

```bash
cd $PROJECT_ROOT/analog/layout

# 각 블록: (1) 레이아웃 생성 → (2) 탭 추가 → (3) flatten+추출 → (4) LVS
# 예: BL Write Driver
cd bl_write_driver
magic -noconsole -dnull -rcfile $PDK_ROOT/sky130B/libs.tech/magic/sky130B.magicrc \
  < bl_write_driver.tcl
magic -noconsole -dnull -rcfile $PDK_ROOT/sky130B/libs.tech/magic/sky130B.magicrc \
  < ../add_taps.tcl
netgen -batch lvs \
  "bl_write_driver_flat.spice bl_write_driver_flat" \
  "bl_write_driver_sch.spice bl_write_driver" \
  $PDK_ROOT/sky130B/libs.tech/netgen/sky130B_setup.tcl \
  lvs_report.txt
```

**결과:**

| 블록 | 트랜지스터 | PDK 디바이스 | DRC | LVS |
|------|-----------|-------------|-----|-----|
| BL Write Driver | 8T (4P+4N) | pfet/nfet_01v8 | 0 errors | PASS |
| Sense Amplifier | 10T (5P+5N) | pfet/nfet_01v8 | 0 errors | PASS |
| WL Driver | 8T (4P+4N) | pfet/nfet_01v8 + g5v0d10v5 | 0 errors | PASS |

**핵심 교훈:** met1 bridge가 디바이스 gate met1과 겹치면 **단락 발생**.
특히 large W 디바이스(W=4)는 gate met1이 예상보다 멀리 확장됨 → 좌표 정밀 확인 필수.

상세: [analog/layout/README.md](analog/layout/README.md)

---

### Phase 9: Liberty Characterization (ngspice)

각 블록에 대해 ngspice 시뮬레이션 기반 정식 Liberty (.lib) 파일 생성.
Python multiprocessing 16코어 병렬, 7×7 sweep (input_slew × output_load).

```bash
cd $PROJECT_ROOT/analog/layout
(cd bl_write_driver && python3 char_bl_write_driver.py)   # ~10분, 197 sims
(cd sense_amp && python3 char_sense_amp.py)               # ~5분, 100 sims
(cd wl_driver && python3 char_wl_driver.py)               # ~5분, 99 sims
```

**측정 조건:** Sky130B tt corner, 25°C, slew 0.01~1.65ns, load 0.5~316fF

**결과:**

| 블록 | Timing Arcs | 주요 delay | .lib 파일 |
|------|-------------|-----------|----------|
| BL Write Driver | DATA→BL (pos), EN→BL (3state) | 0.07~1.09 ns | `bl_write_driver/bl_write_driver.lib` |
| Sense Amplifier | SAE→Q/QB (neg, eval+prech) | 0.05~5.11 ns | `sense_amp/sense_amp.lib` |
| WL Driver | IN→OUT (pos, 1.8V→3.3V) | 0.26~1.84 ns | `wl_driver/wl_driver.lib` |

**LEF/LIB 일괄 생성:**
```bash
cd $PROJECT_ROOT/analog/layout
bash gen_all.sh
```

---

### Phase 10: 남은 작업

| 항목 | 상태 | 설명 |
|------|------|------|
| XOR inference FSM | ✅ 완료 | xor_controller.v (2-phase) |
| Input Encoder | ✅ 완료 | input_encoder.v |
| SAE Control | ✅ 완료 | sae_control.v |
| Blackbox Verilog | ✅ 완료 | WL Driver, SA, BL WD blackbox 통합 |
| 2-Array OpenLane PnR | ✅ 완료 | DRC=0, LVS=0, Timing clean |
| Post-Layout Co-Sim | ✅ 완료 | XOR 4/4 PASS (layout-extracted) |
| Caravan wrapper | 미완 | Efabless Caravan 칩 통합 |

---

## 폴더 구조

```
rram-xor-inference/
├── README.md                       # 프로젝트 개요
├── env.sh                          # 환경변수 정의
├── requirements.txt                # Python 의존성
│
├── setup/                          # 환경 설치 스크립트
│   ├── install_all.sh              # 원클릭 전체 설치
│   ├── install_deps.sh             # 시스템 패키지
│   ├── install_pdk.sh              # Sky130 PDK 빌드
│   ├── install_ngspice.sh          # ngspice-43 빌드
│   └── patches/verilator_shim.patch
│
├── openlane/                       # ✅ OpenLane RTL-to-GDS
│   ├── src/                        # Verilog RTL
│   │   ├── rram_ctrl_top.v         #   Top 모듈 (21 매크로 통합)
│   │   ├── xor_controller.v        #   XOR inference FSM
│   │   ├── input_encoder.v         #   Phase별 SL 생성
│   │   ├── sae_control.v           #   SA enable 타이밍
│   │   └── *_blackbox.v            #   매크로 blackbox 선언
│   ├── gds/, lef/, lib/            # 매크로 GDS/LEF/LIB
│   ├── config.json                 # OpenLane 설정
│   ├── config/macro_placement.cfg  # 21 매크로 배치
│   ├── run_openlane.sh             # Docker 실행 스크립트
│   └── scripts/fix_lvs_vpb.sh
│
├── analog/                         # ✅ 아날로그 설계 + 시뮬레이션
│   ├── xschem/                     # 회로도 (.sch)
│   ├── layout/                     # 레이아웃 + GDS/LEF/LIB
│   ├── sim/                        # 시뮬레이션
│   │   ├── cosim/                  # d_cosim co-simulation
│   │   ├── postsim/               # Post-layout 결과 정리
│   │   └── postlayout/            # Schematic vs Layout 비교
│   └── pic/                        # 회로도 이미지
│
├── reram_cell_fixed/               # RRAM 셀 DRC 수정
│
└── docs/                           # 상세 문서
    ├── ARCHITECTURE.md
    ├── PROJECT_GUIDE.md            # ⭐ 이 파일
    └── VERIFICATION.md
```

---

## Quick Start (새 환경에서 재현)

```bash
# 1. 레포 클론
git clone https://github.com/smhong1514/rram-xor-inference.git
cd rram-xor-inference

# 2. 환경 설정 (env.sh 수정 후)
source env.sh

# 3. 전체 설치 (PDK + ngspice + 시스템 패키지)
./setup/install_all.sh

# 4. XOR co-simulation 실행
cd analog/sim/cosim
./run_xor_cosim.sh

# 5. OpenLane 빌드 (선택)
cd $PROJECT_ROOT/openlane
./run_openlane.sh
```

---

## 도구 버전 요약

| 도구 | 버전 | 용도 |
|------|------|------|
| OpenLane | 1.1.1 (efabless/openlane:v1.1.1) | RTL-to-GDS |
| open_pdks | commit `bdc9412b` | PDK 소스 (Sky130B + RRAM) |
| Magic | 8.3 revision 599+ | 레이아웃, DRC, SPICE 추출 |
| netgen | Sky130B setup | LVS 검증 |
| ngspice | 42+ (기본), 43 (d_cosim) | SPICE 시뮬레이션 |
| Verilator | 5.x | Verilog→C++ (d_cosim용) |
| xschem | latest | 회로도 편집 (선택) |
| Python | 3.x | characterization, 파형 플롯 |
| gdsfactory | latest | RRAM 셀/어레이 GDS 생성 |

---

## 핵심 교훈 & 트러블슈팅

### PDK 관련
- **volare 사용 금지** → open_pdks 직접 빌드
- **`--enable-reram-sky130`** 필수 (기본값에서 RRAM 라이브러리 빠짐)
- **PDK 버전 매칭**: OpenLane 1.1.1 → open_pdks commit `bdc9412b`
- **Docker PDK 마운트**: 호스트와 동일 경로 사용 (sky130B→sky130A 절대경로 symlink)

### RRAM 매크로 관련
- **RRAM 셀 .mag 포트**: PDK 원본에 TE/BE 포트 정의 없음 → 수동 추가 필요
- **GDS 원점**: 반드시 (0,0) 정렬 (LEF 좌표 일치)
- **LEF OBS**: 핀 영역 제외해야 라우터 접근 가능

### 아날로그 설계 관련
- **SA precharge 극성**: PMOS gate = SAE 직접 연결 (inverter 불필요, PMOS는 active-low)
- **xschem wire 연결**: endpoint가 상대 wire 위에 있어야 T-junction (단순 교차 ≠ 연결)
- **met1 bridge 단락**: 디바이스 gate met1 좌표 확인 후 tap 배치 (large W 주의)

### XOR 신경망 관련
- **XOR는 비선형** → 1-layer로 불가, 2-layer 분해 필요: XOR = AND(OR, NAND)
- **Input 0 = 0.6V** (0V 아님) → SA input pair Vth 확보
- **Balanced column** 필수 → 각 BL 컬럼 = 2 LRS + 2 HRS

---

## 라이선스

교육 및 연구 목적으로 제공됩니다.
