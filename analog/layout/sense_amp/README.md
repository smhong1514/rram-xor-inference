# Sense Amplifier Layout

## 개요

StrongARM Latch-type Sense Amplifier. 좌우 대칭 구조로 INP/INN 차동 입력을 full-swing 디지털 출력(Q/QB)으로 변환.
모든 트랜지스터가 1.8V (`sky130_fd_pr__pfet_01v8` / `sky130_fd_pr__nfet_01v8`).

- **트랜지스터**: 10개 (5 PMOS + 5 NMOS)
- **포트**: SAE, INP, INN, Q, QB, VDD(1.8V), VSS
- **동작**: SAE=0 → precharge (Q=QB=VDD), SAE=1 → evaluate (차동 증폭)
- **성능**: 50mV 입력 → 1.8V full-swing, resolution time ~230ps

## 회로 구성

```
[Precharge]         [Equalize]        [Latch PMOS]
MP3(Q,SAE,VDD)      MP5(QB,SAE,Q)     MP1(Q,QB,VDD)    MP2(QB,Q,VDD)
 pfet W=0.5          pfet W=0.5        pfet W=1.0        pfet W=1.0
MP4(QB,SAE,VDD)
 pfet W=0.5

[Latch NMOS]        [Input Pair]      [Tail Switch]
MN1(Q,QB,FN1)       MN3(FN1,INP,TAIL) MN0(TAIL,SAE,VSS)
 nfet W=1.0          nfet W=2.0        nfet W=2.0
MN2(QB,Q,FN2)       MN4(FN2,INN,TAIL)
 nfet W=1.0          nfet W=2.0
```

SPICE pin order: Drain, Gate, Source, Bulk

## Sky130B PDK 디바이스

| 인스턴스 | PDK Cell | W (um) | L (um) | Layout Cell |
|---------|----------|--------|--------|-------------|
| MP3, MP4, MP5 | `sky130_fd_pr__pfet_01v8` | 0.5 | 0.15 | `dev_pfet_w050` |
| MP1, MP2 | `sky130_fd_pr__pfet_01v8` | 1.0 | 0.15 | `dev_pfet_w100` |
| MN1, MN2 | `sky130_fd_pr__nfet_01v8` | 1.0 | 0.15 | `dev_nfet_w100` |
| MN0, MN3, MN4 | `sky130_fd_pr__nfet_01v8` | 2.0 | 0.15 | `dev_nfet_w200` |

디바이스 셀 생성: `../devices/gen_devices.tcl`

## 레이아웃 배치

```
              VDD rail (met1, y=1140-1154)
  ┌─────────────────────────────────────┐
  │ MP3   MP1   MP5   MP2   MP4        │  ← PMOS row (y=+1000, +650)
  │ W=0.5 W=1.0 W=0.5 W=1.0 W=0.5     │
  ├─────────────────────────────────────┤
  │     MN1              MN2           │  ← Latch NMOS (y=-350)
  │     MN3              MN4           │  ← Input pair (y=-700)
  │              MN0                   │  ← Tail switch (y=-1050)
  └─────────────────────────────────────┘
              VSS rail (met1, y=-1220~-1206)
```

- **좌우 대칭**: Q쪽(x=300) | 중심(x=600) | QB쪽(x=900) — matching 중요
- PMOS: precharge + equalize (상단), latch (하단)
- NMOS: latch → input pair → tail 순서로 아래쪽
- 배선: met1 (intra-column), met2 + via1 (inter-column, INP/INN 대칭 배선)

## Substrate/Well Tap

- **nwell merge**: (245,550)-(955,1140) — 모든 PFET nwell 연결 + VDD rail까지
- **ntap strip**: (250,1110)-(950,1140) — VDD rail 바로 아래
- **met1 bridge**: (250,1110)-(950,1154) — ntap ↔ VDD rail
- **ptap strip**: (250,-1250)-(950,-1220) — VSS rail 바로 아래
- **met1 bridge**: (250,-1250)-(950,-1206) — ptap ↔ VSS rail

## 검증 결과

| 항목 | 결과 |
|------|------|
| DRC | 0 errors |
| 디바이스 수 | 10 (layout) = 10 (schematic) |
| 넷 수 | 10 (layout) = 10 (schematic) |
| LVS | **Circuits match uniquely** |

## 설계 과정에서 발견된 버그

1. **SAE 극성 반전 (v1~v3)**: Precharge PMOS gate에 inverter로 SAE_B 연결 → PMOS는 active-low이므로 SAE 직접 연결이 정답. Inverter 제거 (v4).
2. **MN0 floating net (v2)**: MN0 source wire(x=370)와 VSS iopin(x=350) x좌표 불일치 → net1 floating → x좌표 통일로 해결.
3. **MP5 equalize 위치 (v3)**: Q-VDD short 위험 → 별도 행으로 분리.

## 파일 목록

| 파일 | 설명 |
|------|------|
| `sense_amp.tcl` | 레이아웃 생성 스크립트 |
| `sense_amp.mag` | Magic 레이아웃 (hierarchical) |
| `sense_amp.gds` | GDS 출력 |
| `sense_amp_flat.spice` | 추출된 layout netlist (flat) |
| `sense_amp_sch.spice` | schematic netlist (LVS 비교용) |
| `lvs_report.txt` | netgen LVS 결과 리포트 |

## Liberty Characterization

ngspice 7×7 sweep으로 측정한 정식 Liberty (.lib) 파일.
16코어 병렬 실행 (Python multiprocessing), Sky130B tt corner, 25°C.
입력 차동: INP=0.925V, INN=0.875V (ΔV=50mV, worst-case).

### Timing Arcs

SAE→Q/QB: negative_unate (SAE↑→Q↓ evaluate, SAE↓→Q↑ precharge).
Q와 QB는 대칭 회로이므로 동일 테이블 사용.

| Arc | 방향 | Delay 범위 | Transition 범위 |
|-----|------|-----------|----------------|
| SAE → Q cell_fall | evaluate (SAE↑→Q↓) | 0.052 ~ 5.106 ns | 0.069 ~ 6.076 ns |
| SAE → Q cell_rise | precharge (SAE↓→Q↑) | 0.049 ~ 2.255 ns | 0.039 ~ 2.991 ns |

### Input Capacitance

| Pin | 측정 방법 | 값 |
|-----|----------|-----|
| SAE | AC analysis @ 1GHz | 36.2 fF |
| INP, INN | AC analysis @ 1GHz | 12.2 fF |

### Liberty 파일

| 파일 | 설명 |
|------|------|
| `char_sense_amp.py` | Characterization 스크립트 (100 sims) |
| `sense_amp.lib` | 생성된 Liberty (7×7 timing tables) |
| `sense_amp.lef` | LEF (gen_lef.tcl로 생성) |

```bash
# 재실행 (~5분, 16코어)
cd $PROJECT_ROOT/analog/layout/sense_amp && python3 char_sense_amp.py
```

## 재현 방법

```bash
cd $PROJECT_ROOT/analog/layout/sense_amp

# 1. 레이아웃 생성
magic -noconsole -dnull -rcfile $PDK_ROOT/sky130B/libs.tech/magic/sky130B.magicrc \
  < sense_amp.tcl

# 2. 탭 추가
magic -noconsole -dnull -rcfile $PDK_ROOT/sky130B/libs.tech/magic/sky130B.magicrc \
  < add_taps.tcl

# 3. LVS
netgen -batch lvs \
  "sense_amp_flat.spice sense_amp_flat" \
  "sense_amp_sch.spice sense_amp" \
  $PDK_ROOT/sky130B/libs.tech/netgen/sky130B_setup.tcl \
  lvs_report.txt
```
