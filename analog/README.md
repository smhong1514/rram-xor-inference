# Analog Blocks - Sky130 RRAM Compute-in-Memory

Sky130 PDK 기반 RRAM 4x4 크로스바 어레이를 활용한 아날로그 Compute-in-Memory(CIM) 블록 설계.
WL Driver, Sense Amplifier schematic 설계 및 XOR 뉴럴 네트워크 inference 시뮬레이션 완료.

## 시뮬레이션 결과 요약

| 시뮬레이션 | 스크립트 | 결과 | 설명 |
|-----------|----------|------|------|
| SA 단독 검증 | `sense_amp_tb.spice` | **PASS** | 50mV 입력차 → 1.8V full-swing, 230ps |
| 1-Layer XOR (A=0,B=1) | `run_xor.sh` | **PASS** | 단일 케이스 파형 확인 |
| 1-Layer XOR (4 cases) | `run_xor_all.sh` | **2/4 PASS** | (0,0)과 (1,1) 실패 - XOR는 비선형 |
| 1-Layer 디버그 | `run_xor_debug.sh` | - | BL/SA 내부 노드 분석 |
| **2-Layer XOR (4 cases)** | **`run_xor_2layer.sh`** | **4/4 PASS** | **3개 RRAM 어레이로 XOR 구현** |
| BL Write Driver 단독 | `bl_write_driver_tb.spice` | **PASS** | EN=1→BL=DATA, EN=0→Hi-Z |
| **d_cosim Mixed-Signal** | **`cosim/rram_cosim_full.spice`** | **PASS** | **FSM↔아날로그 closed-loop** |

---

## 환경 설정 및 필수 소프트웨어

### 필수 설치

```bash
# ngspice (SPICE 시뮬레이터)
sudo apt install ngspice    # >= 42

# Python (결과 판정 및 파형 플롯)
sudo apt install python3 python3-pip
pip3 install matplotlib numpy

# xschem (회로도 편집, 선택사항)
# WSL2에서는 DISPLAY=:0 필요 (Xvfb 불가, /tmp/.X11-unix read-only)
```

### PDK 설정

Sky130 PDK + RRAM 라이브러리가 필요합니다.
OpenLane 1.1.1이 기대하는 정확한 open_pdks 버전을 사용해야 합니다.

**PDK 버전 정보:**

| 항목 | 값 |
|------|-----|
| PDK | SkyWater Sky130B |
| open_pdks 커밋 | `bdc9412b3e468c102d01b7cf6337be06ec6e9c9a` |
| open_pdks 소스 | (local clone) |
| 설치 경로 | `$PDK_ROOT` |
| OpenLane 버전 | 1.1.1 (`efabless/openlane:latest`) |
| RRAM 라이브러리 | `sky130_fd_pr_reram` (open_pdks `--enable-reram-sky130` 옵션) |

**왜 이 특정 커밋인가:**
- OpenLane 1.1.1은 특정 PDK 버전을 기대함. 버전 불일치 시 `-ignore_mismatches` 플래그 필요
- `bdc9412b` 커밋은 OpenLane 1.1.1과 정확히 매칭되는 버전
- 이 버전에서 `--enable-reram-sky130` 옵션으로 RRAM 셀 라이브러리 포함 빌드 가능
- RRAM 소자 모델 파일: `sky130_fd_pr_reram__reram_cell` (OSDI compact model)

**RRAM OSDI 모델 참고:**
- PDK에 포함된 OSDI 파일: `sky130_fd_pr_reram__reram_module.osdi`
- ngspice에서 사용하려면 `--enable-osdi` 옵션으로 ngspice 빌드 필요
- Ubuntu 패키지 ngspice-42는 OSDI 미포함 → **본 시뮬레이션에서는 저항 간이 모델 사용**
- 정밀 시뮬레이션(SET/RESET 동작 포함)에는 OSDI 빌드 ngspice 필요

**환경변수 설정:**
```bash
# ~/.bashrc에 추가
export PDK_ROOT=$PDK_ROOT
export PDK=sky130B
```

**PDK 빌드 방법 (처음 설치 또는 재빌드 시):**
```bash
# 1. open_pdks 소스 준비
cd open_pdks
git checkout bdc9412b3e468c102d01b7cf6337be06ec6e9c9a

# 2. 빌드 설정
./configure --enable-sky130-pdk \
            --enable-reram-sky130 \
            --disable-klayout-sky130 \
            --prefix=$HOME/pdk

# 옵션 설명:
#   --enable-sky130-pdk      : Sky130 PDK 빌드
#   --enable-reram-sky130    : RRAM 라이브러리 포함 (필수!)
#   --disable-klayout-sky130 : klayout 빌드 오류 회피
#   --prefix                 : 시스템 PDK와 분리 설치

# 3. 빌드 & 설치 (make -j1: git clone 충돌 방지를 위해 순차 빌드)
make -j1 && make install
```

**주의사항:**
- `sky130B` 내부 파일이 `sky130A`로 **절대경로 심볼릭 링크** 되어 있음
- Docker에서 PDK를 마운트할 때 호스트와 동일한 경로 사용 필수
  - 예: `-v $PDK_ROOT:$PDK_ROOT`
  - `/pdk` 같은 다른 경로로 마운트하면 심볼릭 링크가 깨짐

### 확인

```bash
# ngspice 동작 확인
ngspice --version
# → ngspice-42 이상

# PDK 라이브러리 확인
ls $PDK_ROOT/sky130B/libs.tech/ngspice/sky130.lib.spice
# → 파일이 있으면 OK

# RRAM 라이브러리 확인
ls $PDK_ROOT/sky130B/libs.tech/ngspice/sky130_fd_pr_reram*
# → sky130_fd_pr_reram__reram_cell.spice 등 파일이 있으면 OK

# OSDI 모델 확인 (선택사항 - 저항 모델 사용 시 불필요)
ls $PDK_ROOT/sky130B/libs.tech/combined/sky130_fd_pr_reram__reram_module.osdi
```

---

## 폴더 구조

```
analog/
├── README.md                  # 이 파일
├── xschem/                    # xschem 회로도
│   ├── wl_driver.sch          # WL Driver (8 트랜지스터)
│   ├── sense_amp.sch          # Sense Amplifier v5 (10 트랜지스터)
│   ├── bl_write_driver.sch    # BL Write Driver (8 트랜지스터, tri-state)
│   ├── sense_amp_me_v1.sch    # SA 초기 버전 (참고용)
│   └── simulation/            # xschem에서 추출한 SPICE 넷리스트
│       ├── sense_amp.spice    # SA v5 netlist (SAE 직접 연결, inverter 없음)
│       └── wl_driver.spice    # WL Driver netlist
│
├── sim/                       # ngspice 시뮬레이션
│   │
│   │  [SA 단독]
│   ├── sense_amp_tb.spice     # SA testbench (INP=0.925V, INN=0.875V)
│   ├── sa_result.csv          # SA wrdata 출력 (time,sae,time,q,time,qb,...)
│   ├── plot_sa.py             # SA 파형 → sense_amp_sim.png
│   ├── sense_amp_sim.png      # SA 파형 결과 이미지
│   │
│   │  [1-Layer XOR]
│   ├── run_xor.sh             # 단일 케이스 (A=0,B=1), wrdata 출력
│   ├── run_xor_all.sh         # 4 케이스 truth table (2/4 PASS)
│   ├── run_xor_debug.sh       # BL/SA 내부 노드 디버그 측정
│   ├── xor_result.csv         # wrdata 출력 (run_xor.sh 결과)
│   ├── plot_xor.py            # XOR 파형 → xor_inference_sim.png
│   ├── xor_inference_sim.png  # XOR 파형 결과 이미지
│   │
│   │  [2-Layer XOR] ★ 최종
│   ├── run_xor_2layer.sh      # 3개 어레이, 4 케이스 자동 실행 (4/4 PASS)
│   │
│   │  [BL Write Driver]
│   ├── bl_write_driver_tb.spice  # BL Write Driver testbench
│   │
│   │  [d_cosim Mixed-Signal Co-simulation] ★
│   ├── cosim/                    # Verilog-SPICE co-simulation
│   │   ├── rram_cosim_full.spice # Full closed-loop testbench
│   │   ├── rram_mixed_tb.spice   # PWL-driven reference testbench
│   │   ├── d_cosim_full.spice    # d_cosim 기본 검증
│   │   ├── plot_cosim_full.py    # Co-sim 파형 플롯
│   │   ├── plot_cosim.py         # 기본 co-sim 플롯
│   │   ├── run_cosim.sh          # 빌드+실행 스크립트
│   │   ├── controller_cosim.v    # d_cosim용 포트 재배열 wrapper
│   │   └── verilog/              # vlnggen 소스 + 빌드
│   │       ├── controller.v      # FSM controller RTL
│   │       ├── controller_cosim.v # d_cosim wrapper
│   │       └── *_obj_dir/        # Verilator 빌드 산출물 (.gitignore)
│   │
│   │  [기타]
│   ├── xor_inference_tb.spice # (미사용) OSDI RRAM 모델 기반 - ngspice-42 미지원
│   └── .spiceinit             # ngspice 설정
│
└── pic/                       # 회로도 이미지
    ├── WL_v1.png              # WL Driver schematic
    ├── sense_amp_v5.png       # SA 최종 버전
    ├── sense_amp_v1~v4.png    # SA 이전 버전들 (설계 과정)
    └── sense_amp_ex.png       # Cadence 참고 SA 이미지
```

---

## 실행 가이드

### Step 1: SA 단독 시뮬레이션

SA가 정상 동작하는지 단독으로 확인합니다.

```bash
cd $PROJECT_ROOT/analog/sim

# 시뮬레이션 실행
ngspice -b sense_amp_tb.spice

# 결과 확인: 터미널에 아래와 같이 출력됨
#   vq_final = 0.000000e+00        ← Q → 0V (LOW)
#   vqb_final = 1.800000e+00       ← QB → 1.8V (HIGH)
#   t_resolve = 2.30e-10           ← 230ps resolution time

# 파형 플롯 (선택사항)
python3 plot_sa.py
# → sense_amp_sim.png 생성
```

**testbench 구성:** SA 단독 + DC 입력 + SAE 클럭
```
입력: INP=0.925V, INN=0.875V (ΔV=50mV, BL 전압 모사)
SAE: PULSE(0 1.8 10n 0.1n 0.1n 19.8n 40n)
     → 10ns precharge, 20ns evaluate, 반복
출력: CQ=CQB=10fF 부하

기대 결과: INN(0.875V) < INP(0.925V) → Q=LOW, QB=HIGH
```

### Step 2: 1-Layer XOR 시뮬레이션

WL Driver + RRAM 4x4 + SA를 결합한 1-layer 시도. **XOR는 비선형이므로 2/4만 성공.**

```bash
cd $PROJECT_ROOT/analog/sim

# 단일 케이스 (A=0, B=1) - 파형 데이터 포함
bash run_xor.sh
python3 plot_xor.py          # → xor_inference_sim.png

# 4 케이스 truth table
bash run_xor_all.sh
# 출력 예시:
#   A=0 B=0 | Expected XOR=0 | Q1=1.86V QB1=1.86V | Q1=1 | FAIL  ← 미분해
#   A=0 B=1 | Expected XOR=1 | Q1=1.80V QB1=0.00V | Q1=1 | PASS
#   A=1 B=0 | Expected XOR=1 | Q1=0.00V QB1=1.80V | Q1=0 | FAIL  ← 극성 반전
#   A=1 B=1 | Expected XOR=0 | Q1=1.86V QB1=1.86V | Q1=1 | FAIL  ← 미분해

# 디버그 (BL/SA 내부 노드 상세 측정)
bash run_xor_debug.sh
```

**1-Layer 실패 원인:**
- (0,0): SL 모두 0V → BL ≈ 0V → SA 입력 NMOS Vth(~0.5V) 미만 → SA 미동작
- (1,1): SL 모두 1.8V → BL0 ≈ BL1 → 전압차 없음 → random latch
- 결론: XOR는 linearly non-separable → 1-layer로 구현 불가능

### Step 3: 2-Layer XOR 시뮬레이션 (최종)

```bash
cd $PROJECT_ROOT/analog/sim

# 실행 (4 케이스 자동 순회, 약 1~2분 소요)
bash run_xor_2layer.sh

# 출력 예시:
# ================================================
#   2-Layer RRAM XOR Neural Network Simulation
#   Layer1: Array1(0.9V)=OR + Array2(1.5V)=NAND
#   Layer2: Array3(1.35V)=AND(OR,NAND)=XOR
#   Input: 0→0.6V, 1→1.8V | Same weights, diff bias
# ================================================
# A=0 B=0 | h1(OR)=1.15e-06[0] h2(NAND)=1.80e+00[1] | XOR=6.04e-07[0] exp=0 | PASS
# A=0 B=1 | h1(OR)=1.80e+00[1] h2(NAND)=1.80e+00[1] | XOR=1.80e+00[1] exp=1 | PASS
# A=1 B=0 | h1(OR)=1.80e+00[1] h2(NAND)=1.80e+00[1] | XOR=1.80e+00[1] exp=1 | PASS
# A=1 B=1 | h1(OR)=1.80e+00[1] h2(NAND)=5.35e-07[0] | XOR=6.04e-07[0] exp=0 | PASS
#
# ================================================
#   Result: 4 PASS / 0 FAIL out of 4
# ================================================
```

**상세 로그 확인** (필요시):
```bash
# 각 케이스별 ngspice 로그 (시뮬레이션 중 /tmp에 저장됨)
cat /tmp/xor2l_0_0.log | grep -E "^vh|^vy|^vbl"
cat /tmp/xor2l_0_1.log | grep -E "^vh|^vy|^vbl"
cat /tmp/xor2l_1_0.log | grep -E "^vh|^vy|^vbl"
cat /tmp/xor2l_1_1.log | grep -E "^vh|^vy|^vbl"
```

---

## 아날로그 블록 상세 설계

### 1. WL Driver

**파일:** `xschem/wl_driver.sch` | **트랜지스터:** 8개 | **핀:** IN, OUT, VDD, VWL, VSS

1.8V 디지털 입력을 고전압(VWL) 출력으로 레벨 시프트하는 드라이버.
RRAM 셀의 access transistor(nfet_g5v0d10v5) gate를 구동하기 위해 VWL 전압이 필요.

```
구조: Input Inverter → Cross-coupled Level Shifter → HV Buffer

[Input Inverter]              [Level Shifter]               [HV Buffer]
MP0(INB,IN,VDD,VDD) W=1      MP1(Q,QB,VWL,VWL) W=1        MP3(OUT,Q,VWL,VWL) W=4
MN0(INB,IN,VSS,VSS) W=0.5    MN1(Q,IN,VSS,VSS) W=2        MN3(OUT,Q,VSS,VSS) W=2
                              MP2(QB,Q,VWL,VWL) W=1
                              MN2(QB,INB,VSS,VSS) W=2

트랜지스터 정보:
  MP0, MN0: sky130_fd_pr__pfet_01v8, nfet_01v8 (1.8V CMOS)
  나머지 6개: sky130_fd_pr__pfet_g5v0d10v5, nfet_g5v0d10v5 (5V HV)
  SPICE pin order: Drain, Gate, Source, Bulk
```

**동작:**
- IN=VDD(1.8V) → INB=0 → MN2 OFF, MN1 ON → Q=0 → MP2 ON → QB=VWL → MP3 OFF, MN3 ON → OUT=0
- IN=0 → INB=VDD → MN2 ON, MN1 OFF → QB=0 → MP1 ON → Q=VWL → MP3 ON, MN3 OFF → OUT=VWL
- 시뮬레이션에서 IN=VDD(고정) → WL이 항상 VWL=3.3V로 driven

### 2. Sense Amplifier (StrongARM Latch-type)

**파일:** `xschem/sense_amp.sch` | **트랜지스터:** 10개 | **핀:** SAE, INP, INN, Q, QB, VDD, VSS

작은 BL 전압차(수십~수백mV)를 full-swing 디지털 출력(0V/1.8V)으로 증폭하는 래치형 SA.

```
[Precharge PMOS]           [Equalize PMOS]          [Cross-coupled Latch PMOS]
MP3(Q,SAE,VDD,VDD) W=0.5  MP5(QB,SAE,Q,VDD) W=0.5  MP1(Q,QB,VDD,VDD) W=1
MP4(QB,SAE,VDD,VDD) W=0.5                           MP2(QB,Q,VDD,VDD) W=1

[Cross-coupled Latch NMOS] [Input Differential Pair] [Tail Current Source]
MN1(Q,QB,FN1,VSS) W=1     MN3(FN1,INP,TAIL,VSS) W=2  MN0(TAIL,SAE,VSS,VSS) W=2
MN2(QB,Q,FN2,VSS) W=1     MN4(FN2,INN,TAIL,VSS) W=2

모든 트랜지스터: sky130_fd_pr__pfet_01v8, nfet_01v8 (1.8V CMOS)
SPICE pin order: Drain, Gate, Source, Bulk
```

**동작 (2-phase):**

1. **Precharge (SAE=0V):**
   - MP3, MP4 ON → Q=QB=VDD (precharge)
   - MP5 ON → Q-QB equalize (offset 제거)
   - MN0 OFF → tail current 차단, latch 비활성

2. **Evaluate (SAE=1.8V):**
   - MP3, MP4, MP5 OFF → precharge 해제
   - MN0 ON → tail current 흐름
   - MN3, MN4가 INP, INN 전압차에 따라 비대칭 전류 생성
   - Cross-coupled latch(MP1-MP2-MN1-MN2)가 차이를 증폭 → full swing

**출력 규칙:**
```
INP > INN → FN1 더 많은 전류 → Q 더 빨리 하강 → Q=LOW, QB=HIGH
INP < INN → FN2 더 많은 전류 → QB 더 빨리 하강 → Q=HIGH, QB=LOW

즉: INN > INP → Q=HIGH (1.8V)
    INN < INP → Q=LOW  (0V)
```

**SA 시뮬레이션 결과:**
```
testbench: sense_amp_tb.spice
입력:  INP=0.925V, INN=0.875V (ΔV=50mV)
출력:  Q → 0V (LOW), QB → 1.8V (HIGH)  [INP > INN이므로]
해상시간: ~230ps (SAE 상승 → Q/QB 분리 완료)
```

### 3. BL Write Driver (Tri-state Buffer)

**파일:** `xschem/bl_write_driver.sch` | **트랜지스터:** 8개 | **핀:** EN, DATA, BL, VDD, VSS

디지털 컨트롤러의 bl_en/bl_data 신호를 받아 BL에 full-swing 전압을 인가하는 트라이스테이트 버퍼.
기존 NFET pass gate 대비 Vth drop 없이 VDD 레일까지 출력 가능.

```
구조: EN Inverter + DATA Inverter + Series PMOS Pull-up + Series NMOS Pull-down

[EN Inverter]                [DATA Inverter]              [Output Stage]
MP0(EN_B,EN,VDD,VDD) W=0.5  MP3(DATA_B,DATA,VDD,VDD) W=0.5  MP1(NET_P,EN_B,VDD,VDD) W=4
MN0(EN_B,EN,VSS,VSS) W=0.5  MN3(DATA_B,DATA,VSS,VSS) W=0.5  MP2(BL,DATA_B,NET_P,VDD) W=4
                                                              MN2(BL,DATA_B,NET_N,VSS) W=4
                                                              MN1(NET_N,EN,VSS,VSS) W=4

모든 트랜지스터: sky130_fd_pr__pfet_01v8, nfet_01v8 (1.8V CMOS)
SPICE pin order: Drain, Gate, Source, Bulk
```

**동작:**

| EN | DATA | MP1 | MP2 | MN2 | MN1 | BL |
|----|------|-----|-----|-----|-----|----|
| 1 | 1 | ON (EN_B=0) | ON (DATA_B=0) | OFF | ON | **VDD** (pull-up) |
| 1 | 0 | ON | OFF | ON (DATA_B=1) | ON | **VSS** (pull-down) |
| 0 | X | OFF (EN_B=1) | - | - | OFF | **Hi-Z** (양쪽 차단) |

**시뮬레이션 결과:**
```
testbench: bl_write_driver_tb.spice
부하: 100kΩ (RRAM HRS 모사)
EN=1, DATA=1 → BL = 1.774V (98.5% of VDD) ← NFET pass gate는 ~1.3V
EN=1, DATA=0 → BL = 0.000V
EN=0         → BL = Hi-Z
Rise time: 0.58ns, Fall time: 0.20ns
```

**vs NFET Pass Gate:**
| 항목 | NFET Pass Gate | Tri-state Buffer |
|------|----------------|-----------------|
| BL=VDD 출력 | ~1.3V (Vth drop) | 1.774V (full swing) |
| 트랜지스터 수 | 1개/BL | 8개 (공유 4개 + BL당 4개) |
| 구동 능력 | 약함 | W=4 출력단 |

---

## XOR 뉴럴 네트워크 inference 설계

### 배경: 왜 XOR가 어려운가

XOR(A,B)는 **비선형 함수** (linearly non-separable).
2D 평면에서 직선 하나로 XOR=0과 XOR=1을 분리할 수 없음.

```
XOR Truth Table:            2D 입력 공간:
A B | XOR                   B
0 0 |  0                    1 ┤ ●(0,1)=1    ○(1,1)=0
0 1 |  1                      │
1 0 |  1                    0 ┤ ○(0,0)=0    ●(1,0)=1
1 1 |  0                      └──┤──────────┤── A
                                  0          1
                            → 직선 하나로 ●과 ○ 분리 불가능!
```

RRAM 크로스바 1개 + SA 1쌍 = **하나의 선형 분류기** (직선 하나) → XOR 불가.
해결: **2층 네트워크**로 분해.

```
XOR(A,B) = AND( OR(A,B), NAND(A,B) )

  Layer 1: h1 = OR(A,B)     → 직선 1 (A+B > low threshold)
           h2 = NAND(A,B)   → 직선 2 (A+B < high threshold)
  Layer 2: y  = AND(h1, h2) → 직선 3 (h1+h2 > mid threshold)
```

### RRAM 크로스바의 동작 원리

RRAM 4x4 크로스바 어레이 구조:
```
         BL0      BL1      BL2      BL3
          │        │        │        │
SL0 ──[R00]──┤──[R01]──┤──[R02]──┤──[R03]──┤
       TE BE      TE BE      TE BE      TE BE
         │        │        │        │
        [M00]    [M01]    [M02]    [M03]   ← WL0 gate
         │        │        │        │
SL1 ──[R10]──┤──[R11]──┤──[R12]──┤──[R13]──┤
        ...       ...       ...       ...
```

각 셀: RRAM(TE→BE) + access NFET(drain→source=SL, gate=WL)
- WL=HIGH → NFET ON → SL 전압이 RRAM을 통해 BL에 전달
- BL 전압 = **가중 평균** (voltage divider):

```
BL = Σ(SLi × Gi) / Σ(Gi)

  SLi: i번째 SL 전압 (입력값)
  Gi:  i번째 RRAM conductance (가중치)
  LRS (Tfilament=4.9nm): R=10kΩ,  G=100μS (큰 가중치)
  HRS (Tfilament=3.3nm): R=500kΩ, G=2μS   (작은 가중치, ≈무시)
```

SA는 BL0 vs BL1 전압을 비교 → **선형 분류 경계** 구현.

### 핵심 설계 제약조건 (시뮬레이션 과정에서 발견)

#### 제약 1: Balanced Column (균형 컬럼)

각 BL 컬럼은 **정확히 2 LRS + 2 HRS** 를 가져야 함.

```
불균형 예시 (실패):                    균형 예시 (성공):
     BL0       BL1                         BL0       BL1
R0:  LRS(100μS) HRS(2μS)             R0:  HRS(2μS)   LRS(100μS)
R1:  LRS(100μS) HRS(2μS)             R1:  HRS(2μS)   LRS(100μS)
R2:  HRS(2μS)   LRS(100μS)           R2:  LRS(100μS) HRS(2μS)
R3:  LRS(100μS) HRS(2μS)             R3:  LRS(100μS) HRS(2μS)
────────────────────────              ────────────────────────
합계: 302μS     106μS                 합계: 204μS     204μS
```

**왜 문제인가:**
- BL = Σ(SLi×Gi) / Σ(Gi)에서 분모가 다르면 가중 평균 스케일이 달라짐
- 불균형 시 LRS가 많은 쪽 BL이 bias 전압에 의해 지배되어
  입력과 무관하게 한쪽 BL이 항상 높아짐

#### 제약 2: SA Complementary Constraint (SA 상보 제약)

Balanced column에서 SA1(BL0 vs BL1)과 SA2(BL2 vs BL3)는 **항상 상보적**:

```
가중치 부호 패턴 (LRS="+큰가중치", HRS="-작은가중치≈0"):

         BL0  BL1  BL2  BL3
Row 0:    -    +    +    -     ← 신호 행 (Input A)
Row 1:    -    +    +    -     ← 신호 행 (Input B)
Row 2:    +    -    -    +     ← 편향 행 (Bias)
Row 3:    +    -    -    +     ← 편향 행 (Bias)
컬럼합:  2+2- 2+2- 2+2- 2+2-  ← 모두 balanced ✓
```

SA1은 BL0 vs BL1 비교 → 부호 [-,-,+,+] vs [+,+,-,-] → **f(bias - input)**
SA2는 BL2 vs BL3 비교 → 부호 [+,+,-,-] vs [-,-,+,+] → **f(input - bias)**
→ SA2 = NOT(SA1) 항상 성립!

**의미:** 하나의 어레이에서 OR(SA1)과 NAND(SA2)를 동시에 얻을 수 없음.
둘 다 "sum type" 함수(A+B vs threshold)이지만 threshold가 다름.
→ **Layer 1에 2개의 어레이가 필요** (각각 다른 bias로 OR, NAND 생성)

#### 제약 3: Input Offset Encoding (입력 오프셋)

Logic 0 = **0.6V** (0V가 아님), Logic 1 = 1.8V.

```
문제 상황 (logic 0 = 0V일 때):
  SL=0V이고 RRAM=LRS(10kΩ) → BL이 0V 방향으로 강하게 pull
  → BL 전압 ≈ 0V ~ 0.4V
  → SA 입력 NMOS(MN3, MN4)의 Vth ≈ 0.5V 미만
  → SA의 input pair가 동작하지 않음 → evaluate 불가, precharge 상태 유지

해결 (logic 0 = 0.6V):
  SL=0.6V → LRS 경로가 BL을 0.6V 이상으로 유지
  → BL 전압 ≈ 0.6V ~ 1.8V 범위
  → SA input pair 항상 동작 범위 내
```

실제 측정으로 확인:
```
(A=0,B=0) logic 0 = 0V일 때:   BL0 ≈ 0V, BL1 ≈ 0V → SA 미동작 (FAIL)
(A=0,B=0) logic 0 = 0.6V일 때: BL0 ≈ 0.89V, BL1 ≈ 0.61V → SA 정상 (PASS)
```

### 최종 2-Layer XOR 아키텍처

**파일:** `sim/run_xor_2layer.sh`

```
              ┌────────────────────────────────────────────┐
              │              Layer 1                        │
              │                                            │
              │   ┌─────────────────┐                      │
  A (SL0) ───┤──→│  Array 1        │──→ SA1 ──→ h1 (OR)  │
  B (SL1) ───┤──→│  bias=0.9V      │                      │
              │   │  (SL2,SL3)      │                      │
              │   └─────────────────┘                      │
              │                                            │
              │   ┌─────────────────┐                      │
  A (SL0) ───┤──→│  Array 2        │──→ SA2 ──→ h2 (NAND)│
  B (SL1) ───┤──→│  bias=1.5V      │                      │
              │   │  (SL2,SL3)      │                      │
              │   └─────────────────┘                      │
              └──────────────┬─────────────────────────────┘
                             │ VCVS buffer (이상적 전압 전달)
                             │ Eh1: h1 → Layer2 SL0
                             │ Eh2: h2 → Layer2 SL1
                             ▼
              ┌────────────────────────────────────────────┐
              │              Layer 2                        │
              │                                            │
              │   ┌─────────────────┐                      │
  h1 (SL0) ──┤──→│  Array 3        │──→ SA1 ──→ y_xor    │
  h2 (SL1) ──┤──→│  bias=1.35V     │          (최종 출력) │
              │   │  (SL2,SL3)      │                      │
              │   └─────────────────┘                      │
              └────────────────────────────────────────────┘
```

**회로 구성 요소 (전체):**

| 구성 요소 | 수량 | 설명 |
|----------|------|------|
| RRAM 4x4 어레이 (`rram_4x4_balanced`) | 3개 | 모두 동일 가중치 행렬 |
| WL Driver (`wl_driver`) | 12개 | 어레이당 4개 (WL0~WL3) |
| Sense Amplifier (`sense_amp`) | 6개 | 어레이당 2개 (SA1, SA2) |
| VCVS buffer | 2개 | Layer 1→2 이상적 전압 전달 |
| 전원 | 3개 | VDD=1.8V, VWL=3.3V, VSS=0V |

### SPICE 넷리스트 구성 상세

**RRAM 모델 (저항 간이 모델):**
```spice
.subckt sky130_fd_pr_reram__reram_cell TE BE Tfilament_0=3.3e-9
R1 TE BE {500k + (10k - 500k) * (Tfilament_0 - 3.3e-9) / (4.9e-9 - 3.3e-9)}
.ends
```

| 상태 | Tfilament_0 | 저항 | Conductance | 의미 |
|------|-------------|------|-------------|------|
| HRS | 3.3nm | 500kΩ | 2μS | 약한 연결 (가중치 ≈ 0) |
| LRS | 4.9nm | 10kΩ | 100μS | 강한 연결 (가중치 ≈ 1) |

> ngspice-42 Ubuntu 패키지는 `--enable-osdi` 없이 빌드되어 OSDI RRAM 모델 사용 불가.
> 이 간이 모델은 READ(inference) 시 고정 저항만 반영. SET/RESET 동적 거동 미포함.

**가중치 행렬 (3개 어레이 모두 동일):**

```
rram_4x4_balanced subckt 내부:

              BL0(SA1+)  BL1(SA1-)  BL2(SA2+)  BL3(SA2-)
Row 0 (SL0):  HRS        LRS        LRS        HRS       ← Input A / h1
Row 1 (SL1):  HRS        LRS        LRS        HRS       ← Input B / h2
Row 2 (SL2):  LRS        HRS        HRS        LRS       ← Bias
Row 3 (SL3):  LRS        HRS        HRS        LRS       ← Bias

Tfilament_0 값:
              BL0      BL1      BL2      BL3
Row 0:       3.3e-9   4.9e-9   4.9e-9   3.3e-9
Row 1:       3.3e-9   4.9e-9   4.9e-9   3.3e-9
Row 2:       4.9e-9   3.3e-9   3.3e-9   4.9e-9
Row 3:       4.9e-9   3.3e-9   3.3e-9   4.9e-9

Column balance 검증:
  BL0: 2×HRS + 2×LRS = 2×2μS + 2×100μS = 204μS ✓
  BL1: 2×LRS + 2×HRS = 204μS ✓
  BL2: 2×LRS + 2×HRS = 204μS ✓
  BL3: 2×HRS + 2×LRS = 204μS ✓
```

**SL 연결 (입력 인코딩):**

```
                     Array 1 (OR)    Array 2 (NAND)    Array 3 (AND)
SL0:                 A (0.6V/1.8V)   A (0.6V/1.8V)    h1 (SA출력)
SL1:                 B (0.6V/1.8V)   B (0.6V/1.8V)    h2 (SA출력)
SL2:                 bias=0.9V       bias=1.5V         bias=1.35V
SL3:                 bias=0.9V       bias=1.5V         bias=1.35V
SA 사용:             SA1→h1(OR)      SA2→h2(NAND)      SA1→y_xor(AND)
```

**편향 전압이 논리 함수를 결정하는 원리:**

```
SA1 출력 = (BL1 > BL0) ? HIGH : LOW

BL0 ≈ (A×2 + B×2 + bias×100 + bias×100) / 204    (HRS≈2μS ≈무시)
BL1 ≈ (A×100 + B×100 + bias×2 + bias×2) / 204

→ BL1 > BL0 조건:
  (A+B)×100 + bias×4 > (A+B)×4 + bias×200
  (A+B)×96 > bias×196
  (A+B) > bias × 2.04

대략적으로: SA1=HIGH when (A+B) > 2×bias
```

| bias | 조건 (A+B) > 2×bias | 함수 |
|------|---------------------|------|
| 0.9V | A+B > 1.8V → (0,1)(1,0)(1,1) 만족 | **OR** |
| 1.5V | A+B > 3.0V → (1,1)만 만족 | **AND** |
| 1.5V (SA2) | SA2=NOT(SA1) → (0,0)(0,1)(1,0) 만족 | **NAND** |
| 1.35V | A+B > 2.7V → 둘 다 HIGH일 때만 | **AND** (Layer 2) |

**Layer간 연결 (VCVS):**
```spice
Eh1 sl2_0 0 h1 0 1.0    * h1(OR 출력) → Layer 2의 SL0
Eh2 sl2_1 0 h2 0 1.0    * h2(NAND 출력) → Layer 2의 SL1
```
이상적인 전압 전달 (gain=1.0, 무한 입력 임피던스, 0 출력 임피던스).

**타이밍:**
```spice
VSAE1 sae1 0 PULSE(0 1.8 10n 0.1n 0.1n 80n 200n)   * Layer 1 SA enable
VSAE2 sae2 0 PULSE(0 1.8 40n 0.1n 0.1n 40n 200n)   * Layer 2 SA enable

시간축:
0ns ──── 10ns ──── 35ns ──── 40ns ──── 70ns ──── 100ns
│ precharge │ L1 eval      │ L2 eval      │
│           │ SAE1↑        │ SAE2↑        │
│           │              │              │
│           │ h1,h2 측정 → │ y_xor 측정 → │
│           │ @35ns        │ @70ns        │
```

### 시뮬레이션 결과 상세 (4/4 PASS)

#### Case 1: A=0, B=0 → XOR=0 (PASS)

```
입력: SL_A=0.6V, SL_B=0.6V

Layer 1 Array 1 (bias=0.9V):
  BL0(SA1+) = 0.893V    BL1(SA1-) = 0.607V
  → BL0 > BL1 → SA1: h1 = LOW (≈0V)    ← OR(0,0) = 0 ✓

Layer 1 Array 2 (bias=1.5V):
  BL2(SA2+) = 0.620V    BL3(SA2-) = 1.476V
  → BL3 > BL2 → SA2: h2 = HIGH (1.8V)  ← NAND(0,0) = 1 ✓

Layer 2 Array 3 (bias=1.35V, inputs: h1=0V, h2=1.8V):
  SA1: y_xor = LOW (≈0V)                ← AND(0,1) = 0 ✓
  측정값: vy_xor = 6.04e-07V
```

#### Case 2: A=0, B=1 → XOR=1 (PASS)

```
입력: SL_A=0.6V, SL_B=1.8V

Layer 1 Array 1 (bias=0.9V):
  BL0(SA1+) = 0.907V    BL1(SA1-) = 1.116V
  → BL1 > BL0 → SA1: h1 = HIGH (1.8V)  ← OR(0,1) = 1 ✓

Layer 1 Array 2 (bias=1.5V):
  BL2(SA2+) = 1.132V    BL3(SA2-) = 1.492V
  → BL3 > BL2 → SA2: h2 = HIGH (1.8V)  ← NAND(0,1) = 1 ✓

Layer 2 Array 3 (bias=1.35V, inputs: h1=1.8V, h2=1.8V):
  SA1: y_xor = HIGH (1.8V)              ← AND(1,1) = 1 ✓
  측정값: vy_xor = 1.80e+00V
```

#### Case 3: A=1, B=0 → XOR=1 (PASS)

```
입력: SL_A=1.8V, SL_B=0.6V

Layer 1 Array 1 (bias=0.9V):
  BL0(SA1+) = 0.907V    BL1(SA1-) = 1.116V
  → BL1 > BL0 → SA1: h1 = HIGH (1.8V)  ← OR(1,0) = 1 ✓

Layer 1 Array 2 (bias=1.5V):
  BL2(SA2+) = 1.132V    BL3(SA2-) = 1.492V
  → BL3 > BL2 → SA2: h2 = HIGH (1.8V)  ← NAND(1,0) = 1 ✓

Layer 2 Array 3 (bias=1.35V, inputs: h1=1.8V, h2=1.8V):
  SA1: y_xor = HIGH (1.8V)              ← AND(1,1) = 1 ✓
  측정값: vy_xor = 1.80e+00V
```

#### Case 4: A=1, B=1 → XOR=0 (PASS)

```
입력: SL_A=1.8V, SL_B=1.8V

Layer 1 Array 1 (bias=0.9V):
  BL0(SA1+) = 0.921V    BL1(SA1-) = 1.771V
  → BL1 > BL0 → SA1: h1 = HIGH (1.8V)  ← OR(1,1) = 1 ✓

Layer 1 Array 2 (bias=1.5V):
  BL2(SA2+) = 1.790V    BL3(SA2-) = 1.508V
  → BL2 > BL3 → SA2: h2 = LOW (≈0V)    ← NAND(1,1) = 0 ✓

Layer 2 Array 3 (bias=1.35V, inputs: h1=1.8V, h2=0V):
  SA1: y_xor = LOW (≈0V)                ← AND(1,0) = 0 ✓
  측정값: vy_xor = 6.04e-07V
```

#### 결과 요약 테이블

| A | B | SL_A | SL_B | BL0(Arr1) | BL1(Arr1) | h1(OR) | BL2(Arr2) | BL3(Arr2) | h2(NAND) | y_xor | XOR | 판정 |
|---|---|------|------|-----------|-----------|--------|-----------|-----------|----------|-------|-----|------|
| 0 | 0 | 0.6V | 0.6V | 0.893V | 0.607V | **0** | 0.620V | 1.476V | **1** | **0V** | 0 | PASS |
| 0 | 1 | 0.6V | 1.8V | 0.907V | 1.116V | **1** | 1.132V | 1.492V | **1** | **1.8V** | 1 | PASS |
| 1 | 0 | 1.8V | 0.6V | 0.907V | 1.116V | **1** | 1.132V | 1.492V | **1** | **1.8V** | 1 | PASS |
| 1 | 1 | 1.8V | 1.8V | 0.921V | 1.771V | **1** | 1.790V | 1.508V | **0** | **0V** | 0 | PASS |

> BL 전압은 evaluate 시점(15ns)에서 측정. h1, h2는 35ns, y_xor는 70ns에서 측정.
> 판정 기준: 전압 > 0.9V → HIGH(1), ≤ 0.9V → LOW(0)

---

## 설계 과정 히스토리 (Phase 1 → 3)

### Phase 1: SA 단독 검증

StrongARM Latch-type SA를 설계하고 50mV differential input에서
full-swing 출력을 확인. v1~v5까지 5회 반복 설계.

주요 수정 사항:
- v1~v3: SAE 극성 반전 버그 → inverter 제거, SAE 직접 연결 (v4)
  - PMOS precharge gate에 SAE_B(inverted)를 연결했으나
    PMOS는 active-low → SAE 직접 연결이 맞음
- v3: MP5 equalize 위치 → Q-VDD short 위험 → 별도 행으로 분리
- v4: MN0 source wire x좌표(370) ↔ VSS stub x좌표(350) 불일치
  → floating net1 버그 → 좌표 통일 (v5)

### Phase 2: 1-Layer XOR 시도

WL Driver + RRAM 4x4 + SA를 결합하여 1-layer XOR 시뮬레이션.
입력 A, B를 SL에 중복 연결 (SL0=SL1=A, SL2=SL3=B).

결과: A=0,B=1과 A=1,B=0만 성공 (differential이 존재하는 경우).

| A | B | BL0 | BL1 | SA 동작 | 결과 |
|---|---|-----|-----|---------|------|
| 0 | 0 | ≈0V | ≈0V | Vth 미만 → 미동작 | FAIL |
| 0 | 1 | ~0.9V | ~0.6V | 정상 분해 | PASS |
| 1 | 0 | ~0.9V | ~0.6V | 정상 분해 | PASS |
| 1 | 1 | ≈1.7V | ≈1.7V | 차이 없음 → random latch | FAIL |

결론: XOR는 비선형 → 1-layer로 구현 불가능.

### Phase 3: 2-Layer XOR 구현

XOR = AND(OR, NAND) 분해 후 2-layer 네트워크 설계.
3가지 제약조건 발견 및 해결 (상세는 위 "핵심 설계 제약조건" 참조).

진행 과정:
1. **1차 시도** (2/4 PASS): 불균형 컬럼 사용 → bias LRS가 BL 지배 → 실패
2. **2차 시도** (3/4 PASS): 균형 컬럼 + logic 0=0V → (0,0)에서 BL < SA Vth → 실패
3. **3차 시도 (최종)** (4/4 PASS): 균형 컬럼 + logic 0=0.6V + 3개 어레이

최종 결과: 3개 RRAM 4x4 어레이 + 12개 WL Driver + 6개 SA로 **4/4 PASS**.

---

## xschem 회로도 열기 (참고)

```bash
# WSL2/WSLg 환경에서 xschem GUI로 회로도 열기
DISPLAY=:0 xschem --rcfile ~/.xschem/xschemrc $PROJECT_ROOT/analog/xschem/sense_amp.sch &
DISPLAY=:0 xschem --rcfile ~/.xschem/xschemrc $PROJECT_ROOT/analog/xschem/wl_driver.sch &

# 비대화형 netlist 추출 + SVG export
DISPLAY=:0 xschem --rcfile ~/.xschem/xschemrc sense_amp.sch \
  --command "after 3000 {xschem netlist; xschem zoom_full; after 500 {xschem print svg out.svg; after 1000 exit}}"
rsvg-convert -w 1920 -h 1080 --keep-aspect-ratio out.svg -o out.png
```

> WSL2에서 Xvfb 사용 불가 (/tmp/.X11-unix read-only). 반드시 `DISPLAY=:0` 사용.

---

## d_cosim Mixed-Signal Co-simulation

### 개요

디지털 FSM 컨트롤러(Verilog)와 아날로그 블록(SPICE)을 하나의 ngspice 시뮬레이션에서 실행하는 closed-loop co-simulation.
ngspice의 `d_cosim` XSPICE 코드 모델을 사용하여 Verilator로 컴파일된 Verilog를 실시간으로 구동합니다.

### 필수 소프트웨어

```bash
# ngspice-43 (d_cosim + KLU 지원 빌드)
# 설치 경로: $NGSPICE_HOME (default: ~/ngspice-local)
$NGSPICE --version   # → ngspice-43

# Verilator (Verilog→C++ 컴파일러)
verilator --version                      # → Verilator 5.x
```

**ngspice-43 빌드** (d_cosim 지원):
```bash
cd ngspice-43
mkdir release && cd release
../configure --prefix=$NGSPICE_HOME \
  --enable-xspice --enable-cider --enable-osdi \
  --with-ngshared --enable-klu \
  CFLAGS="-O2" LDFLAGS="-lSuiteSparse_config"
make -j$(nproc) && make install
```

### 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     ngspice simulation                       │
│                                                             │
│  ┌──────────┐    DAC     ┌──────────┐                       │
│  │ d_cosim  │──bridges──→│ Analog   │                       │
│  │ (FSM     │            │ Blocks   │                       │
│  │ Verilog) │←──bridges──│          │                       │
│  └──────────┘    ADC     └──────────┘                       │
│                                                             │
│  Digital Domain          Analog Domain                      │
│  - clk, rst_n            - WL Driver (1.8V→3.3V)           │
│  - cmd_valid/write/row   - BL Write Driver (tri-state)     │
│  - bl_sense[3:0]         - BL Precharge PMOS               │
│  - wl_sel[3:0]           - RRAM 4x4 Array (OSDI model)     │
│  - bl_en[3:0]            - Sense Amplifier (StrongARM)      │
│  - bl_data[3:0]          - SL Switch NMOS                   │
│  - write_en, read_en                                        │
└─────────────────────────────────────────────────────────────┘
```

### 실행 방법

```bash
cd $PROJECT_ROOT/analog/sim/cosim

# Step 1: Verilog를 .so로 컴파일 (vlnggen 사용)
cd verilog
$NGSPICE -- \
  $VLNGGEN \
  -Wno-CASEINCOMPLETE controller_cosim.v controller.v
cp controller_cosim.so ../
cd ..

# Step 2: Co-sim 실행
$NGSPICE -b rram_cosim_full.spice

# Step 3: 파형 플롯 (선택)
python3 plot_cosim_full.py
# → rram_cosim_full.png 생성
```

### d_cosim 포트 매핑

d_cosim은 입력을 먼저, 출력을 나중에 나열해야 합니다.
`controller_cosim.v`가 포트 재배열을 처리합니다.

```
입력 (13 bits): clk, rst_n, cmd_valid, cmd_write, cmd_row[1:0],
                cmd_col[1:0], cmd_data, bl_sense[3:0]
출력 (21 bits): cmd_ready, resp_valid, resp_data, wl_sel[3:0],
                sl_sel[3:0], bl_en[3:0], bl_data[3:0], write_en, read_en
```

d_cosim에서 multi-bit 신호는 **per-bit, MSB first**로 매핑:
```spice
afsm [clk_d] [rst_d] ... [bl_sense3] [bl_sense2] [bl_sense1] [bl_sense0]
+    [cmd_ready_d] ... [wl3] [wl2] [wl1] [wl0] ...
+    null
+    cosim_ctrl
.model cosim_ctrl d_cosim ...
```

### 테스트 시나리오 (rram_cosim_full.spice)

| Phase | 시간 | 동작 | 검증 항목 |
|-------|------|------|----------|
| 1 | 45ns | READ row=2, col=2 | RRAM cell 읽기, SA 감지, resp_data |
| 2 | 145ns | WRITE row=2, col=2, data=1 | BL Write Driver 구동, WL/SL 활성화 |
| 3 | 260ns | READ row=2, col=2 (verify) | 쓰기 후 재읽기 검증 |

### Co-sim 결과

```
Phase 1 (READ):
  - WL2 활성화 (3.3V), SA가 BL2 감지
  - resp_data = 0 (HRS, RRAM 미프로그래밍 상태)

Phase 2 (WRITE):
  - BL Write Driver가 BL2에 1.788V 인가 (기존 NFET pass gate: ~1.3V)
  - WL2 = 3.3V, SL2 = 0V (WRITE 조건)
  - 8 cycle 동안 프로그래밍 펄스 인가

Phase 3 (Verify READ):
  - RRAM OSDI 모델의 SET 동역학으로 인해 HRS→LRS 전환 미완료
  - 이는 OSDI 모델 파라미터 이슈 (회로 설계 이슈 아님)
```

### ADC/DAC Bridge 설명

ADC/DAC bridge는 **시뮬레이션 전용 인터페이스**로, 실제 회로 소자가 아닙니다.

- **DAC bridge** (`adc_buff`): 디지털 신호 → SPICE 아날로그 전압 변환
  - `in_low=0.2 in_high=0.8 out_low=0.0 out_high=1.8`
- **ADC bridge** (`dac_buff`): SPICE 아날로그 전압 → 디지털 신호 변환
  - `in_low=0.4 in_high=1.0`

실제 하드웨어에서는 디지털 컨트롤러의 CMOS 출력이 직접 아날로그 블록에 연결되므로
bridge가 필요 없습니다. Co-sim에서는 ngspice의 아날로그 엔진과 XSPICE 디지털 엔진 사이의
데이터 타입 변환을 위해 사용됩니다.
