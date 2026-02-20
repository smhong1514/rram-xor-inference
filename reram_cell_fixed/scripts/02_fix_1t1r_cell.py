#!/usr/bin/env python3
"""
================================================================================
1T1R Cell ReRAM Replacement Script
================================================================================

이 스크립트는 기존 RRAM_1T1R_new.gds 파일 내의 sky130_fd_pr_reram__reram_cell을
DRC 수정된 버전으로 교체합니다.

[입력]
  - ../gds/RRAM_1T1R_new.gds (원본 1T1R 셀)

[출력]
  - RRAM_1T1R_new_fixed.gds (ReRAM 셀이 교체된 버전)

[변경 내용]
  - sky130_fd_pr_reram__reram_cell 내부만 수정
  - Metal1: 320x260nm → 390x390nm
  - Metal2: 260x320nm → 390x390nm
  - 나머지 구조 (NFET, 배선 등)는 그대로 유지

================================================================================
"""

from pathlib import Path

# KLayout Python 모듈 사용
try:
    import klayout.db as db
except ImportError:
    print("ERROR: klayout 모듈이 필요합니다.")
    print("설치: pip install klayout")
    exit(1)


def fix_reram_cell(layout: db.Layout) -> None:
    """
    레이아웃 내의 sky130_fd_pr_reram__reram_cell을 DRC 수정 버전으로 교체
    """
    # 셀 찾기
    reram_cell = None
    for cell in layout.each_cell():
        if cell.name == "sky130_fd_pr_reram__reram_cell":
            reram_cell = cell
            break

    if reram_cell is None:
        raise ValueError("sky130_fd_pr_reram__reram_cell을 찾을 수 없습니다")

    # 레이어 정의
    MET1 = layout.layer(68, 20)
    MET1_PIN = layout.layer(68, 16)
    MET1_LABEL = layout.layer(68, 5)
    VIA = layout.layer(68, 44)
    MET2 = layout.layer(69, 20)
    MET2_PIN = layout.layer(69, 16)
    MET2_LABEL = layout.layer(69, 5)
    RERAM = layout.layer(201, 20)

    # 기존 shapes 삭제
    for li in layout.layer_indices():
        reram_cell.shapes(li).clear()

    # 새로운 shapes 삽입 (단위: nm)
    # ReRAM marker (320nm x 320nm)
    reram_cell.shapes(RERAM).insert(db.Box(-160, -160, 160, 160))

    # Metal1 (390nm x 390nm)
    reram_cell.shapes(MET1).insert(db.Box(-195, -195, 195, 195))
    reram_cell.shapes(MET1_PIN).insert(db.Box(-195, -195, 195, 195))
    reram_cell.shapes(MET1_LABEL).insert(db.Text("BE", 0, 0))

    # Via (150nm x 150nm)
    reram_cell.shapes(VIA).insert(db.Box(-75, -75, 75, 75))

    # Metal2 (390nm x 390nm)
    reram_cell.shapes(MET2).insert(db.Box(-195, -195, 195, 195))
    reram_cell.shapes(MET2_PIN).insert(db.Box(-195, -195, 195, 195))
    reram_cell.shapes(MET2_LABEL).insert(db.Text("TE", 0, 0))


def main():
    print("=" * 60)
    print("1T1R Cell ReRAM Replacement")
    print("=" * 60)

    # 경로 설정
    project_dir = Path(__file__).parent.parent.parent
    input_path = project_dir / "gds" / "RRAM_1T1R_new.gds"
    output_dir = Path(__file__).parent.parent / "gds"
    output_path = output_dir / "RRAM_1T1R_new_fixed.gds"

    if not input_path.exists():
        print(f"ERROR: 입력 파일을 찾을 수 없습니다: {input_path}")
        exit(1)

    # 레이아웃 로드
    layout = db.Layout()
    layout.dbu = 0.001  # 1nm
    layout.read(str(input_path))

    print(f"입력: {input_path}")

    # ReRAM 셀 수정
    fix_reram_cell(layout)

    # 저장
    output_dir.mkdir(parents=True, exist_ok=True)
    layout.write(str(output_path))

    print(f"출력: {output_path}")
    print()
    print("변경 내용:")
    print("  sky130_fd_pr_reram__reram_cell 내부만 수정")
    print("  Metal1: 320x260nm → 390x390nm")
    print("  Metal2: 260x320nm → 390x390nm")
    print("  나머지 구조는 그대로 유지")
    print("=" * 60)


if __name__ == "__main__":
    main()
