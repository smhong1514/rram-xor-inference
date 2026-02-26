#!/usr/bin/env python3
"""ReLU 5T OTA Layout Generator (Python -> Magic TCL).

Circuit: 5T OTA (SPICE pin order: D, G, S, B)
  Row1 PMOS W=2.0: M3(node_A, node_A, VDD, VDD)  M4(OUT, node_A, VDD, VDD)
  Row0 NMOS W=2.0: M1(node_A, VREF, TAIL, VSS)    M2(OUT, VBL, TAIL, VSS)
  Tail NMOS W=2.0: M5(TAIL, VBIAS, VSS, VSS)  -- centered below

Layout: 2 columns (Col0=M1/M3 left, Col1=M2/M4 right) + M5 center bottom
"""
import os

# ======================================================================
# DRC constants (lambda units, 1lambda = 10nm)
# ======================================================================
GL = 50             # gate length (L=0.5um for ReLU OTA)
SD = 27             # source/drain width
DW = SD + GL + SD   # device width = 104
CT = 17             # contact size
CT_PITCH = 36       # contact pitch
POLY_EXT = 13       # poly extension beyond diff
POLY_SPACE = 21     # min poly spacing
POLY_ENC_CT_1 = 8   # poly enclosure of polycont
DIFF_ENC_CT = 4     # diff enclosure of licon (source side)
GATE_CT_SPACE = 6   # gate to drain licon spacing
LI_ENC_CT = 8       # li1 enclosure of licon
LI_MIN_AREA = 561   # li1 min area
LI_SPACE = 17       # li1 min spacing
M1_WIDTH = 14; M1_SPACE = 14; M1_MIN_AREA = 830
M1_ENC_MCON = 5; M1_ENC_MCON_1 = 6
NW_ENC = 18         # nwell enclosure of pdiff
DIFF_SPACE = 27; TAP_SPACE = 27; TAP_ENC_LICON = 12
VIA_SIZE = 15
M1_ENC_VIA = 6; M1_ENC_VIA_MIN = 6
M2_WIDTH = 14; M2_SPACE = 14; M2_MIN_AREA = 676; M2_ENC_VIA = 6
POLYCONT_DIFF_SPACE = 24
VIA1_MIN_W = 26; VIA1_SURR = 3

W200 = 200
MARGIN = 15
COL_SP = 60         # column spacing
RAIL_H = 48         # power rail height
TAP_H = CT + 2*TAP_ENC_LICON  # 41

# ======================================================================
# Vertical coordinate calculation (bottom to top)
# ======================================================================
y = 0
Y_VSS_B = y; y += RAIL_H; Y_VSS_T = y; y += 12
Y_PTAP_B = y; y += TAP_H; Y_PTAP_T = y; y += TAP_SPACE

# M5 tail transistor
Y_TAIL_B = y; y += W200; Y_TAIL_T = y

# Gap between tail and diff pair
GAP_TAIL = 100
Y_GAP_TAIL_B = y; y += GAP_TAIL; Y_GAP_TAIL_T = y

# Row0: NMOS differential pair (M1, M2)
Y_R0N_B = y; y += W200; Y_R0N_T = y

# Gap between NMOS and PMOS
GAP01 = 130
Y_GAP0_B = y; y += GAP01; Y_GAP0_T = y

# Row1: PMOS current mirror (M3, M4)
Y_R1P_B = y; y += W200; Y_R1P_T = y; y += TAP_SPACE

# ntap + VDD rail
Y_NTAP_B = y; y += TAP_H; Y_NTAP_T = y; y += 12
Y_VDD_B = y; y += RAIL_H; Y_VDD_T = y

# Poly contact tracks
Y_GT_LO_B = Y_GAP_TAIL_B + POLYCONT_DIFF_SPACE
Y_GT_LO_T = Y_GT_LO_B + CT

Y_G0_LO_B = Y_GAP0_B + POLYCONT_DIFF_SPACE
Y_G0_LO_T = Y_G0_LO_B + CT
Y_G0_HI_T = Y_GAP0_T - POLYCONT_DIFF_SPACE
Y_G0_HI_B = Y_G0_HI_T - CT

# Verify poly spacing in gaps
for name, lo_t, hi_b in [("Gap0", Y_G0_LO_T, Y_G0_HI_B)]:
    lo_pad = lo_t + POLY_ENC_CT_1
    hi_pad = hi_b - POLY_ENC_CT_1
    assert hi_pad - lo_pad >= POLY_SPACE, f"{name} poly spacing {hi_pad-lo_pad} < {POLY_SPACE}"

# ======================================================================
# Horizontal coordinates: 2 columns + M5 centered
# ======================================================================
col_x = []
x = MARGIN
for _ in range(2):
    col_x.append(x)
    x += DW + COL_SP
CELL_W = x - COL_SP + MARGIN  # total cell width

# M5 center x
M5_CX = (col_x[0] + col_x[1] + DW) // 2
M5_X = M5_CX - DW // 2

# Nwell: covers PMOS row + ntap
NW_X0 = col_x[0] - NW_ENC
NW_X1 = col_x[1] + DW + NW_ENC
NW_Y0 = Y_R1P_B - NW_ENC
NW_Y1 = Y_NTAP_T + NW_ENC

print(f"Cell: {CELL_W} x {Y_VDD_T} lambda = {CELL_W*0.01:.2f} x {Y_VDD_T*0.01:.2f} um")

# ======================================================================
# TCL generation helpers
# ======================================================================
T = []
def emit(s): T.append(s)
def bp(x0, y0, x1, y1, layer):
    T.append(f"box {x0} {y0} {x1} {y1}")
    T.append(f"paint {layer}")

def contacts_in_sd(cx0, cy0, sd_w, diff_h, is_drain=False):
    c_x0 = cx0 + (GATE_CT_SPACE if is_drain else DIFF_ENC_CT)
    c_x1 = c_x0 + CT
    avail = diff_h - 2*6
    nc = max(1, (avail - CT) // CT_PITCH + 1)
    arr_h = (nc-1)*CT_PITCH + CT
    sy = cy0 + (diff_h - arr_h) // 2
    return [(c_x0, sy+i*CT_PITCH, c_x1, sy+i*CT_PITCH+CT) for i in range(nc)]

def paint_contacts(cts, layer):
    for c in cts: bp(c[0], c[1], c[2], c[3], layer)

def paint_li1_strip_y(cts):
    if not cts: return None
    x0, x1 = cts[0][0], cts[0][2]
    y0 = cts[0][1] - LI_ENC_CT; y1 = cts[-1][3] + LI_ENC_CT
    if (x1-x0)*(y1-y0) < LI_MIN_AREA:
        nh = (LI_MIN_AREA + (x1-x0) - 1) // (x1-x0)
        e = nh - (y1-y0)
        y0 -= e//2; y1 += (e+1)//2
    bp(x0, y0, x1, y1, "locali")
    return (x0, y0, x1, y1)

def paint_mcon(cts):
    for c in cts: bp(c[0], c[1], c[2], c[3], "viali")

def paint_via1(vx0, vy0):
    cx = vx0 + VIA_SIZE//2; cy = vy0 + VIA_SIZE//2
    v1x0 = cx - VIA1_MIN_W//2; v1y0 = cy - VIA1_MIN_W//2
    v1x1 = v1x0 + VIA1_MIN_W; v1y1 = v1y0 + VIA1_MIN_W
    bp(v1x0, v1y0, v1x1, v1y1, "via1")
    bp(v1x0, v1y0-VIA1_SURR, v1x1, v1y1+VIA1_SURR, "metal1")
    bp(v1x0, v1y0-VIA1_SURR, v1x1, v1y1+VIA1_SURR, "metal2")
    return (v1x0, v1y0, v1x1, v1y1)

def met1_on_contacts(cts):
    x0 = cts[0][0]-M1_ENC_MCON; x1 = cts[0][2]+M1_ENC_MCON
    y0 = cts[0][1]-M1_ENC_MCON_1; y1 = cts[-1][3]+M1_ENC_MCON_1
    if (x1-x0)*(y1-y0) < M1_MIN_AREA:
        nh = (M1_MIN_AREA + (x1-x0)-1)//(x1-x0)
        e = nh-(y1-y0)
        y0 -= e//2; y1 += (e+1)//2
    bp(x0, y0, x1, y1, "metal1")
    return (x0, y0, x1, y1)

def ensure_m1_area(x0, y0, x1, y1):
    if (x1-x0)*(y1-y0) < M1_MIN_AREA:
        nh = (M1_MIN_AREA + (x1-x0)-1)//(x1-x0)
        e = nh-(y1-y0)
        y0 -= e//2; y1 += (e+1)//2
    return x0, y0, x1, y1

pad_w = CT + 2*POLY_ENC_CT_1  # 33

def add_gate_contact(dev_name, track_y0, track_y1, extend_dir):
    d = DI[dev_name]
    gcx = d["gcx"]; gx0 = d["gx0"]; gx1 = d["gx1"]
    pcx0 = gcx - CT//2; pcx1 = pcx0 + CT
    px0 = gcx - pad_w//2; px1 = px0 + pad_w
    pad_y0 = track_y0 - POLY_ENC_CT_1; pad_y1 = track_y1 + POLY_ENC_CT_1
    if extend_dir == 'up':
        bp(gx0, d["yb"]-POLY_EXT, gx1, pad_y1, "poly")
    else:
        bp(gx0, pad_y0, gx1, d["yt"]+POLY_EXT, "poly")
    bp(px0, pad_y0, px1, pad_y1, "poly")
    bp(pcx0, track_y0, pcx1, track_y1, "polycont")
    li_y0 = track_y0; li_y1 = track_y1
    if (px1-px0)*(li_y1-li_y0) < LI_MIN_AREA:
        eh = (LI_MIN_AREA//(px1-px0)) - (li_y1-li_y0) + 2
        li_y0 -= eh//2; li_y1 += (eh+1)//2
    bp(px0, li_y0, px1, li_y1, "locali")
    bp(pcx0, track_y0, pcx1, track_y1, "viali")
    return pcx0, track_y0, pcx1, track_y1

def via1_on_m1(cts, at_top=True):
    m1 = met1_on_contacts(cts)
    vx = cts[0][0]
    vy = m1[3] - VIA_SIZE - M1_ENC_VIA_MIN if at_top else m1[1] + M1_ENC_VIA_MIN
    paint_via1(vx, vy)
    return vx, vy

# ======================================================================
# Header
# ======================================================================
emit("tech load /home/hsm/pdk_matched/share/pdk/sky130B/libs.tech/magic/sky130B.tech")
emit("drc style drc(full)")
emit("drc off")
emit("snap internal")
emit("cellname delete relu")
emit("edit")

# ======================================================================
# NWELL
# ======================================================================
emit("\n# === NWELL ===")
bp(NW_X0, NW_Y0, NW_X1, NW_Y1, "nwell")

# ======================================================================
# Transistor definitions
# ======================================================================
devices = {
    "M5": {"col": -1, "cx": M5_X, "type": "n", "yb": Y_TAIL_B, "w": W200,
           "gate": "VBIAS", "src": "VSS", "drn": "TAIL"},
    "M1": {"col": 0, "type": "n", "yb": Y_R0N_B, "w": W200,
           "gate": "VREF", "src": "TAIL", "drn": "node_A"},
    "M2": {"col": 1, "type": "n", "yb": Y_R0N_B, "w": W200,
           "gate": "VBL", "src": "TAIL", "drn": "OUT"},
    "M3": {"col": 0, "type": "p", "yb": Y_R1P_B, "w": W200,
           "gate": "node_A", "src": "VDD", "drn": "node_A"},
    "M4": {"col": 1, "type": "p", "yb": Y_R1P_B, "w": W200,
           "gate": "node_A", "src": "VDD", "drn": "OUT"},
}

DI = {}
for dn, d in devices.items():
    if d["col"] == -1:
        cx = d["cx"]
    else:
        cx = col_x[d["col"]]
    yb = d["yb"]; w = d["w"]
    dtype = "pdiff" if d["type"] == "p" else "ndiff"
    ctype = "pdiffc" if d["type"] == "p" else "ndiffc"
    emit(f"\n# === {dn} ({dtype} W={w*0.01:.1f}) ===")
    bp(cx, yb, cx+DW, yb+w, dtype)
    gx0 = cx+SD; gx1 = gx0+GL
    bp(gx0, yb-POLY_EXT, gx1, yb+w+POLY_EXT, "poly")
    drn_x0 = cx+SD+GL
    sc = contacts_in_sd(cx, yb, SD, w, False)
    dc = contacts_in_sd(drn_x0, yb, SD, w, True)
    paint_contacts(sc, ctype)
    paint_contacts(dc, ctype)
    sl = paint_li1_strip_y(sc)
    dl = paint_li1_strip_y(dc)
    DI[dn] = {"cx": cx, "gx0": gx0, "gx1": gx1, "gcx": (gx0+gx1)//2,
              "yb": yb, "yt": yb+w, "w": w, "sc": sc, "dc": dc, "sl": sl, "dl": dl, "d": d}

# ======================================================================
# Substrate taps
# ======================================================================
emit("\n# === TAPS ===")
# ptap: ONE continuous strip spanning full cell width (avoids contact spacing)
# Only place licon at Col0 and Col1 positions (M5 shares the continuous strip)
bp(0, Y_PTAP_B, CELL_W, Y_PTAP_T, "ptap")
ly0 = Y_PTAP_B+TAP_ENC_LICON; ly1 = ly0+CT
for ci in range(2):
    cx = col_x[ci]
    tx0 = cx+DIFF_ENC_CT; tx1 = tx0+CT
    tx2 = cx+DW-DIFF_ENC_CT-CT; tx3 = tx2+CT
    bp(tx0, ly0, tx1, ly1, "ptapc"); bp(tx2, ly0, tx3, ly1, "ptapc")
    bp(tx0, ly0-LI_ENC_CT, tx3, ly1+LI_ENC_CT, "locali")

# ntap: continuous strip within nwell bounds (nwell enclosure >= 18 lambda)
NTAP_X0 = col_x[0]; NTAP_X1 = col_x[1] + DW
bp(NTAP_X0, Y_NTAP_B, NTAP_X1, Y_NTAP_T, "ntap")
ny0 = Y_NTAP_B+TAP_ENC_LICON; ny1 = ny0+CT
for ci in range(2):
    cx = col_x[ci]
    tx0 = cx+DIFF_ENC_CT; tx1 = tx0+CT
    tx2 = cx+DW-DIFF_ENC_CT-CT; tx3 = tx2+CT
    bp(tx0, ny0, tx1, ny1, "ntapc"); bp(tx2, ny0, tx3, ny1, "ntapc")
    bp(tx0, ny0-LI_ENC_CT, tx3, ny1+LI_ENC_CT, "locali")

# ======================================================================
# Power rails (met1)
# ======================================================================
emit("\n# === POWER RAILS ===")
bp(0, Y_VSS_B, CELL_W, Y_VSS_T, "metal1")
bp(0, Y_VDD_B, CELL_W, Y_VDD_T, "metal1")

# ======================================================================
# VSS connections
# ======================================================================
emit("\n# === VSS ===")
# M5 source -> VSS
paint_mcon(DI["M5"]["sc"])
m5s_m1 = met1_on_contacts(DI["M5"]["sc"])
bp(m5s_m1[0], Y_VSS_T, m5s_m1[2], m5s_m1[1], "metal1")

# ptap -> VSS (only Col0 and Col1 positions)
ly0 = Y_PTAP_B+TAP_ENC_LICON; ly1 = ly0+CT
for ci in range(2):
    cx = col_x[ci]
    for tx in [cx+DIFF_ENC_CT, cx+DW-DIFF_ENC_CT-CT]:
        tx1 = tx+CT
        bp(tx, ly0, tx1, ly1, "viali")
        bp(tx-M1_ENC_MCON, Y_VSS_T, tx1+M1_ENC_MCON, ly1+M1_ENC_MCON_1, "metal1")

# ======================================================================
# VDD connections
# ======================================================================
emit("\n# === VDD ===")
ny0 = Y_NTAP_B+TAP_ENC_LICON; ny1 = ny0+CT
for ci in range(2):
    cx = col_x[ci]
    for tx in [cx+DIFF_ENC_CT, cx+DW-DIFF_ENC_CT-CT]:
        tx1 = tx+CT
        bp(tx, ny0, tx1, ny1, "viali")
        bp(tx-M1_ENC_MCON, ny0-M1_ENC_MCON_1, tx1+M1_ENC_MCON, Y_VDD_B, "metal1")

# M3/M4 source -> VDD (straight met1 bar through ntap)
for dn in ["M3", "M4"]:
    d = DI[dn]
    paint_mcon(d["sc"])
    m1 = met1_on_contacts(d["sc"])
    bp(m1[0], m1[3], m1[2], Y_VDD_B, "metal1")

# ======================================================================
# TAIL net: M1.src + M2.src + M5.drain (met2 horizontal)
# ======================================================================
emit("\n# === TAIL ===")
paint_mcon(DI["M1"]["sc"]); paint_mcon(DI["M2"]["sc"]); paint_mcon(DI["M5"]["dc"])
m1s_m1 = met1_on_contacts(DI["M1"]["sc"])
m2s_m1 = met1_on_contacts(DI["M2"]["sc"])
m5d_m1 = met1_on_contacts(DI["M5"]["dc"])

# Via1 at bottom of M1/M2 source met1 pads
vt_m1_x = DI["M1"]["sc"][0][0]; vt_m1_y = m1s_m1[1] + M1_ENC_VIA_MIN
vt_m2_x = DI["M2"]["sc"][0][0]; vt_m2_y = m2s_m1[1] + M1_ENC_VIA_MIN
# Via1 at top of M5 drain met1 pad
vt_m5_x = DI["M5"]["dc"][0][0]; vt_m5_y = m5d_m1[3] - VIA_SIZE - M1_ENC_VIA_MIN
paint_via1(vt_m1_x, vt_m1_y)
paint_via1(vt_m2_x, vt_m2_y)
paint_via1(vt_m5_x, vt_m5_y)

# Met2 horizontal bar
tail_all_x = sorted([vt_m1_x, vt_m2_x, vt_m5_x])
tail_m2_y0 = min(vt_m1_y, vt_m5_y) - M2_ENC_VIA
tail_m2_y1 = max(vt_m1_y, vt_m5_y) + VIA_SIZE + M2_ENC_VIA
bp(tail_all_x[0]-M2_ENC_VIA, tail_m2_y0,
   tail_all_x[-1]+VIA_SIZE+M2_ENC_VIA, tail_m2_y1, "metal2")

# ======================================================================
# node_A net: M3.drain + M1.drain + M3.gate + M4.gate (diode connected)
# ======================================================================
emit("\n# === node_A ===")
paint_mcon(DI["M3"]["dc"]); paint_mcon(DI["M1"]["dc"])
m3d_m1 = met1_on_contacts(DI["M3"]["dc"])
m1d_m1 = met1_on_contacts(DI["M1"]["dc"])

# Via1 on M1 drain (top of met1)
va_m1_x = DI["M1"]["dc"][0][0]; va_m1_y = m1d_m1[3] - VIA_SIZE - M1_ENC_VIA_MIN
paint_via1(va_m1_x, va_m1_y)
# Via1 on M3 drain (bottom of met1)
va_m3_x = DI["M3"]["dc"][0][0]; va_m3_y = m3d_m1[1] + M1_ENC_VIA_MIN
paint_via1(va_m3_x, va_m3_y)

# Met2 vertical spine: M1.drain -> M3.drain (same column)
na_m2_x0 = va_m1_x - M2_ENC_VIA; na_m2_x1 = va_m1_x + VIA_SIZE + M2_ENC_VIA
na_m2_y0 = va_m1_y - M2_ENC_VIA; na_m2_y1 = va_m3_y + VIA_SIZE + M2_ENC_VIA
bp(na_m2_x0, na_m2_y0, na_m2_x1, na_m2_y1, "metal2")

# M3 diode + M4 gate: connect both gates to node_A via met1 horizontal bar
# Route: M3.gate polycont -> met1 pad -> met1 horizontal bar -> M4.gate polycont
# Then connect M3.gate met1 to node_A met2 spine via via1

m3_pc = add_gate_contact("M3", Y_G0_HI_B, Y_G0_HI_T, 'down')
m4_pc = add_gate_contact("M4", Y_G0_HI_B, Y_G0_HI_T, 'down')

# Met1 horizontal bar connecting M3.gate and M4.gate pads
gate_bar_x0 = m3_pc[0] - M1_ENC_MCON
gate_bar_x1 = m4_pc[2] + M1_ENC_MCON
gate_bar_y0 = m3_pc[1] - M1_ENC_MCON_1
gate_bar_y1 = m3_pc[3] + M1_ENC_MCON_1
gate_bar_x0, gate_bar_y0, gate_bar_x1, gate_bar_y1 = ensure_m1_area(
    gate_bar_x0, gate_bar_y0, gate_bar_x1, gate_bar_y1)
bp(gate_bar_x0, gate_bar_y0, gate_bar_x1, gate_bar_y1, "metal1")

# Via1 on M3 gate side of met1 bar (connects to node_A met2 spine)
# Place via1 aligned with node_A spine x to avoid met2 spacing issues
m3g_vx = DI["M1"]["dc"][0][0]  # align with drain contact x (same as spine)
m3g_vy = gate_bar_y0 + M1_ENC_VIA_MIN
paint_via1(m3g_vx, m3g_vy)

# Extend met1 bar left to cover the via1 met1 pad
via1_m1_x0 = m3g_vx - M1_ENC_VIA
if via1_m1_x0 < gate_bar_x0:
    bp(via1_m1_x0, gate_bar_y0, gate_bar_x0, gate_bar_y1, "metal1")

# Extend node_A met2 spine down to M3 gate via1
na_m2_y0_ext = min(na_m2_y0, m3g_vy - M2_ENC_VIA)
bp(na_m2_x0, na_m2_y0_ext, na_m2_x1, na_m2_y1, "metal2")

# ======================================================================
# OUT net: M4.drain + M2.drain (met2 vertical spine at Col1)
# ======================================================================
emit("\n# === OUT ===")
paint_mcon(DI["M4"]["dc"]); paint_mcon(DI["M2"]["dc"])
m4d_m1 = met1_on_contacts(DI["M4"]["dc"])
m2d_m1 = met1_on_contacts(DI["M2"]["dc"])

# Via1 on M2 drain (top of met1)
vo_m2_x = DI["M2"]["dc"][0][0]; vo_m2_y = m2d_m1[3] - VIA_SIZE - M1_ENC_VIA_MIN
paint_via1(vo_m2_x, vo_m2_y)
# Via1 on M4 drain (bottom of met1)
vo_m4_x = DI["M4"]["dc"][0][0]; vo_m4_y = m4d_m1[1] + M1_ENC_VIA_MIN
paint_via1(vo_m4_x, vo_m4_y)

# Met2 vertical spine
out_m2_x0 = vo_m2_x - M2_ENC_VIA; out_m2_x1 = vo_m2_x + VIA_SIZE + M2_ENC_VIA
out_m2_y0 = vo_m2_y - M2_ENC_VIA; out_m2_y1 = vo_m4_y + VIA_SIZE + M2_ENC_VIA
bp(out_m2_x0, out_m2_y0, out_m2_x1, out_m2_y1, "metal2")

# ======================================================================
# VREF gate contact (M1.gate) in Gap0 lower track
# ======================================================================
emit("\n# === VREF ===")
m1_pc = add_gate_contact("M1", Y_G0_LO_B, Y_G0_LO_T, 'up')
vref_x0 = m1_pc[0]-M1_ENC_MCON_1; vref_x1 = m1_pc[2]+M1_ENC_MCON_1
vref_y0 = m1_pc[1]-M1_ENC_MCON; vref_y1 = m1_pc[3]+M1_ENC_MCON
vref_x0, vref_y0, vref_x1, vref_y1 = ensure_m1_area(vref_x0, vref_y0, vref_x1, vref_y1)
bp(vref_x0, vref_y0, vref_x1, vref_y1, "metal1")

# ======================================================================
# VBL gate contact (M2.gate) in Gap0 lower track
# ======================================================================
emit("\n# === VBL ===")
m2_pc = add_gate_contact("M2", Y_G0_LO_B, Y_G0_LO_T, 'up')
vbl_x0 = m2_pc[0]-M1_ENC_MCON_1; vbl_x1 = m2_pc[2]+M1_ENC_MCON_1
vbl_y0 = m2_pc[1]-M1_ENC_MCON; vbl_y1 = m2_pc[3]+M1_ENC_MCON
vbl_x0, vbl_y0, vbl_x1, vbl_y1 = ensure_m1_area(vbl_x0, vbl_y0, vbl_x1, vbl_y1)
bp(vbl_x0, vbl_y0, vbl_x1, vbl_y1, "metal1")

# ======================================================================
# VBIAS gate contact (M5.gate) in Gap_tail lower track
# ======================================================================
emit("\n# === VBIAS ===")
m5_pc = add_gate_contact("M5", Y_GT_LO_B, Y_GT_LO_T, 'up')
vbias_x0 = m5_pc[0]-M1_ENC_MCON_1; vbias_x1 = m5_pc[2]+M1_ENC_MCON_1
vbias_y0 = m5_pc[1]-M1_ENC_MCON; vbias_y1 = m5_pc[3]+M1_ENC_MCON
vbias_x0, vbias_y0, vbias_x1, vbias_y1 = ensure_m1_area(vbias_x0, vbias_y0, vbias_x1, vbias_y1)
bp(vbias_x0, vbias_y0, vbias_x1, vbias_y1, "metal1")

# ======================================================================
# Labels and ports
# ======================================================================
emit("\n# === LABELS & PORTS ===")
pin_defs = [
    ("VBL",   vbl_x0, vbl_y0, vbl_x1, vbl_y1, "metal1"),
    ("VREF",  vref_x0, vref_y0, vref_x1, vref_y1, "metal1"),
    ("OUT",   out_m2_x0, out_m2_y0, out_m2_x1, out_m2_y1, "metal2"),
    ("VBIAS", vbias_x0, vbias_y0, vbias_x1, vbias_y1, "metal1"),
    ("VDD",   0, Y_VDD_B, CELL_W, Y_VDD_T, "metal1"),
    ("VSS",   0, Y_VSS_B, CELL_W, Y_VSS_T, "metal1"),
]
for i, (pn, x0, y0, x1, y1, layer) in enumerate(pin_defs):
    T.append(f"box {x0} {y0} {x1} {y1}")
    T.append(f"label {pn} s {layer}")
    T.append(f"port make {i+1}")

# ======================================================================
# Save + DRC + Extract + GDS
# ======================================================================
emit("\n# === SAVE + DRC + EXTRACT ===")
emit("save relu")
emit("drc on"); emit("drc check"); emit("drc catchup")
emit("select top cell"); emit("drc why"); emit("drc count")
emit("extract all"); emit("ext2spice lvs"); emit("ext2spice")
emit("gds write relu.gds")
emit("quit -noprompt")

# Write TCL file
out_dir = "/home/hsm/rram_openlane/analog/layout/relu"
tcl_path = os.path.join(out_dir, "relu_gen.tcl")
with open(tcl_path, "w") as f:
    f.write("\n".join(T))
print(f"\nGenerated {tcl_path} ({len(T)} lines)")
print(f"Cell: {CELL_W} x {Y_VDD_T} lambda = {CELL_W*0.01:.2f} x {Y_VDD_T*0.01:.2f} um")
print(f"Pin coordinates (lambda):")
for pn, x0, y0, x1, y1, layer in pin_defs:
    print(f"  {pn:6s}: ({x0},{y0}) - ({x1},{y1}) on {layer}")
