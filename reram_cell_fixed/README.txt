================================================================================
RRAM DRC Fix Documentation
Sky130B PDK - ReRAM Cell Metal Overlap Correction
================================================================================
Date: 2026-02-04
================================================================================

목차
----
1. 문제점
2. 원인 분석
3. 해결 방법
4. 파일 구조
5. 사용 방법
6. DRC 검증 결과


================================================================================
1. 문제점
================================================================================

기존 RRAM 4x4 어레이에서 160개의 DRC 에러 발생:
  - "Metal1 overlap of ReRAM < 0.03um in one direction (via.5a - via.4a)"
  - "Metal2 overlap of ReRAM < 0.03um in one direction (met2.5 - met2.4)"


================================================================================
2. 원인 분석
================================================================================

[Sky130B DRC 룰]
sky130B.tech 파일 (Line 4659-4661):
  surround reram *m1,rm1 30 directional
      "Metal1 overlap of ReRAM < %d in one direction (via.5a - via.4a)"
  surround reram *m2,rm2 30 directional
      "Metal2 overlap of ReRAM < %d in one direction (met2.5 - met2.4)"

→ Metal1/Metal2가 ReRAM 마커를 사방으로 30nm 이상 감싸야 함

[PDK 원본 sky130_fd_pr_reram__reram_cell.gds 치수]
  - ReRAM marker (201/20): 320nm x 320nm
  - Metal1 (68/20): 320nm x 260nm  ← Y방향 30nm 부족
  - Metal2 (69/20): 260nm x 320nm  ← X방향 30nm 부족
  - Via (68/44): 150nm x 150nm

[Overlap 분석]
  Metal1:
    - 좌/우: 0nm (경계 일치)
    - 상/하: -30nm (Metal1이 ReRAM 안쪽)  ← DRC 위반

  Metal2:
    - 좌/우: -30nm (Metal2가 ReRAM 안쪽)  ← DRC 위반
    - 상/하: 0nm (경계 일치)


================================================================================
3. 해결 방법
================================================================================

[수정 치수]
  - ReRAM marker: 320nm x 320nm (변경 없음)
  - Metal1: 390nm x 390nm (확장)
  - Metal2: 390nm x 390nm (확장)
  - Via: 150nm x 150nm (변경 없음)

[Overlap 결과]
  - 사방 35nm overlap 확보 (DRC 요구: 30nm)

[수정 도구]
  - KLayout Ruby 스크립트로 GDS 파일 내 shape 직접 수정
  - 또는 Python (gdsfactory) 스크립트로 새로 생성


================================================================================
4. 파일 구조
================================================================================

fixed/
├── gds/
│   ├── sky130_fd_pr_reram__reram_cell_new.gds  # DRC 수정된 ReRAM 셀
│   ├── RRAM_1T1R_new_fixed.gds                 # DRC 수정된 1T1R 셀
│   └── rram_4x4_array_fixed.gds                # DRC 클린 4x4 어레이
│
├── scripts/
│   ├── 01_generate_reram_cell.py    # ReRAM 셀 생성 (gdsfactory)
│   ├── 02_fix_1t1r_cell.py          # 1T1R 셀 ReRAM 교체 (klayout)
│   └── 03_generate_array.py         # 4x4 어레이 생성 (gdsfactory)
│
└── README.txt                       # 이 문서


================================================================================
5. 사용 방법
================================================================================

[사전 준비]
# Python 가상환경 생성 및 패키지 설치
python3 -m venv ~/venv_gds
source ~/venv_gds/bin/activate
pip install gdsfactory klayout

[스크립트 실행]

1. ReRAM 셀 생성:
   cd ~/rram_sky130_project/fixed/scripts
   source ~/venv_gds/bin/activate
   python 01_generate_reram_cell.py

2. 1T1R 셀 수정 (기존 GDS에서 ReRAM만 교체):
   python 02_fix_1t1r_cell.py

3. 4x4 어레이 생성:
   python 03_generate_array.py

[배열 크기 변경]
03_generate_array.py의 main() 함수에서:
   ROWS = 4  # 원하는 행 수로 변경
   COLS = 4  # 원하는 열 수로 변경


================================================================================
6. DRC 검증 결과
================================================================================

[검증 명령어]
magic -T $PDK/libs.tech/magic/sky130B.tech
gds read rram_4x4_array_fixed.gds
load <top_cell>
drc style drc(full)
drc check
drc count

[결과]
┌─────────────────────────────────────┬─────────────┬─────────────┐
│ 파일                                 │ 수정 전     │ 수정 후     │
├─────────────────────────────────────┼─────────────┼─────────────┤
│ sky130_fd_pr_reram__reram_cell      │ 6 에러      │ 0 에러 ✓    │
│ RRAM_1T1R_new                       │ 에러 있음   │ 0 에러 ✓    │
│ rram_4x4_array                      │ 160 에러    │ 0 에러 ✓    │
└─────────────────────────────────────┴─────────────┴─────────────┘


================================================================================
참고 사항
================================================================================

[Sky130 레이어 정보]
  Layer 68/20  = met1.drawing (Metal1)
  Layer 68/16  = met1.pin
  Layer 68/5   = met1.label
  Layer 68/44  = via.drawing (Via)
  Layer 69/20  = met2.drawing (Metal2)
  Layer 69/16  = met2.pin
  Layer 69/5   = met2.label
  Layer 201/20 = reram.drawing (ReRAM marker)

[DRC 룰 파일 위치]
  $PDK_ROOT/sky130B/libs.tech/magic/sky130B.tech
  Line 4657-4664: ReRAM 관련 DRC 룰

[PDK ReRAM 셀 위치]
  $PDK_ROOT/sky130B/libs.ref/sky130_fd_pr_reram/gds/

================================================================================
