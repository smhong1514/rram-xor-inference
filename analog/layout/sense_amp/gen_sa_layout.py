#!/usr/bin/env python3
"""Sense Amplifier 레이아웃 생성기 (Python → Magic TCL).

이 스크립트는 sky130B DRC 룰에 따라 좌표를 계산하고, Magic TCL 스크립트를 출력한다.
실행 방법:
  1) python3 gen_sa_layout.py        → sense_amp_gen.tcl 생성
  2) magic -noconsole -dnull < sense_amp_gen.tcl  → .mag/.gds/.spice 생성

회로: 10T StrongARM Latch SA (전부 sky130 1.8V, SPICE 핀순서: D,G,S,B)
  Row3 PMOS W=0.5: MP3(Q,SAE,VDD,VDD)    MP5(QB,SAE,Q,VDD)    MP4(QB,SAE,VDD,VDD)
  Row2 PMOS W=1.0: MP1(Q,QB,VDD,VDD)                           MP2(QB,Q,VDD,VDD)
  Row1 NMOS W=1.0: MN1(Q,QB,FN1,VSS)                           MN2(QB,Q,FN2,VSS)
  Row0 NMOS W=2.0: MN3(FN1,INP,TAIL,VSS)  MN0(TAIL,SAE,VSS,VSS)  MN4(FN2,INN,TAIL,VSS)

레이아웃 구조: 3컬럼 좌우대칭 (Col0=Q측 | Col1=중앙 | Col2=QB측)

배선 전략 (v3c, 모든 충돌 해결):
  met1: S/D 패드, poly contact 패드, 전원 레일 스터브, cross-coupling 수평선
  met2: Q/QB 수직 spine, SAE 수직, TAIL 수평, FN1/FN2 L자형
  poly: MN1-MP1/MN2-MP2 gate가 Gap1을 관통하여 연속 (별도 연결 불필요)

Cross-coupling (래치 되먹임):
  Q→MN2.G: Q spine(met2) → stub → via1 → met1 수평(Gap0 upper) → MN2.G pad
  QB→MP1.G: QB spine(met2) → stub → via1 → met1 수평(Gap1 lower) → MP1.G pad

FN1/FN2: met2 L자형 (drain x에서 수평 → source x에서 수직)
"""
import os

# ======================================================================
# DRC 상수 (lambda 단위, 1λ = 0.01µm = 10nm, sky130B.tech 기준)
# ======================================================================
# 트랜지스터 기본 치수
GL = 15             # gate 길이 (poly width over diff)
SD = 27             # source/drain 영역 폭 (gate 양쪽)
DW = SD + GL + SD   # 디바이스 전체 폭 = 69λ
# 컨택트
CT = 17             # licon/mcon 크기 (정사각형)
CT_PITCH = 36       # 컨택트 피치 (17 + 19 spacing)
# Poly
POLY_EXT = 13       # poly가 diff 바깥으로 연장되는 거리
POLY_SPACE = 21     # poly 간 최소 간격
POLY_ENC_CT_1 = 8   # poly가 polycont를 감싸는 거리
# Diffusion / 컨택트 간격
DIFF_ENC_CT = 4     # diff가 licon을 감싸는 거리 (source 쪽)
GATE_CT_SPACE = 6   # gate에서 drain licon까지 거리 (licon.11)
# Local Interconnect (li1)
LI_ENC_CT = 8       # li1이 licon을 감싸는 거리
LI_MIN_AREA = 561   # li1 최소 면적
LI_SPACE = 17       # li1 최소 간격
# Metal 1
M1_WIDTH = 14; M1_SPACE = 14; M1_MIN_AREA = 830
M1_ENC_MCON = 5     # met1이 mcon을 감싸는 거리 (기본)
M1_ENC_MCON_1 = 6   # met1이 mcon을 감싸는 거리 (한 방향)
# Nwell
NW_ENC = 18         # nwell이 p-diff를 감싸는 거리
# Diff/Tap 간격
DIFF_SPACE = 27; TAP_SPACE = 27; TAP_ENC_LICON = 12
# Via1 (met1↔met2)
VIA_SIZE = 15       # via1 기본 크기
M1_ENC_VIA = 6; M1_ENC_VIA_MIN = 6   # met1이 via1을 감싸는 거리
# Metal 2
M2_WIDTH = 14; M2_SPACE = 14; M2_MIN_AREA = 676; M2_ENC_VIA = 6
# Poly contact에서 diff까지 간격 (licon.9 + psdm.5a)
POLYCONT_DIFF_SPACE = 24
# Via1 paint 크기 (26x26, via.1a 기반) 및 방향성 surround
VIA1_MIN_W = 26; VIA1_SURR = 3

# 디바이스 폭 (lambda)
W050 = 50; W100 = 100; W200 = 200
# 레이아웃 마진 및 간격
MARGIN = 15         # 셀 가장자리 마진
COL_SP = 60         # 컬럼 간 간격
RAIL_H = 48         # 전원 레일 높이
TAP_H = CT + 2*TAP_ENC_LICON  # 41λ = tap 높이

# ======================================================================
# 수직 좌표 계산 (아래→위 순서로 적층)
# ======================================================================
# 전체 구조 (아래→위):
#   VSS 레일 → ptap → Row0(NMOS W=2) → Gap0 → Row1(NMOS W=1) → Gap1
#   → Row2(PMOS W=1) → Gap2 → Row3(PMOS W=0.5) → ntap → VDD 레일
y = 0
Y_VSS_B = y; y += RAIL_H; Y_VSS_T = y; y += 12     # VSS 전원 레일
Y_PTAP_B = y; y += TAP_H; Y_PTAP_T = y; y += TAP_SPACE  # p-substrate tap (VSS 연결)
Y_R0N_B = y; y += W200; Y_R0N_T = y                 # Row0: MN3, MN0, MN4 (입력쌍+꼬리)
GAP01 = 130  # Row 사이 gap (poly contact + 배선용 공간)
Y_GAP0_B = y; y += GAP01; Y_GAP0_T = y              # Gap0: FN1/FN2 배선, INP/INN/SAE gate contact
Y_R1N_B = y; y += W100; Y_R1N_T = y                 # Row1: MN1, MN2 (래치 NMOS)
GAP12 = 130
Y_GAP1_B = y; y += GAP12; Y_GAP1_T = y              # Gap1: cross-coupling gate contact
Y_R2P_B = y; y += W100; Y_R2P_T = y                 # Row2: MP1, MP2 (래치 PMOS)
GAP23 = 130
Y_GAP2_B = y; y += GAP23; Y_GAP2_T = y              # Gap2: SAE gate contact
Y_R3P_B = y; y += W050; Y_R3P_T = y; y += TAP_SPACE # Row3: MP3, MP5, MP4 (precharge/equalize)
Y_NTAP_B = y; y += TAP_H; Y_NTAP_T = y; y += 12    # n-well tap (VDD 연결)
Y_VDD_B = y; y += RAIL_H; Y_VDD_T = y               # VDD 전원 레일

# Poly contact 트랙 좌표
# 각 Gap에 상하 2개 트랙: LO(아래쪽, diff에서 24λ 떨어짐), HI(위쪽)
# 이 트랙에 poly contact(polycont)를 배치하여 gate 신호를 metal로 올림
Y_G0_LO_B = Y_GAP0_B + POLYCONT_DIFF_SPACE; Y_G0_LO_T = Y_G0_LO_B + CT  # Gap0 하단 트랙
Y_G0_HI_T = Y_GAP0_T - POLYCONT_DIFF_SPACE; Y_G0_HI_B = Y_G0_HI_T - CT  # Gap0 상단 트랙
Y_G1_LO_B = Y_GAP1_B + POLYCONT_DIFF_SPACE; Y_G1_LO_T = Y_G1_LO_B + CT  # Gap1 하단 트랙
Y_G1_HI_T = Y_GAP1_T - POLYCONT_DIFF_SPACE; Y_G1_HI_B = Y_G1_HI_T - CT  # Gap1 상단 트랙
Y_G2_LO_B = Y_GAP2_B + POLYCONT_DIFF_SPACE; Y_G2_LO_T = Y_G2_LO_B + CT  # Gap2 하단 트랙
Y_G2_HI_T = Y_GAP2_T - POLYCONT_DIFF_SPACE; Y_G2_HI_B = Y_G2_HI_T - CT  # Gap2 상단 트랙
# SAE 전용 트랙: MN1-MP1/MN2-MP2 연속 gate poly와 poly.2 간격 충돌 회피를 위해 위로 이동
# 제약: poly pad 하단 >= (Row2 PMOS 상단 + POLY_EXT) + POLY_SPACE = 801+21 = 822
# → SAE_track_y0 >= 822 + POLY_ENC_CT_1 = 830
Y_G2_SAE_B = 830; Y_G2_SAE_T = Y_G2_SAE_B + CT  # 830-847

for name, lo_t, hi_b in [("Gap0", Y_G0_LO_T, Y_G0_HI_B),
                          ("Gap1", Y_G1_LO_T, Y_G1_HI_B),
                          ("Gap2", Y_G2_LO_T, Y_G2_HI_B)]:
    lo_pad = lo_t + POLY_ENC_CT_1; hi_pad = hi_b - POLY_ENC_CT_1
    assert hi_pad - lo_pad >= POLY_SPACE, f"{name} poly spacing {hi_pad-lo_pad} < {POLY_SPACE}"

# SAE custom track poly spacing checks
sae_pad_bot = Y_G2_SAE_B - POLY_ENC_CT_1  # 822
sae_pad_top = Y_G2_SAE_T + POLY_ENC_CT_1  # 855
mp_poly_top = Y_R2P_T + POLY_EXT  # 801 (MN1-MP1/MN2-MP2 continuous gate poly top)
r3_poly_bot = Y_R3P_B - POLY_EXT  # 905 (MP3/MP5/MP4 device poly bottom)
assert sae_pad_bot - mp_poly_top >= POLY_SPACE, \
    f"SAE-below poly gap {sae_pad_bot - mp_poly_top} < {POLY_SPACE}"
assert r3_poly_bot - sae_pad_top >= POLY_SPACE, \
    f"SAE-above poly gap {r3_poly_bot - sae_pad_top} < {POLY_SPACE}"

# 수평 좌표: 3개 컬럼 (Col0=좌, Col1=중앙, Col2=우)
col_x = []
x = MARGIN
for _ in range(3): col_x.append(x); x += DW + COL_SP
CELL_W = x - COL_SP + MARGIN  # 셀 전체 폭

# Nwell 영역: PMOS (Row2, Row3) + ntap을 감싸는 사각형
NW_X0 = col_x[0] - NW_ENC; NW_X1 = col_x[2] + DW + NW_ENC
NW_Y0 = Y_R2P_B - NW_ENC; NW_Y1 = Y_NTAP_T + NW_ENC

print(f"Cell: {CELL_W} x {Y_VDD_T} lambda = {CELL_W*0.01:.2f} x {Y_VDD_T*0.01:.2f} um")

# ======================================================================
# TCL 생성 헬퍼 함수
# ======================================================================
# T 리스트에 Magic TCL 명령어를 누적한 뒤, 마지막에 파일로 출력한다.
T = []
def emit(s): T.append(s)
def bp(x0, y0, x1, y1, layer):
    """box + paint: (x0,y0)-(x1,y1) 영역에 layer를 칠한다."""
    T.append(f"box {x0} {y0} {x1} {y1}"); T.append(f"paint {layer}")

def contacts_in_sd(cx0, cy0, sd_w, diff_h, is_drain=False):
    """S/D 영역 내에 licon 컨택트 배열 좌표를 계산한다.
    drain 쪽은 gate에서 6λ 떨어져야 하고(licon.11), source 쪽은 4λ."""
    c_x0 = cx0 + (GATE_CT_SPACE if is_drain else DIFF_ENC_CT)
    c_x1 = c_x0 + CT
    avail = diff_h - 2*6  # diff 상하 6λ 여유 (한 방향 enclosure)
    nc = max(1, (avail - CT)//CT_PITCH + 1)  # 컨택트 개수
    arr_h = (nc-1)*CT_PITCH + CT
    sy = cy0 + (diff_h - arr_h)//2  # 중앙 정렬
    return [(c_x0, sy+i*CT_PITCH, c_x1, sy+i*CT_PITCH+CT) for i in range(nc)]

def paint_contacts(cts, layer):
    """컨택트 배열을 주어진 레이어(ndiffc/pdiffc)로 칠한다."""
    for c in cts: bp(c[0], c[1], c[2], c[3], layer)

def paint_li1_strip_y(cts):
    """컨택트 위에 li1 (Local Interconnect) 스트립을 칠한다.
    y방향 enclosure(8λ)을 사용하여 x방향 li.3 간격 위반을 방지."""
    if not cts: return None
    x0, x1 = cts[0][0], cts[0][2]
    y0 = cts[0][1] - LI_ENC_CT; y1 = cts[-1][3] + LI_ENC_CT
    if (x1-x0)*(y1-y0) < LI_MIN_AREA:  # 최소 면적 보장
        nh = (LI_MIN_AREA + (x1-x0) - 1)//(x1-x0); e = nh - (y1-y0)
        y0 -= e//2; y1 += (e+1)//2
    bp(x0, y0, x1, y1, "locali"); return (x0, y0, x1, y1)

def paint_mcon(cts):
    """li1→met1 연결을 위한 mcon (viali) 컨택트를 칠한다."""
    for c in cts: bp(c[0], c[1], c[2], c[3], "viali")

def paint_via1(vx0, vy0):
    """met1↔met2 연결을 위한 via1을 칠한다.
    sky130B 방향성 surround: x방향 0, y방향 3λ 추가."""
    cx = vx0 + VIA_SIZE//2; cy = vy0 + VIA_SIZE//2
    v1x0 = cx - VIA1_MIN_W//2; v1y0 = cy - VIA1_MIN_W//2
    v1x1 = v1x0 + VIA1_MIN_W; v1y1 = v1y0 + VIA1_MIN_W
    bp(v1x0, v1y0, v1x1, v1y1, "via1")
    bp(v1x0, v1y0-VIA1_SURR, v1x1, v1y1+VIA1_SURR, "metal1")
    bp(v1x0, v1y0-VIA1_SURR, v1x1, v1y1+VIA1_SURR, "metal2")
    return (v1x0, v1y0, v1x1, v1y1)

def met1_on_contacts(cts):
    """mcon 컨택트 배열 위에 met1 패드를 칠한다. 최소 면적도 보장."""
    x0 = cts[0][0]-M1_ENC_MCON; x1 = cts[0][2]+M1_ENC_MCON
    y0 = cts[0][1]-M1_ENC_MCON_1; y1 = cts[-1][3]+M1_ENC_MCON_1
    if (x1-x0)*(y1-y0) < M1_MIN_AREA:
        nh = (M1_MIN_AREA + (x1-x0)-1)//(x1-x0); e = nh-(y1-y0)
        y0 -= e//2; y1 += (e+1)//2
    bp(x0, y0, x1, y1, "metal1"); return (x0, y0, x1, y1)

def ensure_m1_area(x0, y0, x1, y1):
    """met1 사각형이 최소 면적(830λ²)을 만족하도록 y방향으로 확장."""
    if (x1-x0)*(y1-y0) < M1_MIN_AREA:
        nh = (M1_MIN_AREA + (x1-x0)-1)//(x1-x0); e = nh-(y1-y0)
        y0 -= e//2; y1 += (e+1)//2
    return x0, y0, x1, y1

def ensure_m2_area(x0, y0, x1, y1):
    """met2 사각형이 최소 면적(676λ²)을 만족하도록 y방향으로 확장."""
    if (x1-x0)*(y1-y0) < M2_MIN_AREA:
        nh = (M2_MIN_AREA + (x1-x0)-1)//(x1-x0); e = nh-(y1-y0)
        y0 -= e//2; y1 += (e+1)//2
    return x0, y0, x1, y1

pad_w = CT + 2*POLY_ENC_CT_1  # 33λ = poly contact pad 폭

def add_gate_contact(dev_name, track_y0, track_y1, extend_dir):
    """디바이스의 gate poly에 polycont를 추가하고, 지정된 트랙(Gap 내)까지 poly를 연장.
    extend_dir='up': poly를 디바이스에서 위(트랙)로 연장
    extend_dir='down': poly를 디바이스에서 아래(트랙)로 연장
    li1 + mcon도 함께 생성하여 met1까지 연결."""
    d = DI[dev_name]
    gcx = d["gcx"]; gx0 = d["gx0"]; gx1 = d["gx1"]
    pcx0 = gcx - CT//2; pcx1 = pcx0 + CT
    px0 = gcx - pad_w//2; px1 = px0 + pad_w
    pad_y0 = track_y0 - POLY_ENC_CT_1; pad_y1 = track_y1 + POLY_ENC_CT_1
    if extend_dir == 'up':
        bp(gx0, d["yb"]-POLY_EXT, gx1, pad_y1, "poly")
    else:
        bp(gx0, pad_y0, gx1, d["yt"]+POLY_EXT, "poly")
    bp(px0, pad_y0, px1, pad_y1, "poly")       # poly contact pad
    bp(pcx0, track_y0, pcx1, track_y1, "polycont")  # polycont (poly→li1)
    li_y0 = track_y0; li_y1 = track_y1
    if (px1-px0)*(li_y1-li_y0) < LI_MIN_AREA:
        eh = (LI_MIN_AREA//(px1-px0)) - (li_y1-li_y0) + 2
        li_y0 -= eh//2; li_y1 += (eh+1)//2
    bp(px0, li_y0, px1, li_y1, "locali")        # li1 스트립
    bp(pcx0, track_y0, pcx1, track_y1, "viali")  # mcon (li1→met1)
    return pcx0, track_y0, pcx1, track_y1

def via1_on_m1(cts, at_top=True):
    """S/D 컨택트 위 met1 패드에 via1을 배치한다.
    at_top=True: met1 패드 상단에 배치, False: 하단에 배치."""
    m1 = met1_on_contacts(cts)
    vx = cts[0][0]
    vy = m1[3] - VIA_SIZE - M1_ENC_VIA_MIN if at_top else m1[1] + M1_ENC_VIA_MIN
    paint_via1(vx, vy)
    return vx, vy

# ======================================================================
# Header
# ======================================================================
emit("tech load $PDK_ROOT/sky130B/libs.tech/magic/sky130B.tech")
emit("drc style drc(full)")
emit("drc off")
emit("snap internal")
emit("cellname delete sense_amp")
emit("edit")

emit("\n# === NWELL ===")
bp(NW_X0, NW_Y0, NW_X1, NW_Y1, "nwell")

# ======================================================================
# 트랜지스터 정의 및 생성
# ======================================================================
# 각 디바이스의 컬럼, 타입(n/p), y좌표, 폭, 핀 이름을 정의
# 루프에서 diff + poly + S/D contacts + li1을 자동 생성
devices = {
    "MN3": {"col":0,"type":"n","yb":Y_R0N_B,"w":W200,"gate":"INP","src":"TAIL","drn":"FN1"},
    "MN0": {"col":1,"type":"n","yb":Y_R0N_B,"w":W200,"gate":"SAE","src":"VSS","drn":"TAIL"},
    "MN4": {"col":2,"type":"n","yb":Y_R0N_B,"w":W200,"gate":"INN","src":"TAIL","drn":"FN2"},
    "MN1": {"col":0,"type":"n","yb":Y_R1N_B,"w":W100,"gate":"QB","src":"FN1","drn":"Q"},
    "MN2": {"col":2,"type":"n","yb":Y_R1N_B,"w":W100,"gate":"Q","src":"FN2","drn":"QB"},
    "MP1": {"col":0,"type":"p","yb":Y_R2P_B,"w":W100,"gate":"QB","src":"VDD","drn":"Q"},
    "MP2": {"col":2,"type":"p","yb":Y_R2P_B,"w":W100,"gate":"Q","src":"VDD","drn":"QB"},
    "MP3": {"col":0,"type":"p","yb":Y_R3P_B,"w":W050,"gate":"SAE","src":"VDD","drn":"Q"},
    "MP5": {"col":1,"type":"p","yb":Y_R3P_B,"w":W050,"gate":"SAE","src":"Q","drn":"QB"},
    "MP4": {"col":2,"type":"p","yb":Y_R3P_B,"w":W050,"gate":"SAE","src":"VDD","drn":"QB"},
}

DI = {}
for dn, d in devices.items():
    ci = d["col"]; cx = col_x[ci]; yb = d["yb"]; w = d["w"]
    dtype = "pdiff" if d["type"]=="p" else "ndiff"
    ctype = "pdiffc" if d["type"]=="p" else "ndiffc"
    emit(f"\n# === {dn} ({dtype} W={w*0.01:.1f}) ===")
    bp(cx, yb, cx+DW, yb+w, dtype)
    gx0 = cx+SD; gx1 = gx0+GL
    bp(gx0, yb-POLY_EXT, gx1, yb+w+POLY_EXT, "poly")
    drn_x0 = cx+SD+GL
    sc = contacts_in_sd(cx, yb, SD, w, False)
    dc = contacts_in_sd(drn_x0, yb, SD, w, True)
    paint_contacts(sc, ctype); paint_contacts(dc, ctype)
    sl = paint_li1_strip_y(sc); dl = paint_li1_strip_y(dc)
    DI[dn] = {"cx":cx,"gx0":gx0,"gx1":gx1,"gcx":(gx0+gx1)//2,
              "yb":yb,"yt":yb+w,"w":w,"sc":sc,"dc":dc,"sl":sl,"dl":dl,"d":d}

# ======================================================================
# 연속 gate poly: MN1-MP1 / MN2-MP2 (cross-coupled 래치 쌍)
# ======================================================================
# MN1과 MP1 (Col0), MN2와 MP2 (Col2)는 같은 gate net (QB, Q)을 공유.
# 각 디바이스의 gate poly를 Gap1을 관통하여 연속 연결하면
# 별도의 metal 배선 없이 gate가 자동으로 연결된다.
emit("\n# === CONTINUOUS GATE POLY (MN1-MP1, MN2-MP2) ===")
for col_idx in [0, 2]:
    if col_idx == 0:
        dn_n, dn_p = "MN1", "MP1"   # Col0: QB gate
    else:
        dn_n, dn_p = "MN2", "MP2"   # Col2: Q gate
    gx0 = DI[dn_n]["gx0"]; gx1 = DI[dn_n]["gx1"]
    poly_top_n = DI[dn_n]["yt"] + POLY_EXT  # NMOS poly 상단
    poly_bot_p = DI[dn_p]["yb"] - POLY_EXT  # PMOS poly 하단
    if poly_bot_p > poly_top_n:  # Gap이 있으면 poly로 채움
        bp(gx0, poly_top_n, gx1, poly_bot_p, "poly")

# ======================================================================
# 기판 탭 (Substrate Taps)
# ======================================================================
# ptap: NMOS 영역 아래, VSS에 연결 (p-type substrate contact)
# ntap: PMOS 영역 위, VDD에 연결 (n-well contact)
# 각 컬럼마다 좌우 2개 licon 배치
emit("\n# === TAPS ===")
for ci in range(3):
    cx = col_x[ci]
    ly0 = Y_PTAP_B+TAP_ENC_LICON; ly1 = ly0+CT
    tx0 = cx+DIFF_ENC_CT; tx1 = tx0+CT
    tx2 = cx+DW-DIFF_ENC_CT-CT; tx3 = tx2+CT
    bp(tx0,ly0,tx1,ly1,"ptapc"); bp(tx2,ly0,tx3,ly1,"ptapc")
    bp(cx,Y_PTAP_B,cx+DW,Y_PTAP_T,"ptap")
    bp(tx0,ly0-LI_ENC_CT,tx3,ly1+LI_ENC_CT,"locali")
    ny0 = Y_NTAP_B+TAP_ENC_LICON; ny1 = ny0+CT
    bp(tx0,ny0,tx1,ny1,"ntapc"); bp(tx2,ny0,tx3,ny1,"ntapc")
    bp(cx,Y_NTAP_B,cx+DW,Y_NTAP_T,"ntap")
    bp(tx0,ny0-LI_ENC_CT,tx3,ny1+LI_ENC_CT,"locali")

# ======================================================================
# 전원 레일 (met1, 셀 전체 폭으로 수평 배치)
# ======================================================================
emit("\n# === POWER RAILS ===")
bp(0, Y_VSS_B, CELL_W, Y_VSS_T, "metal1")  # VSS (하단)
bp(0, Y_VDD_B, CELL_W, Y_VDD_T, "metal1")  # VDD (상단)

# ======================================================================
# VSS 연결: MN0 source → VSS, ptap → VSS
# ======================================================================
emit("\n# === VSS ===")
# MN0의 source는 schematic에서 VSS에 직결.
# met1 바를 MN0 source에서 VSS 레일까지 내린다.
# (MN0 drain의 TAIL via1과 겹치지 않도록 좁은 폭 사용)
paint_mcon(DI["MN0"]["sc"])
mn0s_m1 = met1_on_contacts(DI["MN0"]["sc"])
vss_bar_w = min(mn0s_m1[2] - mn0s_m1[0], 23)
bp(mn0s_m1[0], Y_VSS_T, mn0s_m1[0]+vss_bar_w, mn0s_m1[1], "metal1")

ly0 = Y_PTAP_B+TAP_ENC_LICON; ly1 = ly0+CT
for ci in range(3):
    cx = col_x[ci]
    for tx in [cx+DIFF_ENC_CT, cx+DW-DIFF_ENC_CT-CT]:
        tx1 = tx+CT
        bp(tx,ly0,tx1,ly1,"viali")
        bp(tx-M1_ENC_MCON,Y_VSS_T,tx1+M1_ENC_MCON,ly1+M1_ENC_MCON_1,"metal1")

# ======================================================================
# VDD 연결 (전부 met1, met2는 Q/QB spine이 차지하므로 사용 불가)
#   MP3/MP4: source에서 VDD 레일까지 직선 met1 바 (ntap 영역 관통, 같은 VDD net)
#   MP1/MP2: SAE met1 수평선이 Gap2를 가로막으므로, 셀 가장자리로 우회하는
#            dog-leg 경로 (source → 아래 → 가장자리 → SAE 위로 → VDD)
# ======================================================================
emit("\n# === VDD ===")
ny0 = Y_NTAP_B+TAP_ENC_LICON; ny1 = ny0+CT
for ci in range(3):
    cx = col_x[ci]
    for tx in [cx+DIFF_ENC_CT, cx+DW-DIFF_ENC_CT-CT]:
        tx1 = tx+CT
        bp(tx,ny0,tx1,ny1,"viali")
        bp(tx-M1_ENC_MCON,ny0-M1_ENC_MCON_1,tx1+M1_ENC_MCON,Y_VDD_B,"metal1")

# MP3/MP4 source -> VDD rail via met1 bar (through ntap area, all VDD net)
for dn in ["MP3","MP4"]:
    d = DI[dn]
    paint_mcon(d["sc"])
    m1 = met1_on_contacts(d["sc"])
    bp(m1[0], m1[3], m1[2], Y_VDD_B, "metal1")

# MP1/MP2 source -> VDD via met1 dog-leg around SAE horizontal in Gap2
# SAE met1 horizontal at y=sae_y_lo..sae_y_hi (painted later, at SAE custom track)
# Dog-leg: go to cell edge (left for Col0, right for Col2), bypass SAE, then return
sae_m1_lo = Y_G2_SAE_B - M1_ENC_MCON  # 830-5 = 825
sae_m1_hi = Y_G2_SAE_T + M1_ENC_MCON  # 847+5 = 852
vdd_bypass_y0 = sae_m1_lo - M1_SPACE  # y below SAE with spacing
vdd_bypass_y1 = sae_m1_hi + M1_SPACE  # y above SAE with spacing

for dn in ["MP1","MP2"]:
    d = DI[dn]
    paint_mcon(d["sc"])
    m1 = met1_on_contacts(d["sc"])
    src_x0, src_x1 = m1[0], m1[2]
    if dn == "MP1":
        # Dog-leg LEFT (x=0-14) to bypass SAE at x=35-322
        edge_x0 = 0; edge_x1 = M1_WIDTH
    else:
        # Dog-leg RIGHT (x=CELL_W-14 to CELL_W)
        edge_x0 = CELL_W - M1_WIDTH; edge_x1 = CELL_W
    # Bar A: source met1 up to below SAE
    bp(src_x0, m1[3], src_x1, vdd_bypass_y0, "metal1")
    # Jog B: horizontal to cell edge at y just below SAE
    jog_b_y0 = vdd_bypass_y0 - M1_WIDTH
    bp(min(src_x0,edge_x0), jog_b_y0, max(src_x1,edge_x1), vdd_bypass_y0, "metal1")
    # Bar C: vertical at cell edge, bypassing SAE
    bp(edge_x0, jog_b_y0, edge_x1, vdd_bypass_y1, "metal1")
    # Jog D: horizontal back from cell edge at y just above SAE
    bp(min(src_x0,edge_x0), vdd_bypass_y1, max(src_x1,edge_x1), vdd_bypass_y1+M1_WIDTH, "metal1")
    # Bar E: from above SAE back at source x up to VDD rail
    bp(src_x0, vdd_bypass_y1, src_x1, Y_VDD_B, "metal1")

# ======================================================================
# FN1 넷: MN3.drain → MN1.source (met2 L자형)
#   MN3의 drain(Row0, 입력쌍 출력)과 MN1의 source(Row1, 래치 하단)를 연결.
#   met2 수평선(drain y레벨) + 수직선(source x좌표)으로 L자 형태.
#   수직선을 source x에만 두어 Q spine met2와 겹침 방지.
# ======================================================================
emit("\n# === FN1 (met2 true L-shape) ===")
paint_mcon(DI["MN3"]["dc"])
mn3d_m1 = met1_on_contacts(DI["MN3"]["dc"])
paint_mcon(DI["MN1"]["sc"])
mn1s_m1 = met1_on_contacts(DI["MN1"]["sc"])
# Via1 on MN3 drain (TOP of met1)
fn1_v1a_x = DI["MN3"]["dc"][0][0]; fn1_v1a_y = mn3d_m1[3] - VIA_SIZE - M1_ENC_VIA_MIN
paint_via1(fn1_v1a_x, fn1_v1a_y)
# Via1 on MN1 source (BOTTOM of met1)
fn1_v1b_x = DI["MN1"]["sc"][0][0]; fn1_v1b_y = mn1s_m1[1] + M1_ENC_VIA_MIN
paint_via1(fn1_v1b_x, fn1_v1b_y)
# Met2 horizontal arm: from drain via1 x to source via1 x, at drain y level
fn1_h_x0 = fn1_v1b_x - M2_ENC_VIA
fn1_h_x1 = fn1_v1a_x + VIA_SIZE + M2_ENC_VIA
fn1_h_y0 = fn1_v1a_y - M2_ENC_VIA
fn1_h_y1 = fn1_v1a_y + VIA_SIZE + M2_ENC_VIA
bp(fn1_h_x0, fn1_h_y0, fn1_h_x1, fn1_h_y1, "metal2")
# Met2 vertical arm: at source x only, from drain y level up to source y level
fn1_v_x0 = fn1_v1b_x - M2_ENC_VIA
fn1_v_x1 = fn1_v1b_x + VIA_SIZE + M2_ENC_VIA
fn1_v_y0 = fn1_v1a_y - M2_ENC_VIA  # connect to horizontal arm
fn1_v_y1 = fn1_v1b_y + VIA_SIZE + M2_ENC_VIA
bp(fn1_v_x0, fn1_v_y0, fn1_v_x1, fn1_v_y1, "metal2")

# ======================================================================
# FN2 넷: MN4.drain → MN2.source (met2 L자형, FN1의 대칭)
#   Col2 쪽. QB spine met2와 겹침 방지를 위해 source x에만 수직선.
# ======================================================================
emit("\n# === FN2 (met2 true L-shape) ===")
paint_mcon(DI["MN4"]["dc"])
mn4d_m1 = met1_on_contacts(DI["MN4"]["dc"])
paint_mcon(DI["MN2"]["sc"])
mn2s_m1 = met1_on_contacts(DI["MN2"]["sc"])
# Via1 on MN4 drain (TOP of met1)
fn2_v1a_x = DI["MN4"]["dc"][0][0]; fn2_v1a_y = mn4d_m1[3] - VIA_SIZE - M1_ENC_VIA_MIN
paint_via1(fn2_v1a_x, fn2_v1a_y)
# Via1 on MN2 source (BOTTOM of met1)
fn2_v1b_x = DI["MN2"]["sc"][0][0]; fn2_v1b_y = mn2s_m1[1] + M1_ENC_VIA_MIN
paint_via1(fn2_v1b_x, fn2_v1b_y)
# Met2 horizontal arm: from source via1 x to drain via1 x, at drain y level
fn2_h_x0 = fn2_v1b_x - M2_ENC_VIA
fn2_h_x1 = fn2_v1a_x + VIA_SIZE + M2_ENC_VIA
fn2_h_y0 = fn2_v1a_y - M2_ENC_VIA
fn2_h_y1 = fn2_v1a_y + VIA_SIZE + M2_ENC_VIA
bp(fn2_h_x0, fn2_h_y0, fn2_h_x1, fn2_h_y1, "metal2")
# Met2 vertical arm: at source x only, from drain y level up to source y level
fn2_v_x0 = fn2_v1b_x - M2_ENC_VIA
fn2_v_x1 = fn2_v1b_x + VIA_SIZE + M2_ENC_VIA
fn2_v_y0 = fn2_v1a_y - M2_ENC_VIA
fn2_v_y1 = fn2_v1b_y + VIA_SIZE + M2_ENC_VIA
bp(fn2_v_x0, fn2_v_y0, fn2_v_x1, fn2_v_y1, "metal2")

# ======================================================================
# TAIL 넷: MN3.src + MN0.drain + MN4.src 연결 (met2 수평)
#   3개 디바이스의 S/D를 Row0 하단에서 met2 수평선으로 연결.
#   via1을 met1 패드 하단에 배치하여 FN1/FN2 met2(상단)과 분리.
# ======================================================================
emit("\n# === TAIL ===")
paint_mcon(DI["MN3"]["sc"]); paint_mcon(DI["MN0"]["dc"]); paint_mcon(DI["MN4"]["sc"])
mn3s_m1 = met1_on_contacts(DI["MN3"]["sc"])
mn0d_m1 = met1_on_contacts(DI["MN0"]["dc"])
mn4s_m1 = met1_on_contacts(DI["MN4"]["sc"])
# Via1 at BOTTOM of each met1 pad (to separate from FN1/FN2 met2 at top)
vt_mn3_x = DI["MN3"]["sc"][0][0]; vt_mn3_y = mn3s_m1[1] + M1_ENC_VIA_MIN
vt_mn0_x = DI["MN0"]["dc"][0][0]; vt_mn0_y = mn0d_m1[1] + M1_ENC_VIA_MIN
vt_mn4_x = DI["MN4"]["sc"][0][0]; vt_mn4_y = mn4s_m1[1] + M1_ENC_VIA_MIN
paint_via1(vt_mn3_x, vt_mn3_y); paint_via1(vt_mn0_x, vt_mn0_y); paint_via1(vt_mn4_x, vt_mn4_y)
tail_m2_y0 = vt_mn3_y - M2_ENC_VIA; tail_m2_y1 = vt_mn3_y + VIA_SIZE + M2_ENC_VIA
bp(vt_mn3_x-M2_ENC_VIA, tail_m2_y0, vt_mn4_x+VIA_SIZE+M2_ENC_VIA, tail_m2_y1, "metal2")

# ======================================================================
# Q 넷: Col0 drain 쪽 met2 수직 spine
#   MN1.drain + MP1.drain + MP3.drain + MP5.source를 하나의 수직 met2로 연결.
#   Row3의 MP5.source는 수평 met2 stub으로 연결 (Col1에 있으므로).
# ======================================================================
emit("\n# === Q NET ===")
for dn in ["MN1","MP1","MP3"]:
    paint_mcon(DI[dn]["dc"]); met1_on_contacts(DI[dn]["dc"])
paint_mcon(DI["MP5"]["sc"]); met1_on_contacts(DI["MP5"]["sc"])

vq_mn1_x, vq_mn1_y = via1_on_m1(DI["MN1"]["dc"], at_top=False)
vq_mp1_x, vq_mp1_y = via1_on_m1(DI["MP1"]["dc"], at_top=False)
vq_mp3_x, vq_mp3_y = via1_on_m1(DI["MP3"]["dc"], at_top=False)
vq_mp5_x, vq_mp5_y = via1_on_m1(DI["MP5"]["sc"], at_top=False)

q_m2_x0 = vq_mn1_x - M2_ENC_VIA; q_m2_x1 = vq_mn1_x + VIA_SIZE + M2_ENC_VIA
q_m2_y0 = vq_mn1_y - M2_ENC_VIA; q_m2_y1 = vq_mp3_y + VIA_SIZE + M2_ENC_VIA
bp(q_m2_x0, q_m2_y0, q_m2_x1, q_m2_y1, "metal2")

# Q horizontal met2 to MP5.src (Row3)
qh_y0 = vq_mp5_y - M2_ENC_VIA; qh_y1 = vq_mp5_y + VIA_SIZE + M2_ENC_VIA
bp(q_m2_x0, qh_y0, vq_mp5_x+VIA_SIZE+M2_ENC_VIA, qh_y1, "metal2")

# ======================================================================
# QB 넷: Col2 drain 쪽 met2 수직 spine (Q의 대칭)
#   MN2.drain + MP2.drain + MP4.drain + MP5.drain을 연결.
# ======================================================================
emit("\n# === QB NET ===")
for dn in ["MN2","MP2","MP4","MP5"]:
    paint_mcon(DI[dn]["dc"]); met1_on_contacts(DI[dn]["dc"])

vqb_mn2_x, vqb_mn2_y = via1_on_m1(DI["MN2"]["dc"], at_top=False)
vqb_mp2_x, vqb_mp2_y = via1_on_m1(DI["MP2"]["dc"], at_top=False)
vqb_mp4_x, vqb_mp4_y = via1_on_m1(DI["MP4"]["dc"], at_top=False)
vqb_mp5_x, vqb_mp5_y = via1_on_m1(DI["MP5"]["dc"], at_top=False)

qb_m2_x0 = vqb_mn2_x - M2_ENC_VIA; qb_m2_x1 = vqb_mn2_x + VIA_SIZE + M2_ENC_VIA
qb_m2_y0 = vqb_mn2_y - M2_ENC_VIA; qb_m2_y1 = vqb_mp4_y + VIA_SIZE + M2_ENC_VIA
bp(qb_m2_x0, qb_m2_y0, qb_m2_x1, qb_m2_y1, "metal2")

qbh_y0 = vqb_mp5_y - M2_ENC_VIA; qbh_y1 = vqb_mp5_y + VIA_SIZE + M2_ENC_VIA
bp(vqb_mp5_x-M2_ENC_VIA, qbh_y0, qb_m2_x1, qbh_y1, "metal2")

# ======================================================================
# Cross-coupling (래치 되먹임 배선)
# ======================================================================
# StrongARM latch의 핵심: Q→MN2.G/MP2.G, QB→MN1.G/MP1.G
# MN1-MP1과 MN2-MP2의 gate poly는 이미 연속이므로, 한쪽에만 연결하면 됨.
# 경로: Q(met2 spine) → met2 stub → via1 → met1 수평선 → gate polycont
emit("\n# === CROSS-COUPLING ===")

# Cross-coupling 대상 gate에 polycont 생성
mn1_pc = add_gate_contact("MN1", Y_G0_HI_B, Y_G0_HI_T, 'up')   # MN1.G (QB넷, Gap0 상단)
mn2_pc = add_gate_contact("MN2", Y_G0_HI_B, Y_G0_HI_T, 'up')   # MN2.G (Q넷, Gap0 상단)
mp1_pc = add_gate_contact("MP1", Y_G1_LO_B, Y_G1_LO_T, 'down') # MP1.G (QB넷, Gap1 하단)
mp2_pc = add_gate_contact("MP2", Y_G1_LO_B, Y_G1_LO_T, 'down') # MP2.G (Q넷, Gap1 하단)

# --- Q cross-coupling: Q spine (Col0) -> MN2.G pad (Col2, Gap0 upper) ---
emit("# Q cross-coupling: met2 stub + met1 horizontal in Gap0 upper")

# Extend Q spine met2 down into Gap0 upper area
# Place met2 stub from Q spine x to x=100 (inter-column gap) at Gap0 upper y
q_xc_y = (Y_G0_HI_B + Y_G0_HI_T) // 2  # center of Gap0 upper track
q_xc_stub_x = 100  # landing point in inter-column gap

# Via1 at landing point (met2 -> met1)
q_xc_v1_y = q_xc_y - VIA_SIZE // 2
paint_via1(q_xc_stub_x, q_xc_v1_y)

# Met2 stub from Q spine to landing point
# Extend stub to fully cover via1 met2 pad (directional surround: 0 in x, VIA1_SURR in y)
q_xc_m2_x0 = q_m2_x0  # from Q spine left edge
q_xc_m2_x1 = q_xc_stub_x + VIA_SIZE + M2_ENC_VIA
q_v1_cx = q_xc_stub_x + VIA_SIZE//2; q_v1_cy = q_xc_v1_y + VIA_SIZE//2
q_v1_half = VIA1_MIN_W//2
q_xc_m2_y0 = min(q_xc_v1_y - M2_ENC_VIA, q_v1_cy - q_v1_half - VIA1_SURR)
q_xc_m2_y1 = max(q_xc_v1_y + VIA_SIZE + M2_ENC_VIA, q_v1_cy + q_v1_half + VIA1_SURR)
bp(q_xc_m2_x0, q_xc_m2_y0, q_xc_m2_x1, q_xc_m2_y1, "metal2")
# Also extend Q spine met2 down to this y level
bp(q_m2_x0, q_xc_m2_y0, q_m2_x1, q_m2_y1, "metal2")

# Met1 horizontal from via1 landing to MN2.G pad at Col2
# MN2.G pad met1
mn2g_m1_x0 = mn2_pc[0] - M1_ENC_MCON; mn2g_m1_x1 = mn2_pc[2] + M1_ENC_MCON
mn2g_m1_y0 = mn2_pc[1] - M1_ENC_MCON_1; mn2g_m1_y1 = mn2_pc[3] + M1_ENC_MCON_1
mn2g_m1_x0, mn2g_m1_y0, mn2g_m1_x1, mn2g_m1_y1 = ensure_m1_area(
    mn2g_m1_x0, mn2g_m1_y0, mn2g_m1_x1, mn2g_m1_y1)
bp(mn2g_m1_x0, mn2g_m1_y0, mn2g_m1_x1, mn2g_m1_y1, "metal1")

# Q xc met1 horizontal: from via1 to MN2.G pad
qxc_m1_x0 = q_xc_stub_x - M1_ENC_VIA
qxc_m1_x1 = mn2g_m1_x1
qxc_m1_y0 = mn2g_m1_y0  # align with gate pad y
qxc_m1_y1 = mn2g_m1_y1
bp(qxc_m1_x0, qxc_m1_y0, qxc_m1_x1, qxc_m1_y1, "metal1")

# --- QB cross-coupling: QB spine (Col2) -> MP1.G pad (Col0, Gap1 lower) ---
emit("# QB cross-coupling: met2 stub + met1 horizontal in Gap1 lower")

qb_xc_y = (Y_G1_LO_B + Y_G1_LO_T) // 2
qb_xc_stub_x = 258  # landing in inter-column gap (Col1-Col2), shifted left for met1.2 spacing to MP2.G

qb_xc_v1_y = qb_xc_y - VIA_SIZE // 2
paint_via1(qb_xc_stub_x, qb_xc_v1_y)

# Met2 stub from QB spine to landing
# Extend stub to fully cover via1 met2 pad (directional surround: 0 in x, VIA1_SURR in y)
qb_v1_cx = qb_xc_stub_x + VIA_SIZE//2; qb_v1_cy = qb_xc_v1_y + VIA_SIZE//2
qb_v1_half = VIA1_MIN_W//2
qb_xc_m2_x0 = qb_xc_stub_x - M2_ENC_VIA
qb_xc_m2_x1 = qb_m2_x1  # to QB spine right edge
qb_xc_m2_y0 = min(qb_xc_v1_y - M2_ENC_VIA, qb_v1_cy - qb_v1_half - VIA1_SURR)
qb_xc_m2_y1 = max(qb_xc_v1_y + VIA_SIZE + M2_ENC_VIA, qb_v1_cy + qb_v1_half + VIA1_SURR)
bp(qb_xc_m2_x0, qb_xc_m2_y0, qb_xc_m2_x1, qb_xc_m2_y1, "metal2")
# Extend QB spine met2 down to this y level
bp(qb_m2_x0, qb_xc_m2_y0, qb_m2_x1, qb_m2_y1, "metal2")

# MP1.G pad met1
mp1g_m1_x0 = mp1_pc[0] - M1_ENC_MCON; mp1g_m1_x1 = mp1_pc[2] + M1_ENC_MCON
mp1g_m1_y0 = mp1_pc[1] - M1_ENC_MCON_1; mp1g_m1_y1 = mp1_pc[3] + M1_ENC_MCON_1
mp1g_m1_x0, mp1g_m1_y0, mp1g_m1_x1, mp1g_m1_y1 = ensure_m1_area(
    mp1g_m1_x0, mp1g_m1_y0, mp1g_m1_x1, mp1g_m1_y1)
bp(mp1g_m1_x0, mp1g_m1_y0, mp1g_m1_x1, mp1g_m1_y1, "metal1")

# QB xc met1 horizontal: from MP1.G pad to via1 landing
qbxc_m1_x0 = mp1g_m1_x0
qbxc_m1_x1 = qb_xc_stub_x + VIA_SIZE + M1_ENC_VIA
qbxc_m1_y0 = mp1g_m1_y0
qbxc_m1_y1 = mp1g_m1_y1
bp(qbxc_m1_x0, qbxc_m1_y0, qbxc_m1_x1, qbxc_m1_y1, "metal1")

# Also paint MN1.G pad met1 (connected via poly to MP1.G)
mn1g_m1_x0 = mn1_pc[0]-M1_ENC_MCON; mn1g_m1_x1 = mn1_pc[2]+M1_ENC_MCON
mn1g_m1_y0 = mn1_pc[1]-M1_ENC_MCON_1; mn1g_m1_y1 = mn1_pc[3]+M1_ENC_MCON_1
mn1g_m1_x0,mn1g_m1_y0,mn1g_m1_x1,mn1g_m1_y1 = ensure_m1_area(
    mn1g_m1_x0,mn1g_m1_y0,mn1g_m1_x1,mn1g_m1_y1)
bp(mn1g_m1_x0, mn1g_m1_y0, mn1g_m1_x1, mn1g_m1_y1, "metal1")

# MP2.G pad met1 (connected via poly to MN2.G)
mp2g_m1_x0 = mp2_pc[0]-M1_ENC_MCON; mp2g_m1_x1 = mp2_pc[2]+M1_ENC_MCON
mp2g_m1_y0 = mp2_pc[1]-M1_ENC_MCON_1; mp2g_m1_y1 = mp2_pc[3]+M1_ENC_MCON_1
mp2g_m1_x0,mp2g_m1_y0,mp2g_m1_x1,mp2g_m1_y1 = ensure_m1_area(
    mp2g_m1_x0,mp2g_m1_y0,mp2g_m1_x1,mp2g_m1_y1)
bp(mp2g_m1_x0, mp2g_m1_y0, mp2g_m1_x1, mp2g_m1_y1, "metal1")

# ======================================================================
# SAE 신호 배선 (met2 수직, 끊김 없음)
#   Row3 MP3/MP5/MP4의 gate(Gap2 SAE트랙)와 Row0 MN0의 gate(Gap0 하단트랙)를
#   met2 수직선으로 연결. Gap2의 3개 polycont는 met1 수평선으로 먼저 합친다.
# ======================================================================
emit("\n# === SAE ===")
mp3_pc = add_gate_contact("MP3", Y_G2_SAE_B, Y_G2_SAE_T, 'down')
mp5_pc = add_gate_contact("MP5", Y_G2_SAE_B, Y_G2_SAE_T, 'down')
mp4_pc = add_gate_contact("MP4", Y_G2_SAE_B, Y_G2_SAE_T, 'down')

sae_x0 = mp3_pc[0]-M1_ENC_MCON_1; sae_x1 = mp4_pc[2]+M1_ENC_MCON_1
sae_y0 = mp3_pc[1]-M1_ENC_MCON; sae_y1 = mp3_pc[3]+M1_ENC_MCON
bp(sae_x0, sae_y0, sae_x1, sae_y1, "metal1")

mn0_pc = add_gate_contact("MN0", Y_G0_LO_B, Y_G0_LO_T, 'up')
mn0g_x0 = mn0_pc[0]-M1_ENC_MCON; mn0g_x1 = mn0_pc[2]+M1_ENC_MCON
mn0g_y0 = mn0_pc[1]-M1_ENC_MCON_1; mn0g_y1 = mn0_pc[3]+M1_ENC_MCON_1
mn0g_x0,mn0g_y0,mn0g_x1,mn0g_y1 = ensure_m1_area(mn0g_x0,mn0g_y0,mn0g_x1,mn0g_y1)
bp(mn0g_x0, mn0g_y0, mn0g_x1, mn0g_y1, "metal1")

sae_vx = mp5_pc[0]; sae_vy = sae_y0 + M1_ENC_VIA_MIN
paint_via1(sae_vx, sae_vy)
mn0_vx = mn0_pc[0]; mn0_vy = mn0g_y1 - VIA_SIZE - M1_ENC_VIA_MIN
paint_via1(mn0_vx, mn0_vy)

sae_m2_x0 = mn0_vx-M2_ENC_VIA; sae_m2_x1 = mn0_vx+VIA_SIZE+M2_ENC_VIA
sae_m2_y0 = mn0_vy-M2_ENC_VIA; sae_m2_y1 = sae_vy+VIA_SIZE+M2_ENC_VIA
bp(sae_m2_x0, sae_m2_y0, sae_m2_x1, sae_m2_y1, "metal2")

# ======================================================================
# INP / INN 입력 핀 (met1 패드)
#   MN3.gate = INP, MN4.gate = INN — Gap0 하단 트랙에 polycont 배치
# ======================================================================
emit("\n# === INP ===")
mn3_pc = add_gate_contact("MN3", Y_G0_LO_B, Y_G0_LO_T, 'up')
inp_x0 = mn3_pc[0]-M1_ENC_MCON_1; inp_x1 = mn3_pc[2]+M1_ENC_MCON_1
inp_y0 = mn3_pc[1]-M1_ENC_MCON; inp_y1 = mn3_pc[3]+M1_ENC_MCON
inp_x0,inp_y0,inp_x1,inp_y1 = ensure_m1_area(inp_x0,inp_y0,inp_x1,inp_y1)
bp(inp_x0, inp_y0, inp_x1, inp_y1, "metal1")

emit("\n# === INN ===")
mn4_pc = add_gate_contact("MN4", Y_G0_LO_B, Y_G0_LO_T, 'up')
inn_x0 = mn4_pc[0]-M1_ENC_MCON_1; inn_x1 = mn4_pc[2]+M1_ENC_MCON_1
inn_y0 = mn4_pc[1]-M1_ENC_MCON; inn_y1 = mn4_pc[3]+M1_ENC_MCON
inn_x0,inn_y0,inn_x1,inn_y1 = ensure_m1_area(inn_x0,inn_y0,inn_x1,inn_y1)
bp(inn_x0, inn_y0, inn_x1, inn_y1, "metal1")

# ======================================================================
# 라벨 및 포트 정의 (LVS에 필수)
# ======================================================================
# Magic에서 `label` + `port make`를 해야 SPICE 추출 시 핀 이름이 포함됨.
# 포트 번호 순서는 LVS 대조 시 schematic과 일치해야 함.
emit("\n# === LABELS & PORTS ===")
pin_defs = [
    ("SAE", sae_x0, sae_y0, sae_x1, sae_y1, "metal1"),
    ("INP", inp_x0, inp_y0, inp_x1, inp_y1, "metal1"),
    ("INN", inn_x0, inn_y0, inn_x1, inn_y1, "metal1"),
    ("Q",   q_m2_x0, q_m2_y0, q_m2_x1, q_m2_y1, "metal2"),
    ("QB",  qb_m2_x0, qb_m2_y0, qb_m2_x1, qb_m2_y1, "metal2"),
    ("VDD", 0, Y_VDD_B, CELL_W, Y_VDD_T, "metal1"),
    ("VSS", 0, Y_VSS_B, CELL_W, Y_VSS_T, "metal1"),
]
for i, (pn, x0, y0, x1, y1, layer) in enumerate(pin_defs):
    T.append(f"box {x0} {y0} {x1} {y1}")
    T.append(f"label {pn} s {layer}")
    T.append(f"port make {i+1}")

# ======================================================================
# 저장 + DRC 검증 + SPICE 추출 + GDS 출력
# ======================================================================
# save: Magic .mag 파일로 저장
# drc check: DRC 검증 (0 violations 목표)
# extract + ext2spice: 레이아웃에서 SPICE 넷리스트 추출 (LVS용)
# gds write: GDS-II 파일 출력 (OpenLane 통합용)
emit("\n# === SAVE + DRC + EXTRACT ===")
emit("save sense_amp")
emit("drc on"); emit("drc check"); emit("drc catchup")
emit("select top cell"); emit("drc why"); emit("drc count")
emit("extract all"); emit("ext2spice lvs"); emit("ext2spice")
emit("gds write sense_amp.gds")
emit("quit -noprompt")

# TCL 파일 출력
out_dir = os.path.expandvars("$PROJECT_ROOT/analog/layout/sense_amp")
tcl_path = os.path.join(out_dir, "sense_amp_gen.tcl")
with open(tcl_path, "w") as f:
    f.write("\n".join(T))
print(f"\nGenerated {tcl_path} ({len(T)} lines)")
print(f"Cell: {CELL_W} x {Y_VDD_T} lambda = {CELL_W*0.01:.2f} x {Y_VDD_T*0.01:.2f} um")
