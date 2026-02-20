# RRAM 2-Array XOR Chip Architecture

## Overview

Sky130 PDK 기반 RRAM 4x4 크로스바 어레이 2개를 사용한 XOR 신경망 inference 칩.
디지털 컨트롤러 3개 + 아날로그 매크로 21개 = **총 24개 셀 인스턴스**.

```
XOR(A,B) = AND( OR(A,B), NAND(A,B) )

Phase 0: Array 1 → SA1(OR), SA2(NAND) → h1, h2  (Layer 1)
Phase 1: Array 2 → SA3(AND) → xor_result         (Layer 2)
```

---

## Cell Inventory

### Digital Cells (3)

| Instance | Module | 역할 | 트랜지스터 수 |
|----------|--------|------|--------------|
| `u_ctrl` | `xor_controller` | 6-state FSM, 2-phase inference 제어 | 합성 (std cell) |
| `u_enc` | `input_encoder` | phase별 SL 데이터 생성 (combinational) | 합성 (std cell) |
| `u_sae` | `sae_control` | SAE 3-cycle 펄스 생성기 | 합성 (std cell) |

### Analog Macros (21)

| Instance | Module | 역할 | 트랜지스터 수 | 소속 |
|----------|--------|------|--------------|------|
| `u_rram_array_1` | `rram_4x4_array` | RRAM 4x4 크로스바 (Layer 1: OR+NAND) | 16x 1T1R (32) | Array 1 |
| `u_rram_array_2` | `rram_4x4_array` | RRAM 4x4 크로스바 (Layer 2: AND) | 16x 1T1R (32) | Array 2 |
| `u_wl_drv_1_0` ~ `u_wl_drv_1_3` | `wl_driver` | 1.8V→VWL 레벨 시프터 (Array 1) | 8 each | Array 1 |
| `u_wl_drv_2_0` ~ `u_wl_drv_2_3` | `wl_driver` | 1.8V→VWL 레벨 시프터 (Array 2) | 8 each | Array 2 |
| `u_sa1` | `sense_amp` | BL[0] vs BL[1] → OR 결과 (Array 1) | 10 | Array 1 |
| `u_sa2` | `sense_amp` | BL[2] vs BL[3] → NAND 결과 (Array 1) | 10 | Array 1 |
| `u_sa3` | `sense_amp` | BL[0] vs BL[1] → AND 결과 (Array 2) | 10 | Array 2 |
| `u_bl_wd_1_0` ~ `u_bl_wd_1_3` | `bl_write_driver` | BL tri-state 드라이버 (Array 1, 비활성) | 8 each | Array 1 |
| `u_bl_wd_2_0` ~ `u_bl_wd_2_3` | `bl_write_driver` | BL tri-state 드라이버 (Array 2, 비활성) | 8 each | Array 2 |

**총 트랜지스터**: 2x32 (RRAM) + 8x8 (WL) + 3x10 (SA) + 8x8 (BL_WD) = 64 + 64 + 30 + 64 = **222개** (아날로그만)

---

## Analog Macro Details

### 1. RRAM 4x4 Array (`rram_4x4_array`)

```
크기: 17.87 x 25.15 um
구조: 16x 1T1R (sky130_fd_pr_reram + nfet_g5v0d10v5)
핀:   WL[3:0] (input), BL[3:0] (inout), SL[3:0] (inout), GND (inout)

연결: BL → TE → BE → NFET_Drain, NFET_Gate → WL, NFET_Source → SL
       GND → 모든 NFET body terminal
```

- 같은 GDS/LEF를 2개 인스턴스로 재사용
- Array 1: OR+NAND weight 프로그래밍, Array 2: AND weight 프로그래밍
- `rram_gnd` 핀으로 외부 접지 연결 (두 배열 공유)

### 2. WL Driver (`wl_driver`)

```
크기: 8.04 x 12.36 um
구조: Input Inverter → Cross-coupled Level Shifter → HV Buffer
핀:   IN (input), OUT (output), VDD(1.8V), VWL(고전압), VSS
트랜지스터: 8개 (2x 1.8V pfet/nfet + 6x 5V HV pfet/nfet)

[Input Inverter]         [Level Shifter]              [HV Buffer]
MP0(INB,IN,VDD) W=1u    MP1(Q,QB,VWL) W=1u           MP3(OUT,Q,VWL) W=4u
MN0(INB,IN,VSS) W=0.5u  MN1(Q,IN,VSS) W=2u           MN3(OUT,Q,VSS) W=2u
                         MP2(QB,Q,VWL) W=1u
                         MN2(QB,INB,VSS) W=2u
```

- 8개 인스턴스 (4 per array), 모두 같은 `wl_en[3:0]` 입력
- Inference 중 `wl_en = 4'b1111` (All ON)
- 전원 핀(VDD, VWL, VSS)은 PDN이 자동 연결

### 3. Sense Amplifier (`sense_amp`)

```
크기: 3.63 x 10.96 um
구조: StrongARM Latch-type (좌우 대칭)
핀:   SAE (input), INP (input), INN (input), Q (output), QB (output), VDD, VSS
트랜지스터: 10개 (모두 1.8V CMOS)

[Precharge]           [Equalize]        [Latch PMOS]
MP3(Q,SAE,VDD)  W=0.5u  MP5(QB,SAE,Q) W=0.5u  MP1(Q,QB,VDD)  W=1u
MP4(QB,SAE,VDD) W=0.5u                         MP2(QB,Q,VDD)  W=1u

[Latch NMOS]          [Input Pair]       [Tail]
MN1(Q,QB,FN1)  W=1u   MN3(FN1,INP,TAIL) W=2u  MN0(TAIL,SAE,VSS) W=2u
MN2(QB,Q,FN2)  W=1u   MN4(FN2,INN,TAIL) W=2u
```

- SAE=0: precharge (Q=QB=VDD), SAE=1: evaluate
- 3개 인스턴스: SA1(OR), SA2(NAND), SA3(AND)
- 성능: 50mV 입력차 → 1.8V full-swing, 230ps resolution

### 4. BL Write Driver (`bl_write_driver`)

```
크기: 4.92 x 11.86 um
구조: EN Inverter + DATA Inverter + Series PMOS/NMOS Output Stage
핀:   EN (input), DATA (input), BL (output), VDD, VSS
트랜지스터: 8개 (모두 1.8V CMOS)

[EN Inverter]          [DATA Inverter]        [Output Stage]
MP0(EN_B,EN,VDD) W=0.5u  MP3(DATA_B,DATA,VDD) W=0.5u  MP1(NET_P,EN_B,VDD)  W=4u
MN0(EN_B,EN,VSS) W=0.5u  MN3(DATA_B,DATA,VSS) W=0.5u  MP2(BL,DATA_B,NET_P) W=4u
                                                  MN2(BL,DATA_B,NET_N) W=4u
                                                  MN1(NET_N,EN,VSS)    W=4u
```

- 8개 인스턴스 (4 per array), inference 중 `EN=0` (Hi-Z)
- EN=1: DATA→BL (1.774V full-swing), EN=0: Hi-Z (SA가 BL을 sensing)

---

## Digital Module Details

### 1. XOR Controller (`xor_controller`)

6-state FSM으로 2-phase inference를 순차 제어.

```
State Flow:
  IDLE → WL_ON → SL_SETTLE → SAE_WAIT → LATCH → (phase==0? SL_SETTLE : DONE → IDLE)

States:
  IDLE      : start 대기, wl_en=0000
  WL_ON     : wl_en=1111, WL_SETTLE_CNT(2) 사이클 대기
  SL_SETTLE : input_encoder가 SL 데이터 구동, SL_SETTLE_CNT(4) 사이클 대기
  SAE_WAIT  : sae_trigger→1, sae_done 대기
  LATCH     : phase 0→h1=sa1_q, h2=sa2_q (→SL_SETTLE)
              phase 1→xor_result=sa3_q (→DONE)
  DONE      : result_valid=1, IDLE로 복귀
```

**입출력:**

| 방향 | 신호 | 연결 대상 |
|------|------|----------|
| in | `clk`, `rst_n` | Top 포트 |
| in | `start`, `input_a`, `input_b` | Top 포트 |
| out | `xor_result`, `result_valid`, `ready` | Top 포트 |
| out | `wl_en[3:0]` | WL Drivers (8개 공유) |
| out | `phase` | input_encoder, Top 포트 |
| out | `sae_trigger` | sae_control |
| in | `sae_done` | sae_control |
| in | `sa1_q`, `sa2_q`, `sa3_q` | SA1, SA2, SA3 |
| out | `h1_out`, `h2_out` | input_encoder |

### 2. Input Encoder (`input_encoder`)

Combinational logic. Phase에 따라 두 배열의 SL 데이터를 생성.

```
Phase 0 (Layer 1): sl_data_1 = {1, 1, input_b, input_a}   (Array 1 active)
                    sl_data_2 = {0, 0, 0, 0}               (Array 2 idle)

Phase 1 (Layer 2): sl_data_1 = {0, 0, 0, 0}               (Array 1 idle)
                    sl_data_2 = {1, 1, h2, h1}              (Array 2 active)
```

- SL[1:0]: 입력 데이터 (A, B) 또는 중간값 (h1, h2)
- SL[3:2]: bias reference (VDD=1)

### 3. SAE Control (`sae_control`)

SAE 3-cycle 펄스 생성기.

```
trigger(1-cycle pulse) → SAE=1 for 3 cycles → SAE=0, done=1(pulse)
```

- 20MHz 기준: 3 cycles = 150ns >> SA resolution time (230ps)
- 모든 SA (SA1, SA2, SA3)가 동시에 SAE를 받음
- 컨트롤러가 phase에 따라 올바른 SA 출력만 latch

---

## Signal Connection Map

### Top-Level Ports

| Port | Direction | Width | 용도 |
|------|-----------|-------|------|
| `clk` | input | 1 | 시스템 클럭 (20MHz, 50ns) |
| `rst_n` | input | 1 | Active-low 리셋 |
| `rram_gnd` | inout | 1 | RRAM NFET body 접지 (두 배열 공유) |
| `start` | input | 1 | Inference 시작 트리거 |
| `input_a` | input | 1 | XOR 입력 A |
| `input_b` | input | 1 | XOR 입력 B |
| `xor_result` | output | 1 | XOR 결과 |
| `result_valid` | output | 1 | 결과 유효 신호 |
| `ready` | output | 1 | Inference 준비 완료 |
| `phase` | output | 1 | 0=Layer1, 1=Layer2 (debug) |
| `sae` | output | 1 | SAE 출력 (debug) |
| `vccd1` / `vssd1` | inout | 1 | 전원 핀 (USE_POWER_PINS) |

### Internal Signal Routing

```
┌─────────────────────────────────────────────────────────────────┐
│                        rram_ctrl_top                            │
│                                                                 │
│  ┌──────────────┐    wl_en[3:0]    ┌──────────────────────┐    │
│  │              │──────────────────→│ u_wl_drv_1_0~3       │    │
│  │              │──────────────────→│ u_wl_drv_2_0~3       │    │
│  │              │                   └───────┬──────────────┘    │
│  │              │              wl_out_1[3:0] │  wl_out_2[3:0]   │
│  │              │                   ┌───────▼──────────────┐    │
│  │  u_ctrl      │                   │ u_rram_array_1       │    │
│  │  (xor_       │   sl_data_1[3:0]  │   WL ← wl_out_1     │    │
│  │  controller) │──→u_enc──────────→│   SL ← sl_data_1     │    │
│  │              │   sl_data_2[3:0]  │   BL → bl_bus_1      │    │
│  │              │──→u_enc──────────→│   GND ← rram_gnd     │    │
│  │              │                   └───────┬──────────────┘    │
│  │              │              bl_bus_1[3:0] │  bl_bus_2[3:0]   │
│  │              │                   ┌───────▼──────────────┐    │
│  │              │  sa1_q ←──────────│ u_sa1: INP=bl[0]     │    │
│  │              │  sa2_q ←──────────│ u_sa2: INP=bl[2]     │    │
│  │              │  sa3_q ←──────────│ u_sa3: INP=bl_bus_2[0]│   │
│  │              │                   └──────────────────────┘    │
│  │              │                                               │
│  │              │  sae_trigger      ┌──────────────────────┐    │
│  │              │──────────────────→│ u_sae (sae_control)  │    │
│  │              │  sae_done         │   sae → SA1,SA2,SA3  │    │
│  │              │←──────────────────│                       │    │
│  └──────────────┘                   └──────────────────────┘    │
│                                                                 │
│  BL Write Drivers (EN=0, Hi-Z during inference):                │
│    u_bl_wd_1_0~3 → bl_bus_1[3:0]                               │
│    u_bl_wd_2_0~3 → bl_bus_2[3:0]                               │
└─────────────────────────────────────────────────────────────────┘
```

### Signal Detail Table

| Signal | Source | Destination | 설명 |
|--------|--------|-------------|------|
| `wl_en[3:0]` | u_ctrl | u_wl_drv_1_0~3, u_wl_drv_2_0~3 | WL 드라이버 활성화 (8개 공유) |
| `wl_out_1[3:0]` | u_wl_drv_1_0~3 | u_rram_array_1.WL | Array 1 WL 구동 |
| `wl_out_2[3:0]` | u_wl_drv_2_0~3 | u_rram_array_2.WL | Array 2 WL 구동 |
| `sl_data_1[3:0]` | u_enc | u_rram_array_1.SL | Array 1 SL (입력 인코딩) |
| `sl_data_2[3:0]` | u_enc | u_rram_array_2.SL | Array 2 SL (입력 인코딩) |
| `bl_bus_1[3:0]` | u_rram_array_1.BL | u_sa1, u_sa2, u_bl_wd_1_0~3 | Array 1 BL (SA sensing) |
| `bl_bus_2[3:0]` | u_rram_array_2.BL | u_sa3, u_bl_wd_2_0~3 | Array 2 BL (SA sensing) |
| `sae` | u_sae | u_sa1, u_sa2, u_sa3 | SA Enable (3개 동시) |
| `sae_trigger` | u_ctrl | u_sae | SAE 펄스 시작 |
| `sae_done` | u_sae | u_ctrl | SAE 완료 피드백 |
| `sa1_q` | u_sa1 | u_ctrl | OR 결과 (Array 1 BL[0] vs BL[1]) |
| `sa2_q` | u_sa2 | u_ctrl | NAND 결과 (Array 1 BL[2] vs BL[3]) |
| `sa3_q` | u_sa3 | u_ctrl | AND 결과 (Array 2 BL[0] vs BL[1]) |
| `h1`, `h2` | u_ctrl | u_enc | Layer 1 중간값 (OR, NAND) |
| `phase` | u_ctrl | u_enc, Top 포트 | Phase 선택 (0=L1, 1=L2) |
| `rram_gnd` | Top 포트 | u_rram_array_1.GND, u_rram_array_2.GND | RRAM 접지 (공유) |

---

## 2-Phase Inference Data Flow

### Phase 0: Layer 1 (OR + NAND)

```
Step 1: u_ctrl → wl_en = 4'b1111
Step 2: u_wl_drv_1_0~3 → wl_out_1[3:0] = VWL (고전압)
Step 3: u_enc → sl_data_1 = {1, 1, B, A}   (sl_data_2 = 0000)
Step 4: u_rram_array_1 → BL currents develop on bl_bus_1[3:0]

        BL[0]: I = Σ(w_0j × SL_j)  ← OR positive
        BL[1]: I = Σ(w_1j × SL_j)  ← OR reference
        BL[2]: I = Σ(w_2j × SL_j)  ← NAND positive
        BL[3]: I = Σ(w_3j × SL_j)  ← NAND reference

Step 5: u_sae → SAE=1 (3 cycles)
Step 6: u_sa1 → Q=h1 (OR:  BL[0] > BL[1] → 1)
        u_sa2 → Q=h2 (NAND: BL[2] > BL[3] → 1)
Step 7: u_ctrl → h1_reg = sa1_q, h2_reg = sa2_q
```

### Phase 1: Layer 2 (AND)

```
Step 8:  u_enc → sl_data_2 = {1, 1, h2, h1}   (sl_data_1 = 0000)
Step 9:  u_rram_array_2 → BL currents develop on bl_bus_2[3:0]

         BL[0]: I = Σ(w_0j × SL_j)  ← AND positive
         BL[1]: I = Σ(w_1j × SL_j)  ← AND reference

Step 10: u_sae → SAE=1 (3 cycles)
Step 11: u_sa3 → Q=xor_result (AND: BL[0] > BL[1] → 1)
Step 12: u_ctrl → xor_result = sa3_q, result_valid = 1
```

### XOR Truth Table

| A | B | OR (h1) | NAND (h2) | AND(h1,h2) = XOR |
|---|---|---------|-----------|-------------------|
| 0 | 0 | 0 | 1 | 0 |
| 0 | 1 | 1 | 1 | 1 |
| 1 | 0 | 1 | 1 | 1 |
| 1 | 1 | 1 | 0 | 0 |

---

## Physical Layout

### Die Area

```
DIE_AREA: 200 x 200 um
Core: ~5.52 to ~194 (x), ~11.6 to ~188 (y)
```

### Macro Placement

```
    y ▲
  188 │
      │    ┌─────┐ ┌─────┐  ┌─────┐ ┌─────┐
  110 │    │WL1_1│ │WL1_3│  │WL2_1│ │WL2_3│
      │    └─────┘ └─────┘  └─────┘ └─────┘
   90 │    ┌─────┐ ┌─────┐  ┌─────┐ ┌─────┐
      │    │WL1_0│ │WL1_2│  │WL2_0│ │WL2_2│
   80 │    └─────┘ └─────┘  └─────┘ └─────┘
      │         ┌──────────┐ SA  ┌──────────┐ SA
      │         │ RRAM Arr1│1 2  │ RRAM Arr2│ 3
   75 │         └──────────┘     └──────────┘
      │
      │    ┌────┐┌────┐┌────┐┌────┐  ┌────┐┌────┐┌────┐┌────┐
   20 │    │BW10││BW11││BW12││BW13│  │BW20││BW21││BW22││BW23│
      │    └────┘└────┘└────┘└────┘  └────┘└────┘└────┘└────┘
   12 │─────────────────────────────────────────────────────────
    0 └──────────────────────────────────────────────────────→ x
      0  6  18  30    52 58 66  78  90     112    150    194
```

**배치 전략:**
- Array 1 (좌측): WL Drivers → RRAM → SA1, SA2 순서 (데이터 흐름 방향)
- Array 2 (우측): WL Drivers → RRAM → SA3 순서
- BL Write Drivers: 하단 배치 (BL 신호 접근 용이)
- 매크로를 core 왼쪽 가장자리(x=6)에 배치하여 filler-only 구간 제거 (DRC nwell.4 해결)

---

## Build & Verification

### OpenLane Build

```bash
cd $PROJECT_ROOT/openlane
docker run --rm \
  -v $(pwd):/openlane/designs/rram_ctrl \
  -v $PDK_ROOT:$PDK_ROOT \
  -e PDK_ROOT=$PDK_ROOT \
  -e PDK=sky130B \
  efabless/openlane:latest \
  flow.tcl -design /openlane/designs/rram_ctrl
```

### Verification Results (RUN_2026.02.13_05.29.13)

| 항목 | 결과 |
|------|------|
| DRC (Magic) | **PASS** (0 violations) |
| LVS (Netgen) | **PASS** (0 errors) |
| Setup Timing | **PASS** (no violations) |
| Hold Timing | **PASS** (no violations) |

### Analog Verification

| 항목 | 결과 |
|------|------|
| SA 단독 (50mV input) | **PASS** (1.8V full-swing, 230ps) |
| BL Write Driver | **PASS** (1.774V full-swing) |
| 2-Layer XOR inference | **4/4 PASS** |
| d_cosim co-simulation | **PASS** (FSM↔아날로그 closed-loop) |
