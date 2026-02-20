# Analog Block Layout (Sky130B PDK)

RRAM XOR 신경망 프로젝트의 아날로그 블록 3개에 대한 물리 레이아웃.
Magic VLSI Tcl batch scripting으로 생성, Sky130B PDK 디바이스만 사용.

## 블록 요약

| 블록 | 트랜지스터 | PDK 디바이스 | 전압 | DRC | LVS | Liberty |
|------|-----------|-------------|------|-----|-----|---------|
| [BL Write Driver](bl_write_driver/) | 8T (4P+4N) | pfet/nfet_01v8 | 1.8V only | 0 errors | PASS | ✅ |
| [Sense Amplifier](sense_amp/) | 10T (5P+5N) | pfet/nfet_01v8 | 1.8V only | 0 errors | PASS | ✅ |
| [WL Driver](wl_driver/) | 8T (4P+4N) | pfet/nfet_01v8 + pfet/nfet_g5v0d10v5 | 1.8V + HV | 0 errors | PASS | ✅ |

## 폴더 구조

```
layout/
├── README.md                 ← 이 파일
├── add_taps.tcl              # BL Writer + SA 공용 탭 추가 스크립트
├── gen_lef.tcl               # LEF 생성 스크립트 (Magic batch)
├── gen_lib.py                # 블랙박스 LIB stub 생성 (characterization 이전 버전)
├── gen_all.sh                # LEF/LIB 일괄 생성 wrapper
├── devices/                  # PDK 디바이스 셀 (.mag)
│   └── (dev_*.mag 10개)     #   Sky130B PDK _draw로 생성
├── bl_write_driver/          # BL Write Driver (8T, tri-state buffer)
│   ├── README.md
│   ├── bl_write_driver.tcl   #   레이아웃 생성 스크립트
│   ├── bl_write_driver.mag   #   레이아웃
│   ├── bl_write_driver.gds   #   GDS
│   ├── bl_write_driver.lef   #   LEF
│   ├── bl_write_driver.lib   #   ⭐ ngspice characterized Liberty
│   ├── char_bl_write_driver.py  # Liberty characterization 스크립트
│   ├── bl_write_driver_flat.spice  # 추출 netlist
│   ├── bl_write_driver_sch.spice   # schematic netlist
│   └── lvs_report.txt
├── sense_amp/                # Sense Amplifier (10T, StrongARM latch)
│   ├── README.md
│   ├── sense_amp.tcl
│   ├── sense_amp.mag
│   ├── sense_amp.gds
│   ├── sense_amp.lef
│   ├── sense_amp.lib         #   ⭐ ngspice characterized Liberty
│   ├── char_sense_amp.py     #   Liberty characterization 스크립트
│   ├── sense_amp_flat.spice
│   ├── sense_amp_sch.spice
│   └── lvs_report.txt
├── wl_driver/                # WL Driver (8T, level shifter + HV buffer)
│   ├── README.md
│   ├── wl_driver.tcl
│   ├── add_taps_wl.tcl
│   ├── wl_driver.mag
│   ├── wl_driver.gds
│   ├── wl_driver.lef
│   ├── wl_driver.lib         #   ⭐ ngspice characterized Liberty
│   ├── char_wl_driver.py     #   Liberty characterization 스크립트
│   ├── wl_driver_flat.spice
│   ├── wl_driver_sch.spice
│   └── lvs_report.txt
└── archive/                  # 개발 중 테스트 파일들 (참고용)
```

## 사용된 Sky130B PDK 디바이스

모든 디바이스는 Sky130B PDK `_draw` 함수로 생성:

| Layout Cell | PDK Device | W (um) | L (um) | 사용 블록 |
|-------------|-----------|--------|--------|----------|
| `dev_pfet_w050` | `sky130_fd_pr__pfet_01v8` | 0.5 | 0.15 | BL, SA |
| `dev_nfet_w050` | `sky130_fd_pr__nfet_01v8` | 0.5 | 0.15 | BL, WL |
| `dev_pfet_w100` | `sky130_fd_pr__pfet_01v8` | 1.0 | 0.15 | SA, WL |
| `dev_nfet_w100` | `sky130_fd_pr__nfet_01v8` | 1.0 | 0.15 | SA |
| `dev_nfet_w200` | `sky130_fd_pr__nfet_01v8` | 2.0 | 0.15 | SA |
| `dev_pfet_w400` | `sky130_fd_pr__pfet_01v8` | 4.0 | 0.15 | BL |
| `dev_nfet_w400` | `sky130_fd_pr__nfet_01v8` | 4.0 | 0.15 | BL |
| `dev_hv_pfet_w100` | `sky130_fd_pr__pfet_g5v0d10v5` | 1.0 | 0.5 | WL |
| `dev_hv_nfet_w200` | `sky130_fd_pr__nfet_g5v0d10v5` | 2.0 | 0.5 | WL |
| `dev_hv_pfet_w400` | `sky130_fd_pr__pfet_g5v0d10v5` | 4.0 | 0.5 | WL |

### 디바이스 생성 방법

```tcl
# Magic batch mode에서 Sky130B PDK _draw 함수 호출
set pars [sky130::sky130_fd_pr__nfet_01v8_defaults]
dict set pars w 2.0        ;# Width
dict set pars l 0.15       ;# Length
dict set pars nf 1         ;# Number of fingers
dict set pars guard 0      ;# No guard ring
dict set pars full_metal 1  ;# Full metal1 contacts
sky130::sky130_fd_pr__nfet_01v8_draw $pars
save dev_nfet_w200
```

- `_draw` 함수 직접 호출 필수 (`magic::gencell`은 파라미터 무시 버그)
- `guard 0`: guard ring 없음 (수동으로 ntap/ptap 추가)
- `full_metal 1`: source/drain에 전체 met1 contact 생성

## 레이아웃 제작 흐름

```
1. 디바이스 생성     devices/gen_devices.tcl
       ↓              Sky130B PDK _draw → dev_*.mag
2. 레이아웃 스크립트  {block}/{block}.tcl
       ↓              getcell 배치 → met1/met2 배선 → 라벨/포트
3. 탭 추가           add_taps.tcl / add_taps_wl.tcl
       ↓              nwell merge → ntap/ptap → met1 bridge
4. Flatten + 추출    Magic: flatten → extract all → ext2spice lvs
       ↓              {block}_flat.spice 생성
5. LVS 검증          netgen: layout vs schematic netlist 비교
       ↓              lvs_report.txt
6. GDS 생성          Magic: gds write {block}.gds
7. LEF 생성          gen_lef.tcl (port class/use 설정 → lef write)
8. Liberty 생성      char_{block}.py (ngspice 7×7 sweep → .lib)
```

## 좌표계

- `magscale 1 2`: **2 internal units = 1 lambda**
- `.mag` 파일: internal 좌표 저장
- `box` 명령: **lambda** 좌표 사용
- 변환: lambda = internal / 2

## 핵심 교훈: Substrate/Well Tap

LVS 매칭을 위해 반드시 ntap (nwell→VDD/VWL) + ptap (psub→VSS) 추가 필요.

**met1 bridge가 디바이스 gate/drain met1과 겹치면 단락 발생:**
- 디바이스의 Gate Top/Bottom met1 좌표를 `.mag` 파일에서 확인
- 특히 large W 디바이스는 met1이 예상보다 멀리 확장
- WL Driver 사례: MP3(W=4) Gate Top이 y=570.5-593.5까지 → bridge를 x=1420에서 절단

## Liberty Characterization (ngspice)

각 블록에 대해 ngspice 시뮬레이션 기반 정식 Liberty (.lib) 파일 생성.
Python multiprocessing (16코어 병렬), 7×7 sweep (input_slew × output_load).

### 측정 조건

- **PDK**: Sky130B tt corner, 25°C
- **Slew**: 0.01 ~ 1.65 ns (7점, 20%-80%)
- **Load**: 0.5 fF ~ 316 fF (7점)
- **Threshold**: delay 50%, slew 20%-80%
- **Capacitance**: AC analysis @ 1GHz

### 결과 요약

| 블록 | Arcs | 시뮬레이션 수 | 시간 | 주요 delay |
|------|------|-------------|------|-----------|
| BL Write Driver | DATA→BL (pos), EN→BL (3state) | 197 | ~10분 | 0.07~1.09 ns |
| Sense Amplifier | SAE→Q/QB (neg, eval+prech) | 100 | ~5분 | 0.05~5.11 ns |
| WL Driver | IN→OUT (pos, 3.3V) | 99 | ~5분 | 0.26~1.84 ns |

### 재실행

```bash
cd $PROJECT_ROOT/analog/layout
(cd bl_write_driver && python3 char_bl_write_driver.py)
(cd sense_amp && python3 char_sense_amp.py)
(cd wl_driver && python3 char_wl_driver.py)
```

## 도구 버전

- Magic: 8.3 revision 599
- netgen: Sky130B setup (`sky130B_setup.tcl`)
- ngspice: `/usr/local/bin/ngspice` (characterization)
- PDK: Sky130B (`bdc9412b`, OpenLane 1.1.1 매칭)
- rcfile: `$PDK_ROOT/sky130B/libs.tech/magic/sky130B.magicrc`
