#!/usr/bin/env python3
"""
================================================================================
DRC-Fixed ReRAM Cell Generator for Sky130B PDK
================================================================================

이 스크립트는 DRC 오류가 수정된 sky130_fd_pr_reram__reram_cell을 생성합니다.

[문제점]
PDK 원본 sky130_fd_pr_reram__reram_cell.gds:
  - Metal1: 320nm x 260nm
  - Metal2: 260nm x 320nm
  - ReRAM marker: 320nm x 320nm
  - DRC 룰 위반: Metal이 ReRAM을 30nm 이상 감싸야 함 (surround reram *m1 30)

[해결책]
Metal1/Metal2를 390nm x 390nm로 확장하여 35nm overlap 확보

[생성 파일]
  - sky130_fd_pr_reram__reram_cell_new.gds

================================================================================
"""

import gdsfactory as gf
from gdsfactory.component import Component

# Generic PDK 활성화 (gdsfactory 9.x 필수)
gf.gpdk.PDK.activate()

# Sky130 레이어 정의
LAYER = {
    "met1": (68, 20),
    "met1_pin": (68, 16),
    "met1_label": (68, 5),
    "via": (68, 44),
    "met2": (69, 20),
    "met2_pin": (69, 16),
    "met2_label": (69, 5),
    "reram": (201, 20),
}


@gf.cell
def sky130_fd_pr_reram__reram_cell() -> Component:
    """
    DRC-Fixed ReRAM Cell

    Original (DRC error):
        Metal1: 320nm x 260nm
        Metal2: 260nm x 320nm

    Fixed:
        Metal1: 390nm x 390nm (35nm overlap)
        Metal2: 390nm x 390nm (35nm overlap)
    """
    c = Component()

    # 치수 (um 단위)
    reram_half = 0.160   # ReRAM marker half size (320nm / 2)
    metal_half = 0.195   # Metal half size (390nm / 2)
    via_half = 0.075     # Via half size (150nm / 2)

    # ReRAM marker (320nm x 320nm) - 변경 없음
    c.add_polygon(
        [(-reram_half, -reram_half), (reram_half, -reram_half),
         (reram_half, reram_half), (-reram_half, reram_half)],
        layer=LAYER["reram"]
    )

    # Metal1 (390nm x 390nm) - 확장됨
    c.add_polygon(
        [(-metal_half, -metal_half), (metal_half, -metal_half),
         (metal_half, metal_half), (-metal_half, metal_half)],
        layer=LAYER["met1"]
    )
    c.add_polygon(
        [(-metal_half, -metal_half), (metal_half, -metal_half),
         (metal_half, metal_half), (-metal_half, metal_half)],
        layer=LAYER["met1_pin"]
    )

    # Metal1 Label - "BE" (Bottom Electrode)
    c.add_label(text="BE", position=(0, 0), layer=LAYER["met1_label"])

    # Via (150nm x 150nm) - 변경 없음
    c.add_polygon(
        [(-via_half, -via_half), (via_half, -via_half),
         (via_half, via_half), (-via_half, via_half)],
        layer=LAYER["via"]
    )

    # Metal2 (390nm x 390nm) - 확장됨
    c.add_polygon(
        [(-metal_half, -metal_half), (metal_half, -metal_half),
         (metal_half, metal_half), (-metal_half, metal_half)],
        layer=LAYER["met2"]
    )
    c.add_polygon(
        [(-metal_half, -metal_half), (metal_half, -metal_half),
         (metal_half, metal_half), (-metal_half, metal_half)],
        layer=LAYER["met2_pin"]
    )

    # Metal2 Label - "TE" (Top Electrode)
    c.add_label(text="TE", position=(0, 0), layer=LAYER["met2_label"])

    return c


def main():
    from pathlib import Path

    print("=" * 60)
    print("DRC-Fixed ReRAM Cell Generator")
    print("=" * 60)

    # 출력 경로
    output_dir = Path(__file__).parent.parent / "gds"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 셀 생성
    cell = sky130_fd_pr_reram__reram_cell()

    # GDS 저장
    output_path = output_dir / "sky130_fd_pr_reram__reram_cell_new.gds"
    cell.write_gds(output_path)

    print(f"Output: {output_path}")
    print()
    print("치수:")
    print("  ReRAM marker: 320nm x 320nm")
    print("  Metal1: 390nm x 390nm (확장됨)")
    print("  Metal2: 390nm x 390nm (확장됨)")
    print("  Via: 150nm x 150nm")
    print("  Overlap: 35nm (DRC 요구: 30nm)")
    print("=" * 60)


if __name__ == "__main__":
    main()
