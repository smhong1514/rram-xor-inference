#!/usr/bin/env python3
"""
================================================================================
fix_lef_for_openlane.py — RRAM LEF를 OpenLane 통합용으로 수정
================================================================================

기존 RRAM array LEF 파일에 다음 수정을 적용합니다:
  1. nwell OBS 추가 (standard cell nwell 단절 방지 → LVS VPB 에러 해결)
  2. met1 OBS 분리 (GND PIN 접근 영역 확보)
  3. met2 OBS 조정 (SL PIN 접근 영역 확보)
  4. met3 OBS 조정 (WL/BL PIN 접근 영역 확보)

[사용법]
  python fix_lef_for_openlane.py input.lef [output.lef]

  output.lef 생략 시 input 파일명에 _openlane 접미사 추가
  예: rram_array_3x5_260222.lef → rram_array_3x5_260222_openlane.lef

[배경]
  - RRAM 매크로에 nwell OBS가 없으면 standard cell nwell이 단절되어
    filler 셀의 VPB가 고립 → LVS에서 VPB 에러 발생
  - WL Driver/SA/BL_WD에는 nwell OBS를 추가하면 안 됨!
    (HV nwell과 인접 → nwell.8 DRC 위반)
  - 이 스크립트는 RRAM array LEF 전용

================================================================================
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# PIN 접근을 위한 margin (um)
PIN_ACCESS_MARGIN = 1.0


def parse_lef(lef_path: str) -> dict:
    """LEF 파일을 파싱하여 구조화된 데이터 반환"""
    with open(lef_path, 'r') as f:
        content = f.read()

    data = {}

    # MACRO 이름
    m = re.search(r'MACRO\s+(\S+)', content)
    data['macro_name'] = m.group(1) if m else 'unknown'

    # SIZE
    m = re.search(r'SIZE\s+([\d.]+)\s+BY\s+([\d.]+)', content)
    data['width'] = float(m.group(1))
    data['height'] = float(m.group(2))

    # PIN 정보 수집
    pins = []
    pin_pattern = re.compile(
        r'PIN\s+(\S+)\s*\n'
        r'.*?DIRECTION\s+(\S+)\s*;'
        r'.*?USE\s+(\S+)\s*;'
        r'.*?LAYER\s+(\S+)\s*;'
        r'.*?RECT\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)',
        re.DOTALL
    )
    for pm in pin_pattern.finditer(content):
        pins.append({
            'name': pm.group(1),
            'direction': pm.group(2),
            'use': pm.group(3),
            'layer': pm.group(4),
            'x1': float(pm.group(5)),
            'y1': float(pm.group(6)),
            'x2': float(pm.group(7)),
            'y2': float(pm.group(8)),
        })
    data['pins'] = pins

    # 원본 내용 (OBS 이전까지)
    data['content'] = content

    return data


def find_pin_edges(pins: List[dict], width: float, height: float) -> dict:
    """PIN 위치를 분석하여 어느 edge에 있는지 파악"""
    edges = {
        'bottom': [],  # y1 < height * 0.2
        'top': [],     # y2 > height * 0.8
        'left': [],    # x1 < width * 0.2
        'right': [],   # x2 > width * 0.8
    }
    for pin in pins:
        cy = (pin['y1'] + pin['y2']) / 2
        cx = (pin['x1'] + pin['x2']) / 2
        if cy < height * 0.2:
            edges['bottom'].append(pin)
        elif cy > height * 0.8:
            edges['top'].append(pin)
        if cx < width * 0.2:
            edges['left'].append(pin)
        elif cx > width * 0.8:
            edges['right'].append(pin)
    return edges


def generate_obs(data: dict) -> str:
    """OpenLane 통합용 OBS 생성"""
    w = data['width']
    h = data['height']
    pins = data['pins']
    edges = find_pin_edges(pins, w, h)

    lines = []
    lines.append("  OBS")

    # (1) nwell OBS — 전체 매크로 커버 (핵심!)
    lines.append(f"    LAYER nwell ;")
    lines.append(f"      RECT 0.000 0.000 {w:.3f} {h:.3f} ;")

    # (2) li1 OBS — 약간 inset
    inset = 0.5
    lines.append(f"    LAYER li1 ;")
    lines.append(f"      RECT {inset:.3f} {inset:.3f} {w - inset:.3f} {h - inset:.3f} ;")

    # (3) met1 OBS — GND PIN 영역 제외
    gnd_pins = [p for p in pins if p['layer'] == 'met1']
    if gnd_pins:
        # GND pin은 보통 좌측에 위치
        gnd = gnd_pins[0]
        # GND pin의 접근 영역 계산
        gnd_access_x = gnd['x2'] + PIN_ACCESS_MARGIN
        gnd_access_y = gnd['y2'] + PIN_ACCESS_MARGIN

        # met1 OBS를 2개 RECT로 분리 (GND 접근 영역 제외)
        # RECT 1: GND 접근 영역 오른쪽 전체
        lines.append(f"    LAYER met1 ;")
        lines.append(f"      RECT {gnd_access_x:.3f} 0.000 {w - inset:.3f} {h - inset:.3f} ;")
        # RECT 2: GND 접근 영역 위쪽 (같은 x 범위)
        lines.append(f"    LAYER met1 ;")
        lines.append(f"      RECT 0.000 {gnd_access_y:.3f} {gnd_access_x:.3f} {h - inset:.3f} ;")
    else:
        lines.append(f"    LAYER met1 ;")
        lines.append(f"      RECT {inset:.3f} {inset:.3f} {w - inset:.3f} {h - inset:.3f} ;")

    # (4) met2 OBS — SL PIN 접근 영역 제외 (우측)
    sl_pins = [p for p in pins if p['layer'] == 'met2']
    if sl_pins:
        # SL pin 중 가장 왼쪽 x1 기준
        sl_x_min = min(p['x1'] for p in sl_pins)
        met2_x_right = sl_x_min - PIN_ACCESS_MARGIN
        lines.append(f"    LAYER met2 ;")
        lines.append(f"      RECT 0.000 {inset:.3f} {met2_x_right:.3f} {h - inset:.3f} ;")
    else:
        lines.append(f"    LAYER met2 ;")
        lines.append(f"      RECT {inset:.3f} {inset:.3f} {w - inset:.3f} {h - inset:.3f} ;")

    # (5) met3 OBS — WL/BL PIN 접근 영역 제외 (하단)
    met3_pins = [p for p in pins if p['layer'] == 'met3']
    if met3_pins:
        # WL/BL pin 중 가장 높은 y2 기준
        met3_y_max = max(p['y2'] for p in met3_pins)
        met3_y_start = met3_y_max + PIN_ACCESS_MARGIN
        lines.append(f"    LAYER met3 ;")
        lines.append(f"      RECT 0.000 {met3_y_start:.3f} {w:.3f} {h - inset:.3f} ;")
    else:
        lines.append(f"    LAYER met3 ;")
        lines.append(f"      RECT {inset:.3f} {inset:.3f} {w - inset:.3f} {h - inset:.3f} ;")

    lines.append("  END")
    return '\n'.join(lines)


def fix_lef(input_path: str, output_path: str) -> None:
    """LEF 파일의 OBS를 OpenLane 통합용으로 수정"""
    data = parse_lef(input_path)
    content = data['content']

    print(f"MACRO: {data['macro_name']}")
    print(f"SIZE: {data['width']:.3f} x {data['height']:.3f}")
    print(f"PINs: {len(data['pins'])}")
    for p in data['pins']:
        print(f"  {p['name']:10s} {p['layer']:5s} "
              f"({p['x1']:.3f}, {p['y1']:.3f}) - ({p['x2']:.3f}, {p['y2']:.3f})  "
              f"USE {p['use']}")

    # 기존 OBS 제거
    obs_start = content.find('  OBS\n')
    obs_end = content.find('  END\n', obs_start)
    if obs_start == -1 or obs_end == -1:
        print("ERROR: OBS 섹션을 찾을 수 없습니다")
        return

    # 새 OBS 생성
    new_obs = generate_obs(data)

    # OBS 교체
    new_content = content[:obs_start] + new_obs + '\n' + content[obs_end + len('  END\n'):]

    # 저장
    with open(output_path, 'w') as f:
        f.write(new_content)

    print(f"\n출력: {output_path}")
    print("\nOBS 변경 사항:")
    print("  + nwell OBS (전체 매크로 커버)")
    print("  ~ met1 OBS 분리 (GND PIN 접근 영역 확보)")
    print("  ~ met2 OBS 조정 (SL PIN 접근 영역 확보)")
    print("  ~ met3 OBS 조정 (WL/BL PIN 접근 영역 확보)")


def main():
    if len(sys.argv) < 2:
        print("사용법: python fix_lef_for_openlane.py input.lef [output.lef]")
        print("  output.lef 생략 시 _openlane 접미사 추가")
        sys.exit(1)

    input_path = sys.argv[1]
    if not Path(input_path).exists():
        print(f"ERROR: 파일을 찾을 수 없습니다: {input_path}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        p = Path(input_path)
        output_path = str(p.parent / f"{p.stem}_openlane{p.suffix}")

    print("=" * 60)
    print("RRAM LEF → OpenLane Fix (nwell OBS + PIN access)")
    print("=" * 60)

    fix_lef(input_path, output_path)

    print("=" * 60)


if __name__ == "__main__":
    main()
