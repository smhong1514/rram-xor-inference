#!/usr/bin/env python3
"""BL Write Driver 레이아웃 생성기 (Python → Magic TCL).

이 스크립트는 sky130B DRC 룰에 따라 좌표를 계산하고, Magic TCL 스크립트를 출력한다.
실행 방법:
  1) python3 gen_bl_wd_layout.py     → bl_write_driver_gen.tcl 생성
  2) magic -noconsole -dnull < bl_write_driver_gen.tcl  → .mag/.gds/.spice 생성

회로: 8T Tri-state Buffer (전부 sky130 1.8V, SPICE 핀순서: D,G,S,B)
  Col0 EN인버터:     MP0(EN_B,EN,VDD,VDD)  W=0.5  +  MN0(EN_B,EN,VSS,VSS)  W=0.5
  Col1 출력단 좌측:  MP1(NET_P,EN_B,VDD,VDD) W=4  +  MN1(NET_N,EN,VSS,VSS) W=4
  Col2 출력단 우측:  MP2(BL,DATA_B,NET_P,VDD) W=4 +  MN2(BL,DATA_B,NET_N,VSS) W=4
  Col3 DATA인버터:   MP3(DATA_B,DATA,VDD,VDD) W=0.5 + MN3(DATA_B,DATA,VSS,VSS) W=0.5

  동작: EN=1 → BL=DATA (풀스윙 1.774V), EN=0 → Hi-Z (tri-state)

레이아웃 구조: 4컬럼 (EN_inv | Output_L | Output_R | DATA_inv)
  - Col0/Col3 인버터: NFET↔PFET drain을 met2로 수직 연결
  - Col1↔Col2: NET_P(PFET chain), NET_N(NFET chain) met1 수평 연결
  - BL: Col2 NFET↔PFET drain을 met2로 연결

Gate 배선 (Gap 내 2-track):
  - Lower track: EN(Col0→Col1 NFET gate), DATA(Col3)
  - Upper track: EN_B(Col0 drain→Col1 PFET gate), DATA_B(Col3 drain→Col2 gate)

좌표 단위: lambda (1λ = 0.01µm = 10nm)
"""
import os

# ======================================================================
# DRC 상수 (lambda 단위, 1λ = 0.01µm, sky130B.tech 기준)
# ======================================================================
GL = 15; SD = 27; DW = SD + GL + SD  # 69λ = 디바이스 전체 폭
CT = 17; CT_PITCH = 36  # 컨택트 크기 17λ, 피치 36λ (licon.2≥17 + mcon.2≥19)
POLY_EXT = 13
POLY_SPACE = 21
POLY_ENC_CT_1 = 8
DIFF_ENC_CT = 4     # diff encl of licon (all dirs)
GATE_CT_SPACE = 6   # licon to gate spacing
LI_ENC_CT = 8       # li1 encl of licon (one dir)
LI_MIN_AREA = 561; LI_SPACE = 17
M1_WIDTH = 14; M1_SPACE = 14; M1_MIN_AREA = 830
M1_ENC_MCON = 5     # met1 encl mcon (via.1a+2*via.4a: 17+10=27≥26)
M1_ENC_MCON_1 = 6   # met1 encl mcon (one dir)
NW_ENC = 18; NW_WIDTH = 84
DIFF_SPACE = 27; TAP_SPACE = 27
TAP_ENC_LICON = 12  # tap encl of licon (one dir, licon.7)
TAP_MIN_AREA = 702  # 0.07011µm² → 702λ² (rounded up)
VIA_SIZE = 15
M1_ENC_VIA = 6      # met1 encl via1 (one dir)
M1_ENC_VIA_MIN = 6  # met1 encl via1 (all dirs) for combined rule
M2_WIDTH = 14; M2_SPACE = 14; M2_MIN_AREA = 676
M2_ENC_VIA = 6
MCON_SPACE = 19
POLYCONT_DIFF_SPACE = 24  # licon.9 + psdm.5a

# ======================================================================
# 디바이스 파라미터
# ======================================================================
W_SM = 50    # 인버터 트랜지스터 폭 (0.5µm = 50λ)
W_LG = 400   # 출력단 트랜지스터 폭 (4.0µm = 400λ, 대전류 구동)

# 레이아웃 간격
MARGIN = 15; COL_SP = 60; RAIL_H = 48

# ======================================================================
# 컬럼 정의 (각 컬럼 = NFET + PFET 쌍)
# ======================================================================
# shared_gate=True: NFET/PFET이 같은 gate 신호 → poly가 연속으로 관통
# shared_gate=False: NFET/PFET이 다른 gate → poly를 분리하여 별도 polycont
# track: polycont 배치 위치 ("lower" = Gap 아래쪽, "upper" = 위쪽)
COLS = [
    {"id": 0, "w_n": W_SM, "w_p": W_SM, "shared_gate": True,   # EN 인버터
     "p_gate": "EN", "n_gate": "EN", "p_src": "VDD", "n_src": "VSS",
     "p_drn": "EN_B", "n_drn": "EN_B", "track": "lower"},
    {"id": 1, "w_n": W_LG, "w_p": W_LG, "shared_gate": False,  # 출력단 좌측 (gate 분리)
     "p_gate": "EN_B", "n_gate": "EN", "p_src": "VDD", "n_src": "VSS",
     "p_drn": "NET_P", "n_drn": "NET_N"},
    {"id": 2, "w_n": W_LG, "w_p": W_LG, "shared_gate": True,   # 출력단 우측
     "p_gate": "DATA_B", "n_gate": "DATA_B", "p_src": "NET_P", "n_src": "NET_N",
     "p_drn": "BL", "n_drn": "BL", "track": "upper"},
    {"id": 3, "w_n": W_SM, "w_p": W_SM, "shared_gate": True,   # DATA 인버터
     "p_gate": "DATA", "n_gate": "DATA", "p_src": "VDD", "n_src": "VSS",
     "p_drn": "DATA_B", "n_drn": "DATA_B", "track": "lower"},
]

# ======================================================================
# 수직 좌표 계산 (아래→위 순서로 적층)
# ======================================================================
# 전체 구조:
#   VSS 레일 → ptap → NFET row (W_LG=400λ) → Gap → PFET row → ntap → VDD 레일
GAP = 130  # NFET↔PFET 사이 gap (polycont + 배선 공간)

y = 0
Y_VSS_B = y; y += RAIL_H; Y_VSS_T = y; y += 12       # VSS 전원 레일

TAP_H = CT + 2 * TAP_ENC_LICON  # 41λ (licon + 양쪽 enclosure)

Y_PTAP_B = y; y += TAP_H; Y_PTAP_T = y; y += TAP_SPACE  # p-tap (VSS 연결)
Y_ND_B = y; y += W_LG; Y_ND_T = y                        # NFET diff 영역
Y_GAP_B = y; y += GAP; Y_GAP_T = y                        # Gap (gate poly contact)
Y_PD_B = y; y += W_LG; Y_PD_T = y; y += TAP_SPACE        # PFET diff 영역
Y_NTAP_B = y; y += TAP_H; Y_NTAP_T = y; y += 12          # n-tap (VDD 연결)
Y_VDD_B = y; y += RAIL_H; Y_VDD_T = y                     # VDD 전원 레일

# Gap 내 poly contact 2-track 시스템
# Lower track: NFET diff 상단에서 24λ 떨어진 위치 (EN, DATA gate)
Y_LO_B = Y_GAP_B + POLYCONT_DIFF_SPACE; Y_LO_T = Y_LO_B + CT
# Upper track: PFET diff 하단에서 24λ 떨어진 위치 (EN_B, DATA_B gate)
Y_HI_T = Y_GAP_T - POLYCONT_DIFF_SPACE; Y_HI_B = Y_HI_T - CT

# Verify poly spacing between tracks
lo_pad_top = Y_LO_T + POLY_ENC_CT_1
hi_pad_bot = Y_HI_B - POLY_ENC_CT_1
assert hi_pad_bot - lo_pad_top >= POLY_SPACE, \
    f"Poly spacing {hi_pad_bot - lo_pad_top} < {POLY_SPACE}"

# Verify met1 spacing between tracks
lo_m1_top = Y_LO_T + M1_ENC_MCON
hi_m1_bot = Y_HI_B - M1_ENC_MCON
assert hi_m1_bot - lo_m1_top >= M1_SPACE, \
    f"Met1 spacing {hi_m1_bot - lo_m1_top} < {M1_SPACE}"

print(f"Track spacing: poly={hi_pad_bot - lo_pad_top}, met1={hi_m1_bot - lo_m1_top}")

# Horizontal coordinates
col_x = []
x = MARGIN
for c in COLS:
    col_x.append(x)
    x += DW + COL_SP
CELL_W = x - COL_SP + MARGIN

# Nwell
NW_X0 = min(col_x) - NW_ENC
NW_X1 = max(col_x) + DW + NW_ENC
NW_Y0 = Y_PD_B - NW_ENC
NW_Y1 = Y_NTAP_T + NW_ENC

print(f"Cell: {CELL_W} x {Y_VDD_T} lambda = {CELL_W*0.01:.2f} x {Y_VDD_T*0.01:.2f} µm")

# ======================================================================
# TCL generation
# ======================================================================
T = []

def emit(s): T.append(s)
def bp(x0, y0, x1, y1, layer):
    T.append(f"box {x0} {y0} {x1} {y1}")
    T.append(f"paint {layer}")

def contacts_in_sd(cx0, cy0, sd_w, diff_h, is_drain=False):
    """Return list of (x0,y0,x1,y1) for contacts in S/D region."""
    if is_drain:
        c_x0 = cx0 + GATE_CT_SPACE  # 6λ from gate
    else:
        c_x0 = cx0 + DIFF_ENC_CT    # 4λ from diff edge
    c_x1 = c_x0 + CT
    avail = diff_h - 2 * 6  # 6 for one-dir enclosure
    nc = max(1, (avail - CT) // CT_PITCH + 1)
    arr_h = (nc - 1) * CT_PITCH + CT
    sy = cy0 + (diff_h - arr_h) // 2
    return [(c_x0, sy + i*CT_PITCH, c_x1, sy + i*CT_PITCH + CT) for i in range(nc)]

def paint_contacts(contacts, layer):
    for (x0, y0, x1, y1) in contacts:
        bp(x0, y0, x1, y1, layer)

def paint_li1_strip_y(contacts):
    """Paint li1 strip with y-direction enclosure (8λ above/below).
    This avoids li.3 spacing issues in x-direction."""
    if not contacts: return None
    x0 = contacts[0][0]
    x1 = contacts[0][2]
    y0 = contacts[0][1] - LI_ENC_CT
    y1 = contacts[-1][3] + LI_ENC_CT
    w, h = x1-x0, y1-y0
    if w * h < LI_MIN_AREA:
        need_h = (LI_MIN_AREA + w - 1) // w
        extra = need_h - h
        y0 -= extra // 2; y1 += (extra+1) // 2
    bp(x0, y0, x1, y1, "locali")
    return (x0, y0, x1, y1)

def paint_mcon(contacts):
    for (x0, y0, x1, y1) in contacts:
        bp(x0, y0, x1, y1, "viali")

VIA1_MIN_W = 26   # via.1a + 2*via.4a: minimum via1 paint width
VIA1_SURR = 3     # via.5a - via.4a: directional met1/met2 surround

def paint_via1(vx0, vy0):
    """Paint via1 (26×26) + met1/met2 directional surround (3λ right, 3λ top/bottom)."""
    cx = vx0 + VIA_SIZE // 2
    cy = vy0 + VIA_SIZE // 2
    v1x0 = cx - VIA1_MIN_W // 2
    v1y0 = cy - VIA1_MIN_W // 2
    v1x1 = v1x0 + VIA1_MIN_W
    v1y1 = v1y0 + VIA1_MIN_W
    bp(v1x0, v1y0, v1x1, v1y1, "via1")
    # Directional surround: extend right + top/bottom by 3λ
    bp(v1x0, v1y0 - VIA1_SURR, v1x1 + VIA1_SURR, v1y1 + VIA1_SURR, "metal1")
    bp(v1x0, v1y0 - VIA1_SURR, v1x1 + VIA1_SURR, v1y1 + VIA1_SURR, "metal2")

def met1_on_contacts(contacts, extra_y0=None, extra_y1=None):
    """Paint met1 covering contacts. Uses M1_ENC_MCON_1 in y, M1_ENC_MCON in x."""
    x0 = contacts[0][0] - M1_ENC_MCON
    x1 = contacts[0][2] + M1_ENC_MCON
    y0 = contacts[0][1] - M1_ENC_MCON_1   # 6λ in y-direction
    y1 = contacts[-1][3] + M1_ENC_MCON_1
    if extra_y0 is not None: y0 = min(y0, extra_y0)
    if extra_y1 is not None: y1 = max(y1, extra_y1)
    w, h = x1-x0, y1-y0
    if w * h < M1_MIN_AREA:
        need_h = (M1_MIN_AREA + w - 1) // w
        extra = need_h - h
        y0 -= extra // 2; y1 += (extra+1) // 2
    bp(x0, y0, x1, y1, "metal1")
    return (x0, y0, x1, y1)

def ensure_m1_area(x0, y0, x1, y1):
    w, h = x1-x0, y1-y0
    if w * h < M1_MIN_AREA:
        need_h = (M1_MIN_AREA + w - 1) // w
        extra = need_h - h
        y0 -= extra // 2; y1 += (extra+1) // 2
    return x0, y0, x1, y1

# Header
emit("tech load $PDK_ROOT/sky130B/libs.tech/magic/sky130B.tech")
emit("drc style drc(full)")
emit("drc off")
emit("snap internal")
emit("cellname delete bl_write_driver")
emit("edit")

# Nwell
emit("\n# === NWELL ===")
bp(NW_X0, NW_Y0, NW_X1, NW_Y1, "nwell")

# ======================================================================
# 4개 컬럼 반복 생성 (diff + poly + contacts + li1)
# ======================================================================
# 각 컬럼에서 NFET(하단), PFET(상단)을 생성하고,
# gate polycont를 Gap 내 해당 트랙에 배치한다.
# shared_gate 여부에 따라 poly 관통(연속) 또는 분리 처리.
cd = []  # 컬럼 데이터 저장용

for ci, col in enumerate(COLS):
    cx = col_x[ci]
    wn, wp = col["w_n"], col["w_p"]
    emit(f"\n# === Col{ci} (W_n={wn*0.01:.1f}, W_p={wp*0.01:.1f}) ===")

    nd_y0 = Y_ND_B; nd_y1 = nd_y0 + wn
    bp(cx, nd_y0, cx+DW, nd_y1, "ndiff")

    pd_y0 = Y_PD_B; pd_y1 = pd_y0 + wp
    bp(cx, pd_y0, cx+DW, pd_y1, "pdiff")

    # Gate poly
    gx0 = cx + SD; gx1 = gx0 + GL; gcx = (gx0 + gx1) // 2
    pad_w = CT + 2 * POLY_ENC_CT_1  # 33

    pc_list = []

    if col["shared_gate"]:
        track = col["track"]
        if track == "lower":
            pc_y0, pc_y1 = Y_LO_B, Y_LO_T
        else:
            pc_y0, pc_y1 = Y_HI_B, Y_HI_T

        py0 = nd_y0 - POLY_EXT; py1 = pd_y1 + POLY_EXT
        bp(gx0, py0, gx1, py1, "poly")

        px0 = gcx - pad_w // 2; px1 = px0 + pad_w
        pad_y0 = pc_y0 - POLY_ENC_CT_1; pad_y1 = pc_y1 + POLY_ENC_CT_1
        bp(px0, pad_y0, px1, pad_y1, "poly")

        pcx0 = gcx - CT // 2; pcx1 = pcx0 + CT
        bp(pcx0, pc_y0, pcx1, pc_y1, "polycont")

        # Li1: use pad width (x-encl = 8 on each side of contact)
        li_x0 = px0; li_x1 = px1
        li_y0 = pc_y0; li_y1 = pc_y1
        if (li_x1-li_x0)*(li_y1-li_y0) < LI_MIN_AREA:
            eh = (LI_MIN_AREA//(li_x1-li_x0)) - (li_y1-li_y0) + 2
            li_y0 -= eh//2; li_y1 += (eh+1)//2
        bp(li_x0, li_y0, li_x1, li_y1, "locali")

        pc_list.append({"net": col["p_gate"], "pcx0": pcx0, "pcx1": pcx1,
                         "py0": pc_y0, "py1": pc_y1,
                         "li_x0": li_x0, "li_y0": li_y0, "li_x1": li_x1, "li_y1": li_y1,
                         "pad_x0": px0, "pad_x1": px1, "track": track})
    else:
        # Col1: separate polys
        n_py0 = nd_y0 - POLY_EXT
        n_pad_y0 = Y_LO_B - POLY_ENC_CT_1
        n_pad_y1 = Y_LO_T + POLY_ENC_CT_1
        bp(gx0, n_py0, gx1, n_pad_y1, "poly")
        px0 = gcx - pad_w//2; px1 = px0 + pad_w
        bp(px0, n_pad_y0, px1, n_pad_y1, "poly")
        pcx0 = gcx - CT//2; pcx1 = pcx0 + CT
        bp(pcx0, Y_LO_B, pcx1, Y_LO_T, "polycont")
        li_x0 = px0; li_x1 = px1; li_y0 = Y_LO_B; li_y1 = Y_LO_T
        if (li_x1-li_x0)*(li_y1-li_y0) < LI_MIN_AREA:
            eh = (LI_MIN_AREA//(li_x1-li_x0)) - (li_y1-li_y0) + 2
            li_y0 -= eh//2; li_y1 += (eh+1)//2
        bp(li_x0, li_y0, li_x1, li_y1, "locali")
        pc_list.append({"net": col["n_gate"], "pcx0": pcx0, "pcx1": pcx1,
                         "py0": Y_LO_B, "py1": Y_LO_T,
                         "li_x0": li_x0, "li_y0": li_y0, "li_x1": li_x1, "li_y1": li_y1,
                         "pad_x0": px0, "pad_x1": px1, "track": "lower"})

        p_pad_y0 = Y_HI_B - POLY_ENC_CT_1
        p_pad_y1 = Y_HI_T + POLY_ENC_CT_1
        p_py1 = pd_y1 + POLY_EXT
        bp(gx0, p_pad_y0, gx1, p_py1, "poly")
        bp(px0, p_pad_y0, px1, p_pad_y1, "poly")
        bp(pcx0, Y_HI_B, pcx1, Y_HI_T, "polycont")
        li_y0p = Y_HI_B; li_y1p = Y_HI_T
        if (li_x1-li_x0)*(li_y1p-li_y0p) < LI_MIN_AREA:
            eh = (LI_MIN_AREA//(li_x1-li_x0)) - (li_y1p-li_y0p) + 2
            li_y0p -= eh//2; li_y1p += (eh+1)//2
        bp(li_x0, li_y0p, li_x1, li_y1p, "locali")
        pc_list.append({"net": col["p_gate"], "pcx0": pcx0, "pcx1": pcx1,
                         "py0": Y_HI_B, "py1": Y_HI_T,
                         "li_x0": li_x0, "li_y0": li_y0p, "li_x1": li_x1, "li_y1": li_y1p,
                         "pad_x0": px0, "pad_x1": px1, "track": "upper"})

    # S/D contacts (drain uses GATE_CT_SPACE for gate clearance)
    drn_x0 = cx + SD + GL
    src_n = contacts_in_sd(cx, nd_y0, SD, wn, is_drain=False)
    drn_n = contacts_in_sd(drn_x0, nd_y0, SD, wn, is_drain=True)
    src_p = contacts_in_sd(cx, pd_y0, SD, wp, is_drain=False)
    drn_p = contacts_in_sd(drn_x0, pd_y0, SD, wp, is_drain=True)
    emit("# S/D contacts")
    paint_contacts(src_n, "ndiffc"); paint_contacts(drn_n, "ndiffc")
    paint_contacts(src_p, "pdiffc"); paint_contacts(drn_p, "pdiffc")

    # Li1 strips (y-direction enclosure to avoid li.3 in x)
    emit("# li1 strips (y-direction enclosure)")
    sn_li = paint_li1_strip_y(src_n)
    dn_li = paint_li1_strip_y(drn_n)
    sp_li = paint_li1_strip_y(src_p)
    dp_li = paint_li1_strip_y(drn_p)

    cd.append({"cx": cx, "gx0": gx0, "gx1": gx1, "gcx": gcx,
               "nd_y0": nd_y0, "nd_y1": nd_y1, "pd_y0": pd_y0, "pd_y1": pd_y1,
               "src_n": src_n, "drn_n": drn_n, "src_p": src_p, "drn_p": drn_p,
               "sn_li": sn_li, "dn_li": dn_li, "sp_li": sp_li, "dp_li": dp_li,
               "pc": pc_list, "col": col})

# ======================================================================
# Substrate taps (separate diffusion + contacts for proper enclosure)
# ======================================================================
emit("\n# === TAPS ===")
for ci in range(4):
    cx = col_x[ci]

    licon_y0 = Y_PTAP_B + TAP_ENC_LICON
    licon_y1 = licon_y0 + CT
    tx0 = cx + DIFF_ENC_CT; tx1 = tx0 + CT
    tx2 = cx + DW - DIFF_ENC_CT - CT; tx3 = tx2 + CT

    # P-tap (below NFET, connects to VSS)
    # Paint ptapc composite first (creates proper substrate contact: ptap+licon+li1)
    bp(tx0, licon_y0, tx1, licon_y1, "ptapc")
    bp(tx2, licon_y0, tx3, licon_y1, "ptapc")
    # Extend ptap diffusion for enclosure (licon.7: ≥12λ one dir)
    bp(cx, Y_PTAP_B, cx + DW, Y_PTAP_T, "ptap")
    # Extend li1 for area and enclosure
    bp(tx0, licon_y0 - LI_ENC_CT, tx3, licon_y1 + LI_ENC_CT, "locali")

    # N-tap (above PFET, in nwell, connects to VDD)
    licon_y0n = Y_NTAP_B + TAP_ENC_LICON
    licon_y1n = licon_y0n + CT
    bp(tx0, licon_y0n, tx1, licon_y1n, "ntapc")
    bp(tx2, licon_y0n, tx3, licon_y1n, "ntapc")
    bp(cx, Y_NTAP_B, cx + DW, Y_NTAP_T, "ntap")
    bp(tx0, licon_y0n - LI_ENC_CT, tx3, licon_y1n + LI_ENC_CT, "locali")

# ======================================================================
# Power rails + connections
# ======================================================================
emit("\n# === POWER RAILS ===")
bp(0, Y_VSS_B, CELL_W, Y_VSS_T, "metal1")
bp(0, Y_VDD_B, CELL_W, Y_VDD_T, "metal1")

for ci in range(4):
    col = cd[ci]; c = col["col"]; cx = col_x[ci]
    if c["n_src"] == "VSS":
        emit(f"# Col{ci} NFET src→VSS")
        paint_mcon(col["src_n"])
        x0 = col["src_n"][0][0]-M1_ENC_MCON; x1 = col["src_n"][0][2]+M1_ENC_MCON
        bp(x0, Y_VSS_T, x1, col["src_n"][-1][3]+M1_ENC_MCON_1, "metal1")
        # P-tap mcon + met1
        licon_y0 = Y_PTAP_B + TAP_ENC_LICON; licon_y1 = licon_y0 + CT
        tx0 = cx+DIFF_ENC_CT; tx1 = tx0+CT
        bp(tx0, licon_y0, tx1, licon_y1, "viali")
        bp(tx0-M1_ENC_MCON, Y_VSS_T, tx1+M1_ENC_MCON, licon_y1+M1_ENC_MCON_1, "metal1")
        tx2 = cx+DW-DIFF_ENC_CT-CT; tx3 = tx2+CT
        bp(tx2, licon_y0, tx3, licon_y1, "viali")
        bp(tx2-M1_ENC_MCON, Y_VSS_T, tx3+M1_ENC_MCON, licon_y1+M1_ENC_MCON_1, "metal1")

    if c["p_src"] == "VDD":
        emit(f"# Col{ci} PFET src→VDD")
        paint_mcon(col["src_p"])
        x0 = col["src_p"][0][0]-M1_ENC_MCON; x1 = col["src_p"][0][2]+M1_ENC_MCON
        bp(x0, col["src_p"][0][1]-M1_ENC_MCON_1, x1, Y_VDD_B, "metal1")
        # N-tap mcon + met1
        licon_y0n = Y_NTAP_B + TAP_ENC_LICON; licon_y1n = licon_y0n + CT
        tx0 = cx+DIFF_ENC_CT; tx1 = tx0+CT
        bp(tx0, licon_y0n, tx1, licon_y1n, "viali")
        bp(tx0-M1_ENC_MCON, licon_y0n-M1_ENC_MCON_1, tx1+M1_ENC_MCON, Y_VDD_B, "metal1")
        tx2 = cx+DW-DIFF_ENC_CT-CT; tx3 = tx2+CT
        bp(tx2, licon_y0n, tx3, licon_y1n, "viali")
        bp(tx2-M1_ENC_MCON, licon_y0n-M1_ENC_MCON_1, tx3+M1_ENC_MCON, Y_VDD_B, "metal1")

# ======================================================================
# Drain 연결 (내부 넷 배선)
# ======================================================================
# Col0 (EN_B), Col3 (DATA_B): 인버터 출력 — NFET↔PFET drain을 met2 수직으로 연결
# Col1↔Col2 (NET_P, NET_N): 시리즈 PMOS/NMOS 중간 노드 — met1 수평으로 연결
# Col2 (BL): 출력 — NFET↔PFET drain을 met2 수직으로 연결
emit("\n# === DRAIN CONNECTIONS ===")

# 인버터 컬럼 (Col0, Col3): drain NFET↔PFET via met2
for ci in [0, 3]:
    col = cd[ci]
    emit(f"# Col{ci} drain (NFET↔PFET via met2)")
    paint_mcon(col["drn_n"]); paint_mcon(col["drn_p"])
    n_m1 = met1_on_contacts(col["drn_n"])
    p_m1 = met1_on_contacts(col["drn_p"])
    vx0 = col["drn_n"][0][0]; vx1 = vx0 + VIA_SIZE
    vy0_n = n_m1[3] - VIA_SIZE - M1_ENC_VIA_MIN
    paint_via1(vx0, vy0_n)
    vy0_p = p_m1[1] + M1_ENC_VIA_MIN
    vy1_p = vy0_p + VIA_SIZE
    paint_via1(vx0, vy0_p)
    m2x0 = vx0 - M2_ENC_VIA; m2x1 = vx1 + M2_ENC_VIA
    m2y0 = vy0_n - M2_ENC_VIA; m2y1 = vy1_p + M2_ENC_VIA
    bp(m2x0, m2y0, m2x1, m2y1, "metal2")

# NET_P: Col1 PFET drain → Col2 PFET source
emit("# NET_P: Col1 PFET drain → Col2 PFET source")
paint_mcon(cd[1]["drn_p"]); paint_mcon(cd[2]["src_p"])
p1d_m1 = met1_on_contacts(cd[1]["drn_p"])
p2s_m1 = met1_on_contacts(cd[2]["src_p"])
mid_p = cd[1]["drn_p"][len(cd[1]["drn_p"])//2]
hp_y0 = mid_p[1] - M1_ENC_MCON_1; hp_y1 = mid_p[3] + M1_ENC_MCON_1
bp(p1d_m1[0], hp_y0, p2s_m1[2], hp_y1, "metal1")

# NET_N: Col1 NFET drain → Col2 NFET source
emit("# NET_N: Col1 NFET drain → Col2 NFET source")
paint_mcon(cd[1]["drn_n"]); paint_mcon(cd[2]["src_n"])
n1d_m1 = met1_on_contacts(cd[1]["drn_n"])
n2s_m1 = met1_on_contacts(cd[2]["src_n"])
mid_n = cd[1]["drn_n"][len(cd[1]["drn_n"])//2]
hn_y0 = mid_n[1] - M1_ENC_MCON_1; hn_y1 = mid_n[3] + M1_ENC_MCON_1
bp(n1d_m1[0], hn_y0, n2s_m1[2], hn_y1, "metal1")

# BL: Col2 drain NFET↔PFET via met2
emit("# BL: Col2 drain NFET↔PFET via met2")
paint_mcon(cd[2]["drn_n"]); paint_mcon(cd[2]["drn_p"])
bl_n_m1 = met1_on_contacts(cd[2]["drn_n"])
bl_p_m1 = met1_on_contacts(cd[2]["drn_p"])
vx0 = cd[2]["drn_n"][0][0]; vx1 = vx0 + VIA_SIZE
vy0_n = bl_n_m1[3] - VIA_SIZE - M1_ENC_VIA_MIN
paint_via1(vx0, vy0_n)
vy0_p = bl_p_m1[1] + M1_ENC_VIA_MIN
vy1_p = vy0_p + VIA_SIZE
paint_via1(vx0, vy0_p)
m2x0 = vx0 - M2_ENC_VIA; m2x1 = vx1 + M2_ENC_VIA
m2y0 = vy0_n - M2_ENC_VIA; m2y1 = vy1_p + M2_ENC_VIA
bp(m2x0, m2y0, m2x1, m2y1, "metal2")

# ======================================================================
# Gate 신호 배선 (Gap 내 2-track met1 수평선)
# ======================================================================
# EN: Col0 gate(lower track) → Col1 NFET gate(lower track) — met1 수평
# EN_B: Col0 drain(met2) → via1 → Col1 PFET gate(upper track) — met1 수평
# DATA_B: Col3 drain(met2) → via1 → Col2 gate(upper track) — met1 수평
# DATA: Col3 gate(lower track) — met1 패드만 (외부 핀)
emit("\n# === GATE ROUTING ===")

# EN: Col0 gate(lower) → Col1 NFET gate(lower) — met1 수평 연결
pc0 = cd[0]["pc"][0]
pc1n = cd[1]["pc"][0]
emit("# EN: Col0 gate → Col1 NFET gate (lower track met1)")
bp(pc0["pcx0"], pc0["py0"], pc0["pcx1"], pc0["py1"], "viali")
bp(pc1n["pcx0"], pc1n["py0"], pc1n["pcx1"], pc1n["py1"], "viali")
en_m1_x0 = pc0["pcx0"] - M1_ENC_MCON_1
en_m1_x1 = pc1n["pcx1"] + M1_ENC_MCON_1
en_m1_y0 = pc0["py0"] - M1_ENC_MCON
en_m1_y1 = pc0["py1"] + M1_ENC_MCON
en_m1_x0, en_m1_y0, en_m1_x1, en_m1_y1 = ensure_m1_area(
    en_m1_x0, en_m1_y0, en_m1_x1, en_m1_y1)
bp(en_m1_x0, en_m1_y0, en_m1_x1, en_m1_y1, "metal1")

# EN_B: Col0 drain met2 → via1 (upper) → met1 → Col1 PFET gate (upper)
pc1p = cd[1]["pc"][1]
emit("# EN_B: Col0 drain → Col1 PFET gate (upper track met1)")
c0_drn_x0 = cd[0]["drn_n"][0][0]; c0_drn_x1 = c0_drn_x0 + VIA_SIZE
enb_via_y0 = Y_HI_B; enb_via_y1 = enb_via_y0 + VIA_SIZE
paint_via1(c0_drn_x0, enb_via_y0)
bp(pc1p["pcx0"], pc1p["py0"], pc1p["pcx1"], pc1p["py1"], "viali")
enb_m1_x0 = c0_drn_x0 - M1_ENC_VIA
enb_m1_x1 = pc1p["pcx1"] + M1_ENC_MCON_1
enb_m1_y0 = min(enb_via_y0, pc1p["py0"]) - M1_ENC_MCON
enb_m1_y1 = max(enb_via_y1, pc1p["py1"]) + M1_ENC_MCON
enb_m1_x0, enb_m1_y0, enb_m1_x1, enb_m1_y1 = ensure_m1_area(
    enb_m1_x0, enb_m1_y0, enb_m1_x1, enb_m1_y1)
bp(enb_m1_x0, enb_m1_y0, enb_m1_x1, enb_m1_y1, "metal1")

# DATA_B: Col3 drain met2 → via1 (upper) → met1 → Col2 gate (upper)
pc2 = cd[2]["pc"][0]
emit("# DATA_B: Col3 drain → Col2 gate (upper track met1)")
c3_drn_x0 = cd[3]["drn_n"][0][0]; c3_drn_x1 = c3_drn_x0 + VIA_SIZE
db_via_y0 = Y_HI_B; db_via_y1 = db_via_y0 + VIA_SIZE
paint_via1(c3_drn_x0, db_via_y0)
bp(pc2["pcx0"], pc2["py0"], pc2["pcx1"], pc2["py1"], "viali")
db_m1_x0 = pc2["pcx0"] - M1_ENC_MCON_1
db_m1_x1 = c3_drn_x1 + M1_ENC_VIA
db_m1_y0 = min(db_via_y0, pc2["py0"]) - M1_ENC_MCON
db_m1_y1 = max(db_via_y1, pc2["py1"]) + M1_ENC_MCON
db_m1_x0, db_m1_y0, db_m1_x1, db_m1_y1 = ensure_m1_area(
    db_m1_x0, db_m1_y0, db_m1_x1, db_m1_y1)
bp(db_m1_x0, db_m1_y0, db_m1_x1, db_m1_y1, "metal1")

# ======================================================================
# Signal Pins (on met1)
# ======================================================================
emit("\n# === SIGNAL PINS ===")

pc3 = cd[3]["pc"][0]
emit("# DATA pin met1")
bp(pc3["pcx0"], pc3["py0"], pc3["pcx1"], pc3["py1"], "viali")
data_m1_x0 = pc3["pcx0"] - M1_ENC_MCON_1
data_m1_x1 = pc3["pcx1"] + M1_ENC_MCON_1
data_m1_y0 = pc3["py0"] - M1_ENC_MCON
data_m1_y1 = pc3["py1"] + M1_ENC_MCON
data_m1_x0, data_m1_y0, data_m1_x1, data_m1_y1 = ensure_m1_area(
    data_m1_x0, data_m1_y0, data_m1_x1, data_m1_y1)
bp(data_m1_x0, data_m1_y0, data_m1_x1, data_m1_y1, "metal1")

# 라벨 + 포트 정의 (LVS 추출에 필수, 's'는 font parse 이슈 회피용 방향 지정자)
emit("\n# === LABELS & PORTS ===")
pin_defs = [
    ("EN",   en_m1_x0,   en_m1_y0,   en_m1_x1,   en_m1_y1),
    ("DATA", data_m1_x0, data_m1_y0, data_m1_x1, data_m1_y1),
    ("BL",   bl_n_m1[0], bl_n_m1[1], bl_n_m1[2], bl_n_m1[3]),
    ("VDD",  0,          Y_VDD_B,    CELL_W,      Y_VDD_T),
    ("VSS",  0,          Y_VSS_B,    CELL_W,      Y_VSS_T),
]
for i, (pname, x0, y0, x1, y1) in enumerate(pin_defs):
    T.append(f"box {x0} {y0} {x1} {y1}")
    T.append(f"label {pname} s metal1")
    T.append(f"port make {i+1}")

# ======================================================================
# 저장 + DRC 검증 + SPICE 추출 + GDS 출력
# ======================================================================
emit("\n# === SAVE + DRC + EXTRACT ===")
emit("save bl_write_driver")
emit("drc on")
emit("drc check")
emit("drc catchup")
emit("select top cell")
emit("drc why")
emit("drc count")
emit("extract all")
emit("ext2spice lvs")
emit("ext2spice")
emit("gds write bl_write_driver.gds")
emit("quit -noprompt")

# Write
out_dir = os.path.expandvars("$PROJECT_ROOT/analog/layout/bl_write_driver")
tcl_path = os.path.join(out_dir, "bl_write_driver_gen.tcl")
with open(tcl_path, "w") as f:
    f.write("\n".join(T))
print(f"Generated {tcl_path} ({len(T)} lines)")
print(f"Cell: {CELL_W}x{Y_VDD_T} lambda = {CELL_W*0.01:.2f}x{Y_VDD_T*0.01:.2f} µm")
