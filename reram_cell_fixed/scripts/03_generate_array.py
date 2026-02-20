#!/usr/bin/env python3
"""
================================================================================
RRAM NxM Array GDS Generator (gdsfactory 9.x compatible)
================================================================================

DRC 수정된 1T1R 셀을 사용하여 RRAM 어레이를 생성합니다.

[입력]
  - RRAM_1T1R_new_fixed.gds (DRC 수정된 1T1R 셀)

[출력]
  - rram_4x4_array_fixed.gds (DRC 클린 어레이)

[사용법]
  source ~/venv_gds/bin/activate
  python 03_generate_array.py

[배열 크기 변경]
  main() 함수에서 ROWS, COLS 값을 변경

================================================================================
"""

import os
from pathlib import Path

# PDK 환경변수 제거
if "PDK" in os.environ:
    del os.environ["PDK"]

import gdsfactory as gf
from gdsfactory.component import Component

# Generic PDK 활성화 (gdsfactory 9.x 필수)
gf.gpdk.PDK.activate()

# 경로 설정
PROJECT_DIR = Path(__file__).parent.parent
CELL_1T1R_GDS = PROJECT_DIR / "gds" / "RRAM_1T1R_new_fixed.gds"  # DRC 수정된 1T1R 셀
OUTPUT_DIR = PROJECT_DIR / "gds"

# Sky130 레이어 정의
LAYER = {
    "li1":  (67, 20),
    "met1": (68, 20),
    "met1_label": (68, 5),
    "via":  (68, 44),
    "met2": (69, 20),
    "met2_label": (69, 5),
    "via2": (69, 44),
    "met3": (70, 20),
    "met3_label": (70, 5),
    "text": (83, 44),  # 시각적 텍스트 라벨
}

# 그리드 설정
GRID = 0.005
GRID_INV = 200

def g(v: float) -> float:
    """5nm 그리드에 스냅"""
    return round(v * GRID_INV) / GRID_INV

# Via 크기
VIA_SIZE = 0.15
VIA2_SIZE = 0.20
VIA_PAD = g(0.32)
VIA2_PAD = g(0.37)


def load_cell() -> Component:
    """1T1R 셀 GDS 로드"""
    if not CELL_1T1R_GDS.exists():
        raise FileNotFoundError(f"1T1R 셀을 찾을 수 없습니다: {CELL_1T1R_GDS}")
    cell = gf.import_gds(CELL_1T1R_GDS)
    return cell


@gf.cell
def via_m1_m2() -> Component:
    """Metal1-Via-Metal2 스택"""
    c = Component()
    size = VIA_PAD
    c.add_polygon(
        [(-size/2, -size/2), (size/2, -size/2), (size/2, size/2), (-size/2, size/2)],
        layer=LAYER["met1"]
    )
    c.add_polygon(
        [(-VIA_SIZE/2, -VIA_SIZE/2), (VIA_SIZE/2, -VIA_SIZE/2),
         (VIA_SIZE/2, VIA_SIZE/2), (-VIA_SIZE/2, VIA_SIZE/2)],
        layer=LAYER["via"]
    )
    c.add_polygon(
        [(-size/2, -size/2), (size/2, -size/2), (size/2, size/2), (-size/2, size/2)],
        layer=LAYER["met2"]
    )
    return c


@gf.cell
def via_m2_m3() -> Component:
    """Metal2-Via2-Metal3 스택"""
    c = Component()
    size = VIA2_PAD
    c.add_polygon(
        [(-size/2, -size/2), (size/2, -size/2), (size/2, size/2), (-size/2, size/2)],
        layer=LAYER["met2"]
    )
    c.add_polygon(
        [(-VIA2_SIZE/2, -VIA2_SIZE/2), (VIA2_SIZE/2, -VIA2_SIZE/2),
         (VIA2_SIZE/2, VIA2_SIZE/2), (-VIA2_SIZE/2, VIA2_SIZE/2)],
        layer=LAYER["via2"]
    )
    c.add_polygon(
        [(-size/2, -size/2), (size/2, -size/2), (size/2, size/2), (-size/2, size/2)],
        layer=LAYER["met3"]
    )
    return c


@gf.cell
def create_rram_array(rows: int = 4, cols: int = 4) -> Component:
    """RRAM NxM 배열 생성"""
    c = Component()

    # 1T1R 셀 로드
    cell = load_cell()
    bbox = cell.dbbox()
    cell_w = g(bbox.right - bbox.left)
    cell_h = g(bbox.top - bbox.bottom)
    ox = g(-bbox.left)
    oy = g(-bbox.bottom)

    # 1T1R 셀 내부 핀 위치
    VWL_X = 0.690
    VBL_X = 1.715
    VS_Y = 0.49
    VWL_VIA_Y = 2.335
    VBL_VIA_Y = 1.99
    VS_VIA_X = -0.25

    # 레이아웃 파라미터
    pitch_x = g(4.0)
    pitch_y = g(5.5)
    margin = g(3.0)
    wl_w = g(0.36)
    bl_w = g(0.32)
    sl_w = g(0.32)

    print(f"Cell: {CELL_1T1R_GDS.name}")
    print(f"Cell size: {cell_w:.3f} x {cell_h:.3f} um")

    # 셀 배치
    for row in range(rows):
        for col in range(cols):
            ref = c.add_ref(cell)
            x = g(margin + col * pitch_x + ox)
            y = g(margin + row * pitch_y + oy)
            ref.dmove((x, y))

    # 배열 경계
    array_x_min = margin
    array_x_max = g(margin + (cols - 1) * pitch_x + ox + cell_w)
    array_y_min = margin
    array_y_max = g(margin + (rows - 1) * pitch_y + oy + cell_h)

    # WL 라우팅 (Metal3 수직)
    for col in range(cols):
        wl_x = g(margin + col * pitch_x + ox + VWL_X)
        wl_y_bot = g(array_y_min - 1.5)
        wl_y_top = g(array_y_max + 1.5)
        c.add_polygon(
            [(wl_x - wl_w/2, wl_y_bot), (wl_x + wl_w/2, wl_y_bot),
             (wl_x + wl_w/2, wl_y_top), (wl_x - wl_w/2, wl_y_top)],
            layer=LAYER["met3"]
        )
        # Via2 배치
        for row in range(rows):
            via_x = g(margin + col * pitch_x + ox + VWL_X)
            via_y = g(margin + row * pitch_y + oy + VWL_VIA_Y)
            v2 = c.add_ref(via_m2_m3())
            v2.dmove((via_x, via_y))

    # BL 라우팅 (Metal3 수직)
    for col in range(cols):
        bl_x = g(margin + col * pitch_x + ox + VBL_X)
        bl_y_bot = g(array_y_min - 1.5)
        bl_y_top = g(array_y_max + 1.5)
        c.add_polygon(
            [(bl_x - bl_w/2, bl_y_bot), (bl_x + bl_w/2, bl_y_bot),
             (bl_x + bl_w/2, bl_y_top), (bl_x - bl_w/2, bl_y_top)],
            layer=LAYER["met3"]
        )
        for row in range(rows):
            via_x = g(margin + col * pitch_x + ox + VBL_X)
            via_y = g(margin + row * pitch_y + oy + VBL_VIA_Y)
            v2 = c.add_ref(via_m2_m3())
            v2.dmove((via_x, via_y))

    # SL 라우팅 (Metal2 수평)
    for row in range(rows):
        sl_y = g(margin + row * pitch_y + oy + VS_Y)
        sl_x_left = g(array_x_min - 1.5)
        sl_x_right = g(array_x_max + 1.5)
        c.add_polygon(
            [(sl_x_left, sl_y - sl_w/2), (sl_x_right, sl_y - sl_w/2),
             (sl_x_right, sl_y + sl_w/2), (sl_x_left, sl_y + sl_w/2)],
            layer=LAYER["met2"]
        )
        for col in range(cols):
            via_x = g(margin + col * pitch_x + ox + VS_VIA_X)
            via_y = g(margin + row * pitch_y + oy + VS_Y)
            v1 = c.add_ref(via_m1_m2())
            v1.dmove((via_x, via_y))

    # GND 배선 (Metal1)
    gnd_y = g(array_y_min - 2.0)
    gnd_x_left = g(array_x_min - 1.0)
    gnd_x_right = g(array_x_max + 1.0)
    gnd_w = g(0.5)
    c.add_polygon(
        [(gnd_x_left, gnd_y - gnd_w/2), (gnd_x_right, gnd_y - gnd_w/2),
         (gnd_x_right, gnd_y + gnd_w/2), (gnd_x_left, gnd_y + gnd_w/2)],
        layer=LAYER["met1"]
    )

    # ========================================================================
    # 포트 라벨 추가 (Magic LVS 추출용)
    # ========================================================================
    print("Adding port labels...")

    # WL 라벨 (met3)
    for col in range(cols):
        wl_x = g(margin + col * pitch_x + ox + VWL_X)
        wl_y = g(array_y_min - 1.0)
        c.add_label(text=f"WL[{col}]", position=(wl_x, wl_y), layer=LAYER["met3_label"])

    # BL 라벨 (met3)
    for col in range(cols):
        bl_x = g(margin + col * pitch_x + ox + VBL_X)
        bl_y = g(array_y_min - 1.0)
        c.add_label(text=f"BL[{col}]", position=(bl_x, bl_y), layer=LAYER["met3_label"])

    # SL 라벨 (met2)
    for row in range(rows):
        sl_y = g(margin + row * pitch_y + oy + VS_Y)
        sl_x = g(array_x_max + 1.0)
        c.add_label(text=f"SL[{row}]", position=(sl_x, sl_y), layer=LAYER["met2_label"])

    # GND 라벨 (met1)
    c.add_label(text="GND", position=(gnd_x_left + 0.5, gnd_y), layer=LAYER["met1_label"])

    # ========================================================================
    # 시각적 텍스트 라벨 (사람이 읽기 위한 용도)
    # ========================================================================
    label_size = 0.4
    for col in range(cols):
        wl_x = g(margin + col * pitch_x + ox + VWL_X)
        lbl = c.add_ref(gf.components.text(f"WL{col}", size=label_size, layer=LAYER["text"]))
        lbl.dmove((g(wl_x - 0.3), g(array_y_max + 1.8)))

    for col in range(cols):
        bl_x = g(margin + col * pitch_x + ox + VBL_X)
        lbl = c.add_ref(gf.components.text(f"BL{col}", size=label_size, layer=LAYER["text"]))
        lbl.dmove((g(bl_x - 0.3), g(array_y_max + 2.4)))

    for row in range(rows):
        sl_y = g(margin + row * pitch_y + oy + VS_Y)
        lbl = c.add_ref(gf.components.text(f"SL{row}", size=label_size, layer=LAYER["text"]))
        lbl.dmove((g(array_x_max + 0.5), g(sl_y - 0.2)))

    return c


def main():
    print("=" * 60)
    print("RRAM Array GDS Generator (gdsfactory 9.x)")
    print("Using DRC-fixed 1T1R cell")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ROWS = 4
    COLS = 4

    array = create_rram_array(rows=ROWS, cols=COLS)

    out_path = OUTPUT_DIR / f"rram_{ROWS}x{COLS}_array_fixed.gds"
    array.write_gds(out_path)

    print(f"\nOutput: {out_path}")
    print("=" * 60)

    return array


if __name__ == "__main__":
    main()
