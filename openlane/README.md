# RRAM 2-Array XOR Neural Network - OpenLane Integration

Sky130 PDK 기반, 2개의 RRAM 4x4 크로스바 어레이를 이용한 **XOR 신경망 inference 칩**.
OpenLane RTL-to-GDS 플로우로 DRC/LVS 검증 완료.

## 검증 결과

| 항목 | 결과 |
|------|------|
| DRC (Magic) | **PASS** (0 violations) |
| LVS (Netgen) | **PASS** (0 errors) |
| Setup violations | 없음 |
| Hold violations | 없음 |

> Build: `RUN_2026.02.13_05.29.13`

---

## 1. XOR 신경망 아키텍처

### 1.1 왜 2-Array인가?

XOR은 선형 분리가 불가능하여 단일 레이어(=단일 RRAM 배열)로 구현 불가합니다.
2-레이어 분해가 필요합니다:

```
XOR(A,B) = AND( OR(A,B), NAND(A,B) )
```

단일 배열로는 OR과 AND에 서로 다른 RRAM weight가 필요한데,
동일 셀이 두 연산에 재사용되어 같은 weight로 두 함수를 수행할 수 없습니다.

### 1.2 2-Phase Time-Multiplexed Inference

```
          +--- Array 1 (Layer 1) ---+
          |  SL1 = {1, 1, B, A}     |
  A,B --> |  BL[0:1] -> SA1 -> h1 (OR)   |
          |  BL[2:3] -> SA2 -> h2 (NAND)  |
          +-----------------------------+
                    | h1, h2
                    v
          +--- Array 2 (Layer 2) ---+
          |  SL2 = {1, 1, h2, h1}   |
          |  BL[0:1] -> SA3 -> XOR result |
          +-----------------------------+
```

**Phase 0**: Array 1 활성 -> SA1(OR), SA2(NAND) 동시 latch -> h1, h2
**Phase 1**: Array 2 활성 -> SA3(AND) latch -> xor_result

### 1.3 하드웨어 구성 (21 매크로)

| 블록 | 수량 | 역할 |
|------|------|------|
| RRAM 4x4 Array | 2 | Array 1 (OR+NAND), Array 2 (AND) |
| WL Driver | 8 | 4 per array, 1.8V->HV 레벨 시프트 |
| Sense Amplifier | 3 | SA1(OR), SA2(NAND) for Array 1; SA3(AND) for Array 2 |
| BL Write Driver | 8 | 4 per array, inference 시 Hi-Z (EN=0) |

디지털 로직:
- `xor_controller`: 2-phase FSM (IDLE -> WL_ON -> SL_SETTLE -> SAE_WAIT -> LATCH -> DONE)
- `input_encoder`: phase별 SL 데이터 생성 (Array 1/2 각각)
- `sae_control`: SA enable 타이밍 펄스 생성

---

## 2. 파일 구조

```
openlane/
+-- config.json                        # OpenLane 메인 설정
+-- config/
|   +-- macro_placement.cfg            # 21개 매크로 배치 좌표
+-- src/                               # Verilog RTL
|   +-- rram_ctrl_top.v                # Top 모듈 (21 매크로 통합)
|   +-- xor_controller.v              # XOR inference FSM (2-phase)
|   +-- input_encoder.v               # Phase별 SL 생성
|   +-- sae_control.v                 # SA enable 타이밍
|   +-- rram_blackbox.v               # RRAM 매크로 blackbox
|   +-- wl_driver_blackbox.v          # WL Driver blackbox
|   +-- sense_amp_blackbox.v          # Sense Amp blackbox
|   +-- bl_write_driver_blackbox.v    # BL Write Driver blackbox
|   +-- tb_xor_inference.v            # Testbench (참고용)
+-- lef/                               # 매크로 LEF (핀 위치, OBS)
|   +-- rram_4x4_array.lef            # * nwell OBS 추가됨 (핵심!)
|   +-- wl_driver.lef
|   +-- sense_amp.lef
|   +-- bl_write_driver.lef
+-- gds/                               # 매크로 GDS (레이아웃)
|   +-- rram_4x4_array.gds
|   +-- wl_driver.gds
|   +-- sense_amp.gds
|   +-- bl_write_driver.gds
+-- lib/                               # 매크로 Liberty (타이밍)
|   +-- wl_driver.lib
|   +-- sense_amp.lib
|   +-- bl_write_driver.lib
+-- sky130_fd_pr_reram__reram_cell.mag # RRAM 셀 포트 정의 (LVS용)
+-- runs/RUN_2026.02.13_05.29.13/     # 최종 빌드 결과
```

### 각 파일의 역할

| 파일 | 역할 | 없으면? |
|------|------|---------|
| `config.json` | OpenLane 빌드 설정 전체 | 빌드 불가 |
| `macro_placement.cfg` | 21개 매크로 좌표 지정 | 자동 배치 (DRC/LVS 실패) |
| `src/*.v` | RTL 소스 코드 | 빌드 불가 |
| `lef/*.lef` | 매크로 핀 위치, OBS, nwell | 라우팅/LVS 실패 |
| `gds/*.gds` | 매크로 물리 레이아웃 | GDS 병합 실패 |
| `lib/*.lib` | 타이밍/전력 정보 | 합성 경고 (동작에는 영향 없음) |
| `*.mag` | RRAM 셀 포트 정의 (TE/BE) | 매크로 내부 LVS 실패 |

---

## 3. 빌드 방법

### 3.1 사전 요구사항

**Docker**:
```bash
sudo apt-get install docker.io
sudo usermod -aG docker $USER
```

**PDK (open_pdks sky130B + RRAM)**:
```bash
git clone https://github.com/RTimothyEdwards/open_pdks.git
cd open_pdks
git checkout bdc9412b    # OpenLane 1.1.1 매칭 버전

./configure --enable-sky130-pdk \
            --enable-reram-sky130 \
            --disable-klayout-sky130 \
            --prefix=$HOME/pdk_matched

make -j1
make install

# ~/.bashrc에 추가
export PDK_ROOT=$HOME/pdk_matched/share/pdk
export PDK=sky130B
```

> `--enable-reram-sky130` 없이 빌드하면 RRAM 라이브러리가 누락됩니다.

### 3.2 OpenLane 실행

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

> **PDK 마운트**: 호스트와 동일한 경로로 마운트해야 합니다.
> sky130B 내부 파일이 sky130A로 절대경로 심볼릭 링크되어 있기 때문입니다.

### 3.3 결과 확인

```bash
# DRC 결과 (0이면 통과)
cat runs/*/reports/signoff/drc.rpt

# LVS 결과 ("Total errors = 0" 확인)
cat runs/*/reports/signoff/*lvs.rpt

# 타이밍 확인
grep -i "violation" runs/*/reports/signoff/*sta*/*.rpt

# 최종 GDS
ls runs/*/results/final/gds/rram_ctrl_top.gds
```

---

## 4. config.json 설정 해설

### 4.1 Verilog 소스

```json
"VERILOG_FILES": [
    "dir::src/rram_blackbox.v",          // RRAM 매크로 blackbox
    "dir::src/wl_driver_blackbox.v",     // WL Driver blackbox
    "dir::src/sense_amp_blackbox.v",     // Sense Amp blackbox
    "dir::src/bl_write_driver_blackbox.v", // BL Write Driver blackbox
    "dir::src/xor_controller.v",         // XOR inference FSM
    "dir::src/input_encoder.v",          // Phase별 SL 생성
    "dir::src/sae_control.v",            // SAE 타이밍
    "dir::src/rram_ctrl_top.v"           // Top 모듈
]
```

blackbox 4개 + 디지털 로직 3개 + top = 8개 파일.
blackbox는 합성 시 빈 모듈로 처리되고, EXTRA_LEFS에서 물리 정보를 가져옵니다.

### 4.2 Floorplan

```json
"FP_SIZING": "absolute",
"DIE_AREA": "0 0 200 200",      // 200x200um (21 매크로 수용)
"FP_PDN_AUTO_ADJUST": false,     // PDN 자동조정 비활성 (매크로 충돌 방지)
"PL_TARGET_DENSITY": 0.35,       // 배치 밀도 (매크로 많으므로 낮게)
"FP_CORE_UTIL": 25,              // 코어 활용률 25%
```

21개 매크로가 있어서 밀도/활용률을 낮춰야 합니다.
`FP_PDN_AUTO_ADJUST=false`는 PDN 그리드가 매크로와 충돌하는 것을 방지합니다.

### 4.3 매크로 통합

```json
"EXTRA_LEFS": ["dir::lef/rram_4x4_array.lef", ...],    // 4종 매크로 LEF
"EXTRA_GDS_FILES": ["dir::gds/rram_4x4_array.gds", ...], // 4종 GDS
"EXTRA_LIBS": ["dir::lib/wl_driver.lib", ...],           // 3종 Liberty (RRAM 제외)
"MACRO_PLACEMENT_CFG": "dir::config/macro_placement.cfg"
```

RRAM은 LIB가 없습니다 (순수 패시브 소자).
WL Driver, SA, BL WD는 LIB 제공하여 합성기에 타이밍 정보 전달.

### 4.4 Power

```json
"VDD_NETS": "vccd1",
"GND_NETS": "vssd1",
"FP_PDN_ENABLE_MACROS_GRID": false,  // blackbox 매크로에 PDN 그리드 비활성
"SYNTH_USE_PG_PINS_DEFINES": "USE_POWER_PINS",
"LVS_INSERT_POWER_PINS": false       // blackbox power pin 자동삽입 비활성
```

blackbox 매크로는 내부 power 라우팅 정보가 없으므로
`FP_PDN_ENABLE_MACROS_GRID=false`와 `LVS_INSERT_POWER_PINS=false`가 필수입니다.

### 4.5 라우팅

```json
"DRT_OPT_ITERS": 64,           // 상세 라우팅 최적화 반복 (기본 32)
"GRT_ADJUSTMENT": 0.3,          // 글로벌 라우팅 리소스 (높을수록 보수적)
"GRT_ALLOW_CONGESTION": true    // congestion 허용 (매크로 밀집)
```

21개 매크로가 밀집되어 있어 congestion이 발생할 수 있습니다.
`GRT_ALLOW_CONGESTION=true`로 라우팅 실패를 방지하고,
`DRT_OPT_ITERS=64`로 상세 라우팅 품질을 높입니다.

### 4.6 DRC/LVS 관련 (핵심)

```json
"FP_TAPCELL_DIST": 6,           // *** Tap 셀 간격 6um (기본 13)
"QUIT_ON_MAGIC_DRC": false,      // DRC 에러 있어도 빌드 계속
"QUIT_ON_LVS_ERROR": false       // LVS 에러 있어도 빌드 계속
```

**`FP_TAPCELL_DIST=6`이 핵심입니다.** 기본값 13um에서는 매크로 사이의
좁은 row segment(~13um)에 tap 셀이 배치되지 않아 LU.2 DRC 위반이 발생합니다.
6um으로 줄이면 좁은 segment에도 tap이 배치됩니다.

### 4.7 PDN 그리드

```json
"pdk::sky130*": {
    "FP_PDN_VOFFSET": 5,     // 수직 power strap 오프셋 5um
    "FP_PDN_HOFFSET": 5,     // 수평 power strap 오프셋 5um
    "FP_PDN_VPITCH": 40,     // 수직 power strap 간격 40um
    "FP_PDN_HPITCH": 40      // 수평 power strap 간격 40um
}
```

기본값(~153um)보다 밀집된 40um pitch로 21개 매크로에 안정적 전력 공급.

---

## 5. 매크로 배치 전략

### 5.1 배치 원칙

```
macro_placement.cfg 형식:
instance_name  x  y  orientation
```

**핵심 원칙: 매크로를 core 좌측 edge 가까이 배치 (x=6um)**

OpenLane의 standard cell row는 매크로에 의해 segment로 분할됩니다.
매크로가 core 중앙에 있으면 좌측 edge에 좁은 filler-only segment가 생겨
nwell 단절 (LVS VPB 에러) 및 tap 부재 (DRC LU.2 위반)이 발생합니다.

```
나쁜 배치 (매크로가 중앙):
Core edge  |  좁은 gap (filler만)  |  매크로  |  넓은 영역 ...
x=5.52     x=35                    x=43

좋은 배치 (매크로가 edge 근처):
Core edge | 매크로 (바로 시작)      |  넓은 영역 ...
x=5.52    x=6                      x=14
```

### 5.2 현재 배치

```
200x200um die 기준:

    y=90  [WL 1_1][WL 1_3]        [WL 2_1][WL 2_3]
    y=80  [         ][RRAM 1][SA1][SA2]  [         ][RRAM 2][SA3]
    y=75  [WL 1_0][WL 1_2]        [WL 2_0][WL 2_2]
              |                         |
       Array 1 (left)              Array 2 (right)

    y=20  [BL 1_0..1_3]           [BL 2_0..2_3]
          x=6    x=36             x=50   x=80
```

### 5.3 매크로 크기 참조

| 매크로 | SIZE (um) | 핀 |
|--------|-----------|-----|
| RRAM 4x4 Array | 17.87 x 25.15 | WL[3:0], BL[3:0], SL[3:0], GND |
| WL Driver | 8.04 x 12.36 | IN, OUT, VDD, VWL, VSS |
| Sense Amplifier | 3.63 x 10.96 | SAE, INP, INN, Q, QB, VDD, VSS |
| BL Write Driver | 4.92 x 11.86 | EN, DATA, BL, VDD, VSS |

---

## 6. DRC/LVS 성공을 위한 핵심 수정 3가지

### 6.1 RRAM LEF에 nwell OBS 추가

**문제**: RRAM 매크로 LEF에 nwell 레이어가 없으면 standard cell의 연속 nwell이 끊김.
filler 셀의 VPB(nwell 기판 연결)가 vccd1에서 분리되어 LVS 에러 발생.

```
[std cells] -- nwell 연속 -- [RRAM: nwell 없음!] -- nwell 끊김 -- [std cells]
                                                      |
                                               filler VPB 고립 -> LVS 에러
```

**해결**: `rram_4x4_array.lef`의 OBS 섹션에 매크로 전체를 덮는 nwell 추가:

```
OBS
  LAYER nwell ;
    RECT 0.000 0.000 17.870 25.150 ;  <- 매크로 전체 SIZE
  LAYER li1 ;
    ...
END
```

이것으로 RRAM을 관통하는 nwell 연속성이 유지됩니다.

> **주의**: WL Driver, SA, BL WD에는 nwell OBS를 추가하면 안 됩니다!
> WL Driver는 HV nwell(VWL 핀)이 있어서 LV nwell OBS와 인접하면 nwell.8 DRC 위반 발생.

### 6.2 매크로를 Core 좌측 Edge에 배치

**문제**: 매크로가 core 중앙에 있으면 좌측에 좁은 filler-only row segment 생성.
이 segment에 tap 셀이 없으면:
- nwell.4: 고립된 nwell에 N+ tap 없음
- LU.2/LU.3: N-diff/P-diff에서 P-tap/N-tap까지 거리 > 15um
- LVS: filler VPB가 vccd1과 분리

**해결**: `macro_placement.cfg`에서 가장 왼쪽 매크로를 x=6um에 배치.
Core 좌측 edge가 ~5.52um이므로 gap이 거의 없어져 고립 segment 방지.

### 6.3 FP_TAPCELL_DIST 축소

**문제**: 매크로 사이의 좁은 row segment (~13um)에 기본 tap 간격 (13um)으로는
tap 셀이 배치되지 않아 LU.2 위반 발생.

**해결**: `config.json`에 `"FP_TAPCELL_DIST": 6` 추가.
6um 간격이면 13um 폭 segment에도 최소 1-2개 tap이 배치됨.

---

## 7. 트러블슈팅

### LVS: VPB isolated net 에러 (net count difference)

**증상**: netgen에서 `net count difference`, `unmatched nets` 에러. VPB 관련.

**원인**: 매크로 주변 filler 셀의 nwell(VPB)이 vccd1 power rail에서 분리됨.

**확인 방법**:
```bash
# 추출된 SPICE에서 VPB 확인
grep "VPB" runs/*/results/signoff/rram_ctrl_top.spice | grep FILLER
```

**해결 우선순위**:
1. RRAM LEF에 nwell OBS 추가 (6.1절)
2. 매크로를 core edge에 배치 (6.2절)
3. FP_TAPCELL_DIST 축소 (6.3절)

### DRC: nwell.8 (HV-LV nwell spacing)

**증상**: `HV nwell spacing to LV nwell < 2.0um`

**원인**: WL Driver LEF에 full-extent nwell OBS를 추가하면 LV nwell 생성.
인접 WL Driver의 HV nwell(VWL 핀)과 간격이 2.0um 미만.

**해결**: WL Driver, SA, BL WD의 nwell OBS 제거. PIN에 이미 nwell이 있으므로 불필요.

### DRC: LU.2/LU.3 (Latchup distance)

**증상**: `N-diff distance to P-tap must be < 15.0um`

**원인**: 좁은 row segment에 tap 셀 누락.

**해결**: `"FP_TAPCELL_DIST": 6` 설정.

### "No access point for pin" 에러

**원인**: LEF OBS가 핀 영역을 차단.

**해결**: LEF에서 핀 주변 OBS 영역을 RECT에서 제외.

### RRAM 매크로 내부 LVS 실패 (68 errors)

**원인**: PDK의 `sky130_fd_pr_reram__reram_cell.mag`에 포트 정의가 없음.

**해결**: 포트 정의가 포함된 `.mag` 파일을 작업 디렉토리에 복사:
```
sky130_fd_pr_reram__reram_cell.mag:
<< labels >>
flabel metal2 s -39 -39 39 39 0 FreeSans 160 0 0 0 TE
port 0 nsew
flabel metal1 s -39 -39 39 39 0 FreeSans 160 0 0 0 BE
port 1 nsew
```

### Docker "not a TTY" 에러

**해결**: `-it` 대신 `--rm`만 사용.

---

## 8. 빌드 경고 (무시 가능)

| 경고 | 설명 | 조치 필요? |
|------|------|-----------|
| Max fanout violations | CTS 클록 버퍼 fanout 초과. slew/cap violation 0건, slack 충분 | 아니오 |
| VSRC_LOC_FILES 미설정 | IR drop 분석용. standalone 매크로에서 불필요 | Caravan 통합 시 |
| KLayout GDS XOR 스킵 | `RUN_KLAYOUT=false` 설정으로 의도적 스킵 | 아니오 |
| Deprecated 설정 | `SYNTH_MAX_FANOUT` 등 이름 변경. 하위 호환 자동 매핑 | 선택적 |
| SDC 미설정 | 기본 SDC 사용 (CLOCK_PERIOD=50ns). 20MHz에 충분 | 선택적 |

---

## 9. 참고

- **PDK**: open_pdks sky130B (commit `bdc9412b`, OpenLane 1.1.1 매칭)
- **OpenLane**: 1.x (efabless/openlane:latest)
- **GDS 원점**: 모든 매크로 GDS는 (0,0) 원점 정렬 필수
- **5nm 그리드**: 모든 좌표는 Sky130 제조 그리드 (0.005um) 정렬
- **Docker 마운트**: PDK 경로를 호스트와 동일하게 마운트 (sky130B->sky130A 심볼릭 링크)

---

## 라이선스

교육 및 연구 목적으로 제공됩니다.
