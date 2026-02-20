# WL Driver Layout

## 개요

1.8V 디지털 입력을 고전압(VWL) 출력으로 변환하는 레벨 시프터 + HV 버퍼.
**Mixed-voltage 설계**: 1.8V (`_01v8`) + 5V HV (`_g5v0d10v5`) 트랜지스터 혼합.

- **트랜지스터**: 8개 (1.8V: 1P+1N, HV: 3P+3N)
- **포트**: IN, OUT, VDD(1.8V), VWL(고전압), VSS
- **동작**: IN=1 → OUT=VWL, IN=0 → OUT=VSS

## 회로 구성

```
[Input Inverter]      [Cross-coupled Level Shifter]     [HV Buffer]
 1.8V domain           HV domain (VWL)                   HV domain
MP0(INB,IN,VDD,VDD)   MP1(Q,QB,VWL,VWL)                 MP3(OUT,Q,VWL,VWL)
 pfet_01v8 W=1          pfet_g5v0d10v5 W=1                pfet_g5v0d10v5 W=4
MN0(INB,IN,VSS,VSS)   MP2(QB,Q,VWL,VWL)                 MN3(OUT,Q,VSS,VSS)
 nfet_01v8 W=0.5        pfet_g5v0d10v5 W=1                nfet_g5v0d10v5 W=2
                       MN1(Q,IN,VSS,VSS)
                        nfet_g5v0d10v5 W=2
                       MN2(QB,INB,VSS,VSS)
                        nfet_g5v0d10v5 W=2
```

SPICE pin order: Drain, Gate, Source, Bulk

## Sky130B PDK 디바이스

| 인스턴스 | PDK Cell | W (um) | L (um) | Layout Cell |
|---------|----------|--------|--------|-------------|
| MP0 | `sky130_fd_pr__pfet_01v8` | 1.0 | 0.15 | `dev_pfet_w100` |
| MN0 | `sky130_fd_pr__nfet_01v8` | 0.5 | 0.15 | `dev_nfet_w050` |
| MP1, MP2 | `sky130_fd_pr__pfet_g5v0d10v5` | 1.0 | 0.5 | `dev_hv_pfet_w100` |
| MN1, MN2, MN3 | `sky130_fd_pr__nfet_g5v0d10v5` | 2.0 | 0.5 | `dev_hv_nfet_w200` |
| MP3 | `sky130_fd_pr__pfet_g5v0d10v5` | 4.0 | 0.5 | `dev_hv_pfet_w400` |

HV 디바이스 생성:
```tcl
set pars [sky130::sky130_fd_pr__pfet_g5v0d10v5_defaults]
dict set pars w 4.0; dict set pars l 0.5; dict set pars nf 1
dict set pars guard 0; dict set pars full_metal 1
sky130::sky130_fd_pr__pfet_g5v0d10v5_draw $pars
save dev_hv_pfet_w400
```

## 레이아웃 배치

```
  ┌──────┬─────────────────────┬───────────┐
  │ 1.8V │    HV Domain        │ HV Out    │
  │ VDD  │    VWL rail         │ VWL       │
  │ MP0  │ MP1      MP2        │ MP3(W=4)  │  ← PMOS (y=+300/+350)
  │      │                     │           │
  │ MN0  │ MN1      MN2        │ MN3       │  ← NMOS (y=-300)
  │      │    VSS rail         │           │
  └──────┴─────────────────────┴───────────┘
  col 1    col 2    col 3       col 4
  x=200    x=600    x=1000      x=1450
```

- **전압 도메인 분리**: VDD rail (col 1만), VWL rail (col 2-4)
- VDD rail: (150,420)-(260,434), VWL rail: (520,620)-(1520,634)
- VSS rail: (140,-470)-(1520,-456) — 전체 공유
- 내부 배선:
  - Q net: met1 vertical (col 2) + met2 horizontal → col 3, col 4
  - QB net: met1 vertical (col 3) + met2 horizontal → col 2
  - INB: met1 vertical (col 1) + met2 horizontal → col 3 MN2.G

## Substrate/Well Tap (핵심 이슈)

### VDD domain (column 1)
- **nwell**: (145,200)-(255,**466**) — VDD rail을 넘어 위쪽까지 확장
- **ntap**: (150,**436**)-(250,**466**) — VDD rail **위쪽**에 배치
- **met1 bridge**: (150,420)-(260,466)

> **왜 VDD rail 위쪽인가?**
> MP0의 Gate Top met1이 lambda (185.5,370.5)-(214.5,**393.5**)까지 확장.
> VDD rail 아래(y=390-420)에 ntap을 놓으면 gate met1과 겹쳐서 **VDD-IN 단락** 발생.
> 해결: ntap을 VDD rail 위쪽(y=436-466)으로 이동.

### VWL domain (columns 2-4)
- **nwell**: (528,100)-(1522,620) — 모든 HV PFET nwell 병합
- **ntap**: (530,590)-(***1420***,620) — x=1420에서 절단!
- **met1 bridge**: (530,590)-(***1420***,634)

> **왜 x=1420에서 절단하는가?**
> MP3(dev_hv_pfet_w400)의 Gate Top met1이 lambda (1427,570.5)-(1473,**593.5**)까지 확장.
> met1 bridge가 x=1520까지 가면 gate met1과 겹쳐서 **Q-VWL 단락** 발생.
> 해결: ntap/bridge를 x=1420에서 끊음 (1420 < 1427, 7 lambda 여유).
> VWL bus들(x=549-572, 949-972, 1399-1422)이 bridge를 통해 ntap에 연결 제공.

### VSS ptap
- **ptap**: (150,-500)-(1510,-470)
- **met1 bridge**: (150,-500)-(1520,-456)

## 해결한 오류들

### 1. LVS bulk 불일치 (tap 추가 전)
- **증상**: layout 추출 시 PFET bulk = 개별 nwell 노드 (w_291_400# 등), NFET bulk = VSUBS
- **원인**: substrate/well tap 없음 → nwell이 VDD에, psub이 VSS에 미연결
- **해결**: ntap/ptap 추가 → PFET bulk=VDD/VWL, NFET bulk=VSS

### 2. VDD-IN 단락 (첫 번째 tap 시도)
- **증상**: `extract all` 후 "Ports VDD and IN are electrically shorted"
- **원인**: ntap strip(y=390-420)이 MP0 Gate Top met1(y=370.5-393.5)과 겹침
- **해결**: ntap을 VDD rail 위쪽(y=436-466)으로 이동

### 3. Q-VWL 단락 (두 번째 tap 시도)
- **증상**: 추출 시 X6의 D=VWL (Q가 VWL에 합쳐짐)
- **원인**: VWL ntap met1 bridge(x=530-1520)가 MP3 Gate Top met1(x=1427-1473, y=570.5-593.5)과 겹침
- **분석**: dev_hv_pfet_w400의 Gate Top met1은 device center에서 lambda +220.5 높이까지 확장 → 배치 위치(1450,350)에서 y=570.5까지 도달
- **해결**: ntap/bridge를 x=1420에서 절단 (MP3 gate 시작점 x=1427보다 7 lambda 전)

### 교훈
**met1 bridge는 반드시 모든 디바이스의 met1 핀 좌표를 확인한 후 배치해야 한다.**
특히 large W 디바이스 (W=4.0)는 Gate Top/Bottom met1이 예상보다 멀리 확장된다.

## 검증 결과

| 항목 | 결과 |
|------|------|
| DRC | 0 errors |
| 디바이스 수 | 8 (layout) = 8 (schematic) |
| 넷 수 | 8 (layout) = 8 (schematic) |
| LVS | **Circuits match uniquely** |

## 파일 목록

| 파일 | 설명 |
|------|------|
| `wl_driver.tcl` | 레이아웃 생성 스크립트 (디바이스 배치 + 배선 + DRC + 추출 + GDS) |
| `add_taps_wl.tcl` | 탭 추가 전용 스크립트 (VDD/VWL ntap, VSS ptap) |
| `wl_driver.mag` | Magic 레이아웃 (hierarchical, 탭 포함) |
| `wl_driver.gds` | GDS 출력 |
| `wl_driver_flat.spice` | 추출된 layout netlist (flat) |
| `wl_driver_sch.spice` | schematic netlist (LVS 비교용) |
| `lvs_report.txt` | netgen LVS 결과 리포트 |

## Liberty Characterization

ngspice 7×7 sweep으로 측정한 정식 Liberty (.lib) 파일.
16코어 병렬 실행 (Python multiprocessing), Sky130B tt corner, 25°C.
VWL=3.3V, 출력 threshold는 VDD(1.8V) 도메인 기준 (50%=0.9V).

### Timing Arcs

IN→OUT: positive_unate (IN↑→OUT↑, IN↓→OUT↓). Level shifter 1.8V→3.3V.

| Arc | Delay 범위 | Transition 범위 |
|-----|-----------|----------------|
| IN → OUT cell_rise | 0.258 ~ 1.760 ns | 0.110 ~ 2.168 ns |
| IN → OUT cell_fall | 0.373 ~ 1.843 ns | 0.087 ~ 2.483 ns |

### Input Capacitance

| Pin | 측정 방법 | 값 |
|-----|----------|-----|
| IN | AC analysis @ 1GHz | 45.6 fF |

### Liberty 파일

| 파일 | 설명 |
|------|------|
| `char_wl_driver.py` | Characterization 스크립트 (99 sims) |
| `wl_driver.lib` | 생성된 Liberty (7×7 timing tables) |
| `wl_driver.lef` | LEF (gen_lef.tcl로 생성) |

```bash
# 재실행 (~5분, 16코어)
cd $PROJECT_ROOT/analog/layout/wl_driver && python3 char_wl_driver.py
```

## 재현 방법

```bash
cd $PROJECT_ROOT/analog/layout/wl_driver

# 1. 레이아웃 생성 (디바이스 배치 + 배선)
magic -noconsole -dnull -rcfile $PDK_ROOT/sky130B/libs.tech/magic/sky130B.magicrc \
  << 'EOF'
source wl_driver.tcl
EOF

# 2. 탭 추가 + 재추출
magic -noconsole -dnull -rcfile $PDK_ROOT/sky130B/libs.tech/magic/sky130B.magicrc \
  << 'EOF'
source add_taps_wl.tcl
select top cell
flatten wl_driver_flat
load wl_driver_flat
extract all
ext2spice lvs
ext2spice
load wl_driver
gds write wl_driver.gds
EOF

# 3. LVS
netgen -batch lvs \
  "wl_driver_flat.spice wl_driver_flat" \
  "wl_driver_sch.spice wl_driver" \
  $PDK_ROOT/sky130B/libs.tech/netgen/sky130B_setup.tcl \
  lvs_report.txt
```
