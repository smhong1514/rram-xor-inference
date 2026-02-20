# Analog Simulation

> **프로젝트**: Sky130 PDK 기반 2-Array RRAM XOR 신경망 inference 칩
> **경로**: `$PROJECT_ROOT/analog/sim/`

---

## 폴더 구조

```
analog/sim/
│
├── README.md                      ← 이 문서
│
├── cosim/                         ← d_cosim Mixed-Signal Co-Simulation
│   ├── README.md                  ← 상세 설명 (실행 방법, 디버깅 히스토리)
│   ├── xor_cosim.spice            ← ★ 2-Array XOR inference (4/4 PASS)
│   ├── run_xor_cosim.sh           ← 원클릭 실행 스크립트
│   ├── rram_cosim_full_v3.spice   ← Single-array READ/WRITE
│   └── verilog/                   ← Verilog RTL + vlnggen 빌드
│
├── postsim/                       ← Post-Layout 검증 결과 정리
│   ├── README.md                  ← post-layout 관점 설명 (layout-extracted 증거)
│   ├── xor_cosim*.png             ← XOR 결과 파형
│   └── compare_sch_vs_postlayout* ← schematic vs post-layout 비교
│
├── postlayout/                    ← 개별 블록 Schematic vs Post-Layout 비교
│   ├── wl_compare.spice           ← WL Driver: schematic vs extracted
│   ├── sa_compare.spice           ← Sense Amplifier: schematic vs extracted
│   ├── blwd_compare.spice         ← BL Write Driver: schematic vs extracted
│   ├── *_compare.png              ← 비교 결과 파형
│   └── gl_sim/                    ← Gate-level XOR simulation (Verilog)
│
├── ★ 단독 블록 시뮬레이션 (schematic-level) ★
│   ├── sense_amp_tb.spice         ← SA 단독 테스트 (50mV → full swing, 230ps)
│   ├── bl_write_driver_tb.spice   ← BL WD 단독 테스트
│   ├── xor_inference_tb.spice     ← XOR inference 순수 SPICE (d_cosim 없이)
│   ├── plot_sa.py                 ← SA 파형 플롯
│   ├── plot_xor.py                ← XOR 파형 플롯
│   ├── sense_amp_sim.png          ← SA 시뮬레이션 결과
│   └── xor_inference_sim.png      ← XOR 시뮬레이션 결과
│
└── ★ 실행 스크립트 ★
    ├── run_xor.sh                 ← 기본 XOR 시뮬레이션
    ├── run_xor_2layer.sh          ← 2-layer XOR
    ├── run_xor_all.sh             ← 전체 XOR 테스트
    └── run_xor_debug.sh           ← XOR 디버그 모드
```

---

## 시뮬레이션 종류

### 1. d_cosim Co-Simulation (`cosim/`)

Verilog FSM + SPICE 아날로그를 **ngspice 안에서 동시 실행** (closed-loop).

- **XOR inference**: 4/4 truth table PASS ✅
- **Single-array R/W**: HRS READ → SET WRITE → LRS READ 성공 ✅
- 아날로그 블록: **layout-extracted** 넷리스트 사용

```bash
cd cosim && ./run_xor_cosim.sh
```

### 2. Post-Layout 검증 (`postsim/`)

`cosim/`의 결과를 post-layout 관점에서 정리. Layout-extracted 넷리스트 증거, BL differential 분석 등.

### 3. 개별 블록 비교 (`postlayout/`)

각 아날로그 블록의 **schematic vs layout-extracted** 동작 비교:

| 블록 | 파일 | 결과 |
|------|------|------|
| WL Driver | `wl_compare.spice` | 일치 ✅ |
| Sense Amplifier | `sa_compare.spice` | 일치 ✅ |
| BL Write Driver | `blwd_compare.spice` | 일치 ✅ |

```bash
cd postlayout && bash run_compare.sh
```

### 4. 단독 블록 시뮬레이션 (sim/ 루트)

Schematic-level 순수 SPICE 시뮬레이션 (d_cosim 없이):

```bash
# SA 시뮬레이션
$NGSPICE -b sense_amp_tb.spice
python3 plot_sa.py

# XOR inference (순수 SPICE, PWL stimulus)
$NGSPICE -b xor_inference_tb.spice
python3 plot_xor.py
```

---

## 환경

| 도구 | 버전 | 경로 |
|------|------|------|
| ngspice | 43 (d_cosim + KLU) | `$NGSPICE` |
| Verilator | 5.020+ | d_cosim .so 컴파일용 |
| Sky130 PDK | bdc9412b | `$PDK_ROOT/sky130B/` |
| Python 3 | + numpy, matplotlib | 플롯 생성용 |
