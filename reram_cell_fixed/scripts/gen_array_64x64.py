#!/usr/bin/env python3
"""
RRAM 64x64 Array GDS + LEF Generator
- gen_array_3x5_260222.py 기반 (실제 v2/v3에서 사용된 스크립트)
- ROWS=64, COLS=64로 변경
"""

import os
from pathlib import Path
from typing import List, Tuple, Dict

if "PDK" in os.environ:
    del os.environ["PDK"]

import gdsfactory as gf
from gdsfactory.component import Component

gf.gpdk.PDK.activate()

PROJECT_DIR = Path(__file__).parent.parent
CELL_1T1R_GDS = PROJECT_DIR / "gds" / "RRAM_1T1R_new_fixed.gds"
OUTPUT_DIR = PROJECT_DIR / "gds"

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
    "text": (83, 44),
}

GRID = 0.005
GRID_INV = 200

def g(v: float) -> float:
    return round(v * GRID_INV) / GRID_INV

VIA_SIZE = 0.15
VIA2_SIZE = 0.20
VIA_PAD = g(0.32)
VIA2_PAD = g(0.37)


def load_cell() -> Component:
    if not CELL_1T1R_GDS.exists():
        raise FileNotFoundError(f"1T1R 셀을 찾을 수 없습니다: {CELL_1T1R_GDS}")
    cell = gf.import_gds(CELL_1T1R_GDS)
    return cell


@gf.cell
def via_m1_m2() -> Component:
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


class ArrayInfo:
    def __init__(self):
        self.width = 0.0
        self.height = 0.0
        self.wl_pins: List[Tuple[str, float, float, float, float]] = []
        self.bl_pins: List[Tuple[str, float, float, float, float]] = []
        self.sl_pins: List[Tuple[str, float, float, float, float]] = []
        self.gnd_pin: Tuple[str, float, float, float, float] = None
        self.obs_rects: Dict[str, List[Tuple[float, float, float, float]]] = {
            "li1": [], "met1": [], "met2": [], "met3": []
        }


def create_rram_array(rows: int = 64, cols: int = 64) -> Tuple[Component, ArrayInfo]:
    c = Component()
    info = ArrayInfo()

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

    # Body(GND) 단자 위치
    BODY_X1 = 0.180
    BODY_X2 = 1.210
    BODY_CX = g((BODY_X1 + BODY_X2) / 2)

    # 레이아웃 파라미터
    pitch_x = g(4.0)
    pitch_y = g(5.5)
    margin = g(3.0)
    wl_w = g(0.36)
    bl_w = g(0.32)
    sl_w = g(0.32)

    print(f"Cell: {CELL_1T1R_GDS.name}")
    print(f"Cell size: {cell_w:.3f} x {cell_h:.3f} um")
    print(f"Generating {rows}x{cols} array ({rows*cols} cells)...")

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
    print("Routing WL (Metal3)...")
    for col in range(cols):
        wl_x = g(margin + col * pitch_x + ox + VWL_X)
        wl_y_bot = g(array_y_min - 1.5)
        wl_y_top = g(array_y_max + 1.5)
        c.add_polygon(
            [(wl_x - wl_w/2, wl_y_bot), (wl_x + wl_w/2, wl_y_bot),
             (wl_x + wl_w/2, wl_y_top), (wl_x - wl_w/2, wl_y_top)],
            layer=LAYER["met3"]
        )
        info.wl_pins.append((
            f"WL[{col}]",
            g(wl_x - wl_w/2), g(wl_y_bot),
            g(wl_x + wl_w/2), g(wl_y_bot + 0.5)
        ))
        for row in range(rows):
            via_x = g(margin + col * pitch_x + ox + VWL_X)
            via_y = g(margin + row * pitch_y + oy + VWL_VIA_Y)
            v2 = c.add_ref(via_m2_m3())
            v2.dmove((via_x, via_y))

    # BL 라우팅 (Metal3 수직)
    print("Routing BL (Metal3)...")
    for col in range(cols):
        bl_x = g(margin + col * pitch_x + ox + VBL_X)
        bl_y_bot = g(array_y_min - 1.5)
        bl_y_top = g(array_y_max + 1.5)
        c.add_polygon(
            [(bl_x - bl_w/2, bl_y_bot), (bl_x + bl_w/2, bl_y_bot),
             (bl_x + bl_w/2, bl_y_top), (bl_x - bl_w/2, bl_y_top)],
            layer=LAYER["met3"]
        )
        info.bl_pins.append((
            f"BL[{col}]",
            g(bl_x - bl_w/2), g(bl_y_bot),
            g(bl_x + bl_w/2), g(bl_y_bot + 0.5)
        ))
        for row in range(rows):
            via_x = g(margin + col * pitch_x + ox + VBL_X)
            via_y = g(margin + row * pitch_y + oy + VBL_VIA_Y)
            v2 = c.add_ref(via_m2_m3())
            v2.dmove((via_x, via_y))

    # SL 라우팅 (Metal2 수평)
    print("Routing SL (Metal2)...")
    for row in range(rows):
        sl_y = g(margin + row * pitch_y + oy + VS_Y)
        sl_x_left = g(array_x_min - 1.5)
        sl_x_right = g(array_x_max + 1.5)
        c.add_polygon(
            [(sl_x_left, sl_y - sl_w/2), (sl_x_right, sl_y - sl_w/2),
             (sl_x_right, sl_y + sl_w/2), (sl_x_left, sl_y + sl_w/2)],
            layer=LAYER["met2"]
        )
        info.sl_pins.append((
            f"SL[{row}]",
            g(sl_x_right - 0.5), g(sl_y - sl_w/2),
            g(sl_x_right), g(sl_y + sl_w/2)
        ))
        for col in range(cols):
            via_x = g(margin + col * pitch_x + ox + VS_VIA_X)
            via_y = g(margin + row * pitch_y + oy + VS_Y)
            v1 = c.add_ref(via_m1_m2())
            v1.dmove((via_x, via_y))

    # GND 배선 (Metal1) — per-row GND bar + body stub + 좌측 vertical bar
    print("Routing GND (Metal1)...")
    gnd_w = g(0.50)
    gnd_spacing = g(0.20)
    stub_w = g(0.50)

    gnd_x_left = g(array_x_min - 1.5)
    gnd_x_right = g(array_x_max + 1.5)
    gnd_bar_centers = []

    for row in range(rows):
        cell_bottom = g(margin + row * pitch_y)
        gnd_cy = g(cell_bottom - gnd_spacing - gnd_w / 2)
        gnd_bar_centers.append(gnd_cy)

        # (1) 수평 GND bar
        c.add_polygon(
            [(gnd_x_left, g(gnd_cy - gnd_w/2)), (gnd_x_right, g(gnd_cy - gnd_w/2)),
             (gnd_x_right, g(gnd_cy + gnd_w/2)), (gnd_x_left, g(gnd_cy + gnd_w/2))],
            layer=LAYER["met1"]
        )

        # (2) 각 셀의 body → GND bar 수직 stub
        for col in range(cols):
            stub_cx = g(margin + col * pitch_x + ox + BODY_CX)
            stub_y_top = g(cell_bottom + 0.10)
            stub_y_bot = g(gnd_cy - gnd_w/2 + 0.05)
            c.add_polygon(
                [(g(stub_cx - stub_w/2), stub_y_bot),
                 (g(stub_cx + stub_w/2), stub_y_bot),
                 (g(stub_cx + stub_w/2), stub_y_top),
                 (g(stub_cx - stub_w/2), stub_y_top)],
                layer=LAYER["met1"]
            )

    # (3) 좌측 vertical bar — 모든 GND bar 연결
    vert_w = gnd_w
    vert_x_left = gnd_x_left
    vert_x_right = g(gnd_x_left + vert_w)
    vert_y_bot = g(gnd_bar_centers[0] - gnd_w / 2)
    vert_y_top = g(gnd_bar_centers[-1] + gnd_w / 2)
    c.add_polygon(
        [(vert_x_left, vert_y_bot), (vert_x_right, vert_y_bot),
         (vert_x_right, vert_y_top), (vert_x_left, vert_y_top)],
        layer=LAYER["met1"]
    )

    info.gnd_pin = (
        "GND",
        g(vert_x_left), g(vert_y_bot),
        g(vert_x_right), g(vert_y_bot + 0.5)
    )

    # 포트 라벨 (Magic LVS 추출용)
    print("Adding port labels...")
    for col in range(cols):
        wl_x = g(margin + col * pitch_x + ox + VWL_X)
        wl_y = g(array_y_min - 1.0)
        c.add_label(text=f"WL[{col}]", position=(wl_x, wl_y), layer=LAYER["met3_label"])

    for col in range(cols):
        bl_x = g(margin + col * pitch_x + ox + VBL_X)
        bl_y = g(array_y_min - 1.0)
        c.add_label(text=f"BL[{col}]", position=(bl_x, bl_y), layer=LAYER["met3_label"])

    for row in range(rows):
        sl_y = g(margin + row * pitch_y + oy + VS_Y)
        sl_x = g(array_x_max + 1.0)
        c.add_label(text=f"SL[{row}]", position=(sl_x, sl_y), layer=LAYER["met2_label"])

    c.add_label(text="GND", position=(g(vert_x_left + vert_w/2), g(vert_y_bot + 0.25)), layer=LAYER["met1_label"])

    # 시각적 텍스트 라벨 (64x64는 너무 많으므로 코너만)
    label_size = 0.4
    for col in [0, cols-1]:
        wl_x = g(margin + col * pitch_x + ox + VWL_X)
        lbl = c.add_ref(gf.components.text(f"WL{col}", size=label_size, layer=LAYER["text"]))
        lbl.dmove((g(wl_x - 0.3), g(array_y_max + 1.8)))
    for col in [0, cols-1]:
        bl_x = g(margin + col * pitch_x + ox + VBL_X)
        lbl = c.add_ref(gf.components.text(f"BL{col}", size=label_size, layer=LAYER["text"]))
        lbl.dmove((g(bl_x - 0.3), g(array_y_max + 2.4)))
    for row in [0, rows-1]:
        sl_y = g(margin + row * pitch_y + oy + VS_Y)
        lbl = c.add_ref(gf.components.text(f"SL{row}", size=label_size, layer=LAYER["text"]))
        lbl.dmove((g(array_x_max + 0.5), g(sl_y - 0.2)))

    # LEF 정보 수집
    final_bbox = c.dbbox()
    info.width = g(final_bbox.right - final_bbox.left + 1.0)
    info.height = g(final_bbox.top - final_bbox.bottom + 1.0)

    obs_margin = 0.5
    obs_x1 = g(final_bbox.left - obs_margin)
    obs_y1 = g(final_bbox.bottom - obs_margin)
    obs_x2 = g(final_bbox.right + obs_margin)
    obs_y2 = g(final_bbox.top + obs_margin)

    info.obs_rects["li1"].append((obs_x1, obs_y1, obs_x2, obs_y2))
    info.obs_rects["met1"].append((obs_x1, obs_y1, obs_x2, obs_y2))
    info.obs_rects["met2"].append((obs_x1, obs_y1, obs_x2, obs_y2))
    info.obs_rects["met3"].append((obs_x1, obs_y1, obs_x2, obs_y2))

    return c, info


def generate_lef(macro_name: str, info: ArrayInfo, output_path: Path) -> None:
    lines = []
    lines.append("VERSION 5.7 ;")
    lines.append("BUSBITCHARS \"[]\" ;")
    lines.append("DIVIDERCHAR \"/\" ;")
    lines.append("")

    lines.append(f"MACRO {macro_name}")
    lines.append("  CLASS BLOCK ;")
    lines.append("  FOREIGN {0} 0 0 ;".format(macro_name))
    lines.append(f"  ORIGIN 0 0 ;")
    lines.append(f"  SIZE {info.width:.3f} BY {info.height:.3f} ;")
    lines.append("  SYMMETRY X Y ;")
    lines.append("")

    for pin_name, x1, y1, x2, y2 in info.wl_pins:
        lines.append(f"  PIN {pin_name}")
        lines.append("    DIRECTION INOUT ;")
        lines.append("    USE SIGNAL ;")
        lines.append("    PORT")
        lines.append("      LAYER met3 ;")
        lines.append(f"        RECT {x1:.3f} {y1:.3f} {x2:.3f} {y2:.3f} ;")
        lines.append("    END")
        lines.append(f"  END {pin_name}")
        lines.append("")

    for pin_name, x1, y1, x2, y2 in info.bl_pins:
        lines.append(f"  PIN {pin_name}")
        lines.append("    DIRECTION INOUT ;")
        lines.append("    USE SIGNAL ;")
        lines.append("    PORT")
        lines.append("      LAYER met3 ;")
        lines.append(f"        RECT {x1:.3f} {y1:.3f} {x2:.3f} {y2:.3f} ;")
        lines.append("    END")
        lines.append(f"  END {pin_name}")
        lines.append("")

    for pin_name, x1, y1, x2, y2 in info.sl_pins:
        lines.append(f"  PIN {pin_name}")
        lines.append("    DIRECTION INOUT ;")
        lines.append("    USE SIGNAL ;")
        lines.append("    PORT")
        lines.append("      LAYER met2 ;")
        lines.append(f"        RECT {x1:.3f} {y1:.3f} {x2:.3f} {y2:.3f} ;")
        lines.append("    END")
        lines.append(f"  END {pin_name}")
        lines.append("")

    if info.gnd_pin:
        pin_name, x1, y1, x2, y2 = info.gnd_pin
        lines.append(f"  PIN {pin_name}")
        lines.append("    DIRECTION INOUT ;")
        lines.append("    USE GROUND ;")
        lines.append("    PORT")
        lines.append("      LAYER met1 ;")
        lines.append(f"        RECT {x1:.3f} {y1:.3f} {x2:.3f} {y2:.3f} ;")
        lines.append("    END")
        lines.append(f"  END {pin_name}")
        lines.append("")

    lines.append("  OBS")
    for layer_name, rects in info.obs_rects.items():
        for x1, y1, x2, y2 in rects:
            lines.append(f"    LAYER {layer_name} ;")
            lines.append(f"      RECT {x1:.3f} {y1:.3f} {x2:.3f} {y2:.3f} ;")
    lines.append("  END")
    lines.append("")

    lines.append(f"END {macro_name}")
    lines.append("")
    lines.append("END LIBRARY")

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"LEF saved: {output_path}")


def main():
    print("=" * 60)
    print("RRAM 64x64 Array GDS + LEF Generator")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ROWS = 64
    COLS = 64
    MACRO_NAME = "rram_array_64x64"

    array, info = create_rram_array(rows=ROWS, cols=COLS)

    gds_path = OUTPUT_DIR / f"{MACRO_NAME}.gds"
    array.write_gds(gds_path)
    print(f"GDS saved: {gds_path}")

    lef_path = OUTPUT_DIR / f"{MACRO_NAME}.lef"
    generate_lef(MACRO_NAME, info, lef_path)

    print("")
    print(f"Array: {ROWS} rows x {COLS} cols = {ROWS*COLS} RRAM cells")
    print(f"Size: {info.width:.3f} x {info.height:.3f} um")
    print(f"Pins: WL[0:{COLS-1}], BL[0:{COLS-1}], SL[0:{ROWS-1}], GND")
    print(f"Total pins: {COLS} WL + {COLS} BL + {ROWS} SL + 1 GND = {COLS*2 + ROWS + 1}")
    print("=" * 60)


if __name__ == "__main__":
    main()
