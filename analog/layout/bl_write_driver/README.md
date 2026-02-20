# BL Write Driver Layout

## 개요

EN/DATA 입력을 받아 BL(Bit Line)에 full-swing 출력을 내는 tri-state buffer.
모든 트랜지스터가 1.8V (`sky130_fd_pr__pfet_01v8` / `sky130_fd_pr__nfet_01v8`).

- **트랜지스터**: 8개 (4 PMOS + 4 NMOS)
- **포트**: EN, DATA, BL, VDD(1.8V), VSS
- **동작**: EN=1 → BL=DATA (1.774V full swing), EN=0 → Hi-Z

## 회로 구성

```
[EN Inverter]         [DATA Inverter]       [Output Stage]
MP0(EN_B,EN,VDD)      MP3(DATA_B,DATA,VDD)  MP1(NET_P,EN_B,VDD)  ← series PMOS
 pfet W=0.5            pfet W=0.5            pfet W=4
MN0(EN_B,EN,VSS)      MN3(DATA_B,DATA,VSS)  MP2(BL,DATA_B,NET_P)
 nfet W=0.5            nfet W=0.5            pfet W=4
                                             MN2(BL,DATA_B,NET_N) ← series NMOS
                                              nfet W=4
                                             MN1(NET_N,EN,VSS)
                                              nfet W=4
```

SPICE pin order: Drain, Gate, Source, Bulk

## Sky130B PDK 디바이스

| 인스턴스 | PDK Cell | W (um) | L (um) | Layout Cell |
|---------|----------|--------|--------|-------------|
| MP0, MP3, MN0, MN3 | `sky130_fd_pr__pfet/nfet_01v8` | 0.5 | 0.15 | `dev_pfet_w050` / `dev_nfet_w050` |
| MP1, MP2 | `sky130_fd_pr__pfet_01v8` | 4.0 | 0.15 | `dev_pfet_w400` |
| MN1, MN2 | `sky130_fd_pr__nfet_01v8` | 4.0 | 0.15 | `dev_nfet_w400` |

디바이스 셀 생성 방법 (Magic Tcl):
```tcl
set pars [sky130::sky130_fd_pr__pfet_01v8_defaults]
dict set pars w 4.0; dict set pars l 0.15; dict set pars nf 1
dict set pars guard 0; dict set pars full_metal 1
sky130::sky130_fd_pr__pfet_01v8_draw $pars
save dev_pfet_w400
```
- `_draw` 함수 직접 호출 필수 (`magic::gencell`은 파라미터 무시됨)
- `guard 0`: guard ring 없음, `full_metal 1`: 전체 met1 contact

## 레이아웃 배치

```
         VDD rail (met1, y=880-908)
  ┌──────────────────────────────────────┐
  │  MP0(W=0.5) MP3(W=0.5) MP1(W=4) MP2(W=4) │  ← PMOS row (y=+600)
  ├──────────────────────────────────────┤
  │  MN0(W=0.5) MN3(W=0.5) MN2(W=4) MN1(W=4) │  ← NMOS row (y=-600)
  └──────────────────────────────────────┘
         VSS rail (met1, y=-908~-880)
```

- 좌표계: lambda (2 internal = 1 lambda, `magscale 1 2`)
- 디바이스는 `getcell`로 배치 (box 좌표 = subcell bbox lower-left)
- 배선: met1 (intra-column), met2 + via1 (inter-column crossover)
- 포트 라벨: met1 위에 `label` + `port make`

## Substrate/Well Tap

LVS 매칭을 위해 ntap/ptap 추가 필수:

- **nwell merge**: (145,350)-(1455,880) — 모든 PFET nwell을 연결
- **ntap strip**: (150,850)-(1450,880) — nsubstratencontact + locali + viali
- **met1 bridge**: (150,850)-(1450,908) — ntap을 VDD rail에 연결
- **ptap strip**: (150,-938)-(1450,-908) — psubstratepcontact
- **met1 bridge**: (150,-938)-(1450,-880) — ptap을 VSS rail에 연결

스크립트: `add_taps.tcl` (BL Write Driver 섹션)

## 검증 결과

| 항목 | 결과 |
|------|------|
| DRC | 0 errors |
| 디바이스 수 | 8 (layout) = 8 (schematic) |
| 넷 수 | 9 (layout) = 9 (schematic) |
| LVS | **Circuits match uniquely** |

## 파일 목록

| 파일 | 설명 |
|------|------|
| `bl_write_driver.tcl` | 레이아웃 생성 스크립트 |
| `bl_write_driver.mag` | Magic 레이아웃 (hierarchical) |
| `bl_write_driver.gds` | GDS 출력 |
| `bl_write_driver_flat.spice` | 추출된 layout netlist (flat) |
| `bl_write_driver_sch.spice` | schematic netlist (LVS 비교용) |
| `lvs_report.txt` | netgen LVS 결과 리포트 |
| `dev_*.mag` | PDK 디바이스 셀 symlink (→ `../devices/`) |

## Liberty Characterization

ngspice 7×7 sweep으로 측정한 정식 Liberty (.lib) 파일.
16코어 병렬 실행 (Python multiprocessing), Sky130B tt corner, 25°C.

### Timing Arcs

| Arc | Type | Delay 범위 | Transition 범위 |
|-----|------|-----------|----------------|
| DATA → BL rise | positive_unate | 0.073 ~ 1.091 ns | 0.024 ~ 2.281 ns |
| DATA → BL fall | positive_unate | 0.121 ~ 0.888 ns | 0.043 ~ 2.497 ns |
| EN → BL rise | three_state_enable | 0.051 ~ 0.808 ns | 0.025 ~ 2.216 ns |
| EN → BL fall | three_state_enable | 0.010 ~ 0.574 ns | 0.033 ~ 2.267 ns |

### Input Capacitance

| Pin | 측정 방법 | 값 |
|-----|----------|-----|
| EN | AC analysis @ 1GHz | 68.0 fF |
| DATA | Gate area estimation | 1.3 fF |

### 측정 실패 (EN→BL fall)

EN→BL cell_fall에서 7/49 측정 실패 (느린 slew + 작은 load 조합).
원인: EN이 Vth(~0.4V) 넘으면 BL discharge 시작 → EN이 50%(0.9V) 도달 전에 BL이 이미 떨어짐 → 음수 delay.
`interpolate_failures()`로 주변 유효값 평균 보간.

### Liberty 파일

| 파일 | 설명 |
|------|------|
| `char_bl_write_driver.py` | Characterization 스크립트 (197 sims) |
| `bl_write_driver.lib` | 생성된 Liberty (7×7 timing tables) |
| `bl_write_driver.lef` | LEF (gen_lef.tcl로 생성) |

```bash
# 재실행 (~10분, 16코어)
cd $PROJECT_ROOT/analog/layout/bl_write_driver && python3 char_bl_write_driver.py
```

## 재현 방법

```bash
cd $PROJECT_ROOT/analog/layout/bl_write_driver

# 1. 레이아웃 생성
magic -noconsole -dnull -rcfile $PDK_ROOT/sky130B/libs.tech/magic/sky130B.magicrc \
  < bl_write_driver.tcl

# 2. 탭 추가 (add_taps.tcl의 BL Write Driver 섹션)
magic -noconsole -dnull -rcfile $PDK_ROOT/sky130B/libs.tech/magic/sky130B.magicrc \
  < add_taps.tcl

# 3. LVS
netgen -batch lvs \
  "bl_write_driver_flat.spice bl_write_driver_flat" \
  "bl_write_driver_sch.spice bl_write_driver" \
  $PDK_ROOT/sky130B/libs.tech/netgen/sky130B_setup.tcl \
  lvs_report.txt
```
