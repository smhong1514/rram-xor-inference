#!/usr/bin/env python3
"""WL Driver 레이아웃 생성 스크립트 — Magic TCL 출력 (DRC-clean).

회로 (8T, 1.8V + 5V HV 혼합):
  Col0: XMP0(INB,IN,VDD,VDD)   pfet_01v8       W=1   입력 인버터 PMOS
        XMN0(INB,IN,VSS,VSS)   nfet_01v8       W=0.5 입력 인버터 NMOS
  Col1: XMP1(Q,QB,VWL,VWL)     pfet_g5v0d10v5  W=1   크로스커플 레벨시프터 P1
        XMN1(Q,IN,VSS,VSS)     nfet_g5v0d10v5  W=2   크로스커플 레벨시프터 N1
  Col2: XMP2(QB,Q,VWL,VWL)     pfet_g5v0d10v5  W=1   크로스커플 레벨시프터 P2
        XMN2(QB,INB,VSS,VSS)   nfet_g5v0d10v5  W=2   크로스커플 레벨시프터 N2
  Col3: XMP3(OUT,Q,VWL,VWL)    pfet_g5v0d10v5  W=4   HV 출력 버퍼 PMOS
        XMN3(OUT,Q,VSS,VSS)    nfet_g5v0d10v5  W=2   HV 출력 버퍼 NMOS

핵심: Col1/Col2는 SPLIT 게이트 (NFET과 PFET 게이트 신호가 다름),
     Col0/Col3는 UNIFIED 게이트 (N, P 동일 신호).

게이트 신호 배정:
  Col0: gate = IN  (N, P 공통)           — 입력 인버터
  Col1: N-gate = IN, P-gate = QB (split) — 레벨시프터 좌측
  Col2: N-gate = INB, P-gate = Q (split) — 레벨시프터 우측
  Col3: gate = Q  (N, P 공통)            — 출력 버퍼

레이아웃 구조 (아래→위):
  VSS rail ─ ptap ─ NFET행 ─ [갭: polycont + met2 라우팅] ─ PFET행 ─ ntap ─ VWL rail ─ VDD rail

라우팅 전략:
  - 게이트 polycont는 소스 쪽(게이트 왼편)에 배치 → 드레인 met1과 겹침 방지
  - 드레인 N↔P 연결: met1 수직 버스 (갭을 관통)
  - Split 게이트(Col1/2): polycont 2개 (PC_N=NFET 근처, PC_P=PFET 근처)
  - Unified 게이트(Col0/3): polycont 1개 (갭 중앙)
  - 컬럼 간 라우팅: met2 수평 배선 × 3 트랙
    Track 1: INB (Col0 드레인 → Col2 N-gate)
    Track 2: IN  (Col0 gate → Col1 N-gate) + Q (Col1 드레인 → Col2 P-gate → Col3 gate)
    Track 3: QB  (Col2 드레인 → Col1 P-gate)

특이사항:
  - Col0만 1.8V (ndiff/pdiff), Col1~3은 5V HV (mvndiff/mvpdiff)
  - nwell 2개 분리: LV nwell(Col0)과 HV nwell(Col1~3), 간격 ≥200λ (nwell.8 룰)
  - VDD rail은 Col0 위에만, VWL rail은 Col1~3 위에만 배치
"""
import os

# === DRC 상수 (단위: λ, 1λ = 0.01µm = 10nm) ===
# --- 게이트/SD 치수 ---
GL = 15; SD = 27; DW = SD + GL + SD            # 69λ (1.8V 디바이스 폭)
GL_HV = 50; SD_HV = 29; DW_HV = SD_HV + GL_HV + SD_HV  # 108λ (5V HV 디바이스 폭)
CT = 17; CT_PITCH = 36                          # 콘택트 크기 / 피치
# --- Poly 확장/간격 ---
POLY_EXT = 13; POLY_EXT_HV = 19                 # poly가 diff 밖으로 삐져나오는 길이
POLY_SPACE = 21; POLY_ENC_CT_1 = 8              # poly 간 간격, poly의 polycont 감싸기
# --- Diff/콘택트 감싸기 ---
DIFF_ENC_CT = 4; DIFF_ENC_CT_1 = 6; GATE_CT_SPACE = 6  # diff→콘택트, 게이트→드레인콘택트 간격
LI_ENC_CT = 8; LI_MIN_AREA = 561                # locali 감싸기, 최소 면적
# --- Metal1 ---
M1_WIDTH = 14; M1_SPACE = 14; M1_MIN_AREA = 830 # met1 폭/간격/최소면적
M1_ENC_MCON = 5; M1_ENC_MCON_1 = 6              # met1이 mcon 감싸는 여유
# --- Nwell ---
NW_ENC = 18; NW_ENC_HV = 33                     # nwell이 diff 감싸는 여유 (1.8V / 5V)
TAP_SPACE_HV = 37                                # diff/tap.15b: MV ndiff↔MV ptap 최소 간격
TAP_ENC_LICON = 12; TAP_H = CT + 2 * TAP_ENC_LICON  # 41λ (탭 높이)
# --- Via1 / Metal2 ---
VIA_SIZE = 15; M1_ENC_VIA = 6                    # via1 크기, met1 감싸기
M2_WIDTH = 14; M2_SPACE = 14; M2_MIN_AREA = 676; M2_ENC_VIA = 6  # met2 규칙
POLYCONT_DIFF_SPACE = 24                          # polycont↔diff 최소 간격
VIA1_MIN_W = 26; VIA1_SURR = 3                   # via1 최소폭, 방향성 서라운드
RAIL_H = 48; MARGIN = 15                          # 전원 레일 높이, 셀 여백

# --- 디바이스 채널폭 (λ) ---
# Col0(1.8V inv): N=0.5µm, P=1µm / Col1~2(LS): N=2µm, P=1µm / Col3(buf): N=2µm, P=4µm
col_wn = [50, 200, 200, 200]     # NFET 폭 [Col0, Col1, Col2, Col3]
col_wp = [100, 100, 100, 400]    # PFET 폭 [Col0, Col1, Col2, Col3]

# --- 컬럼 간격 ---
# Col0↔Col1: 260λ (nwell.8 룰: LV↔HV nwell 갭 ≥200λ 확보)
# Col1↔Col2, Col2↔Col3: 50λ (같은 HV nwell 내)
COL_SP_01 = 260; COL_SP_12 = 50; COL_SP_23 = 50
N_H = 200; P_H = 400; GAP = 300  # NFET행 높이, PFET행 높이, N↔P 갭 (라우팅 공간)

# --- 수직 좌표 (아래→위 적층) ---
# VSS rail → ptap → NFET행 → 갭(polycont+met2) → PFET행 → ntap → VWL rail → VDD rail
y = 0
Y_VSS_B = y; y += RAIL_H; Y_VSS_T = y; y += 12       # VSS 전원 레일 (맨 아래)
Y_PTAP_B = y; y += TAP_H; Y_PTAP_T = y; y += TAP_SPACE_HV  # p-substrate 탭 (VSS 연결)
Y_ND_B = y; y += N_H; Y_ND_T = y                       # NFET 행 (ndiff/mvndiff)
Y_GAP_B = y; y += GAP; Y_GAP_T = y                     # N↔P 갭 (polycont + met2 트랙)
Y_PD_B = y; y += P_H; Y_PD_T = y; y += TAP_SPACE_HV   # PFET 행 (pdiff/mvpdiff)
Y_NTAP_B = y; y += TAP_H; Y_NTAP_T = y; y += 12       # n-well 탭 (VDD/VWL 연결)
Y_VWL_B = y; y += RAIL_H; Y_VWL_T = y; y += 12         # VWL 전원 레일 (Col1~3 PFET용)
Y_VDD_B = y; y += RAIL_H; Y_VDD_T = y                   # VDD 전원 레일 (Col0 PFET용)

# --- Polycont 패드 치수 ---
PC_PAD_H = CT + 2 * POLY_ENC_CT_1  # 33λ (polycont + poly 감싸기)

# 갭 내 Polycont 2개 트랙 (split-gate 컬럼용):
# PC_N: NFET 근처 (갭 하단) — NFET 게이트 신호
# PC_P: PFET 근처 (갭 상단) — PFET 게이트 신호
Y_PCN_B = Y_GAP_B + POLYCONT_DIFF_SPACE; Y_PCN_T = Y_PCN_B + CT  # NFET polycont 위치
Y_PCP_T = Y_GAP_T - POLYCONT_DIFF_SPACE; Y_PCP_B = Y_PCP_T - CT  # PFET polycont 위치
# Poly 패드는 CT 바깥으로 POLY_ENC_CT_1 만큼 확장
Y_PCN_PAD_B = Y_PCN_B - POLY_ENC_CT_1; Y_PCN_PAD_T = Y_PCN_T + POLY_ENC_CT_1
Y_PCP_PAD_B = Y_PCP_B - POLY_ENC_CT_1; Y_PCP_PAD_T = Y_PCP_T + POLY_ENC_CT_1

# PC_N ↔ PC_P 사이 poly 간격 검증 (POLY_SPACE 이상 필요)
poly_gap = Y_PCP_PAD_B - Y_PCN_PAD_T
assert poly_gap >= POLY_SPACE, f"Poly gap {poly_gap} < {POLY_SPACE}!"

# --- Met2 트랙 배치 계획 ---
# PC_N ↔ PC_P 사이 공간에 met2 수평 트랙 3개를 중앙 정렬로 배치
# 트랙 높이: via1(26) + surround(2×3) + M2_ENC_VIA(2×6) = 44λ
M2_TRACK_H = VIA1_MIN_W + 2 * VIA1_SURR + 2 * M2_ENC_VIA  # 44λ/트랙
TRACK_PITCH = M2_TRACK_H + M2_SPACE  # 58λ (트랙 간 피치)
TRACK_BLOCK = 3 * M2_TRACK_H + 2 * M2_SPACE  # 160λ (3트랙 전체 높이)
MID_SPACE_B = Y_PCN_PAD_T  # 사용 가능 공간 하단 (PC_N poly 패드 상단)
MID_SPACE_T = Y_PCP_PAD_B  # 사용 가능 공간 상단 (PC_P poly 패드 하단)
MID_CENTER = (MID_SPACE_B + MID_SPACE_T) // 2  # 중앙점
t1_bot = MID_CENTER - TRACK_BLOCK // 2          # 트랙1 하단
t3_top_calc = t1_bot + TRACK_BLOCK              # 트랙3 상단
# 트랙이 PC_N↔PC_P 사이 공간에 들어가는지 검증
assert t1_bot >= MID_SPACE_B, f"Track 1 bottom {t1_bot} < PC_N pad top {MID_SPACE_B}"
assert t3_top_calc <= MID_SPACE_T, f"Track 3 top {t3_top_calc} > PC_P pad bottom {MID_SPACE_T}"

# 각 트랙의 Y 중심 좌표 (via1 배치 기준점)
t1_cy = t1_bot + M2_TRACK_H // 2   # Track 1: INB 신호
t2_cy = t1_cy + TRACK_PITCH         # Track 2: IN + Q 신호 (공유)
t3_cy = t2_cy + TRACK_PITCH         # Track 3: QB 신호

# --- 수평 좌표 ---
# 좌→우: MARGIN | Col0(LV) | 260λ간격 | Col1(HV) | Col2(HV) | Col3(HV) | MARGIN
x = MARGIN
COL0_X = x; x += DW + COL_SP_01       # Col0 시작 (1.8V 인버터)
COL1_X = x; x += DW_HV + COL_SP_12    # Col1 시작 (HV 레벨시프터 좌)
COL2_X = x; x += DW_HV + COL_SP_23    # Col2 시작 (HV 레벨시프터 우)
COL3_X = x; x += DW_HV + MARGIN       # Col3 시작 (HV 출력 버퍼)
CELL_W = x                              # 전체 셀 폭
col_x = [COL0_X, COL1_X, COL2_X, COL3_X]    # 각 컬럼 X 시작 좌표
col_dw = [DW, DW_HV, DW_HV, DW_HV]           # 각 컬럼 디바이스 폭
col_gl = [GL, GL_HV, GL_HV, GL_HV]            # 각 컬럼 게이트 길이
col_sd = [SD, SD_HV, SD_HV, SD_HV]            # 각 컬럼 S/D 영역 폭
col_hv = [False, True, True, True]             # HV 여부 (Col0만 1.8V)

# 게이트 구조 타입:
# "unified" = N과 P가 동일 게이트 신호 (Col0: IN, Col3: Q)
# "split" = N과 P가 다른 게이트 신호 (Col1: N=IN/P=QB, Col2: N=INB/P=Q)
col_gate_type = ["unified", "split", "split", "unified"]

# --- Nwell 영역 (2개 분리) ---
# LV nwell: Col0 PFET + ntap만 감싸기 (1.8V, NW_ENC=18λ)
LV_NW_X0 = COL0_X - NW_ENC; LV_NW_X1 = COL0_X + DW + NW_ENC
LV_NW_Y0 = Y_PD_B - NW_ENC; LV_NW_Y1 = Y_NTAP_T + NW_ENC
# HV nwell: Col1~3 PFET + ntap 감싸기 (5V, NW_ENC_HV=33λ)
HV_NW_X0 = COL1_X - NW_ENC_HV; HV_NW_X1 = COL3_X + DW_HV + NW_ENC_HV
HV_NW_Y0 = Y_PD_B - NW_ENC_HV; HV_NW_Y1 = Y_NTAP_T + NW_ENC_HV
# nwell.8 룰: LV↔HV nwell 간격 ≥200λ 검증
nw_gap = HV_NW_X0 - LV_NW_X1
assert nw_gap >= 200, f"Nwell gap {nw_gap} < 200!"

print(f"Cell: {CELL_W}x{Y_VDD_T}l = {CELL_W*0.01:.2f}x{Y_VDD_T*0.01:.2f}um, nw_gap={nw_gap}")
print(f"  GAP: {Y_GAP_B}..{Y_GAP_T} ({GAP}l)")
print(f"  PC_N: {Y_PCN_B}..{Y_PCN_T}, PC_P: {Y_PCP_B}..{Y_PCP_T}, poly gap: {poly_gap}")
print(f"  Met2 tracks: Y1_cy={t1_cy}, Y2_cy={t2_cy}, Y3_cy={t3_cy}")
print(f"  Mid space: {MID_SPACE_B}..{MID_SPACE_T}, tracks: {t1_bot}..{t3_top_calc}")

# === TCL 코드 생성 ===
T = []                                     # TCL 명령어 리스트
def emit(s): T.append(s)                   # TCL 명령어 추가
def bp(x0, y0, x1, y1, layer):             # box + paint 단축 함수
    emit(f"box {x0} {y0} {x1} {y1}"); emit(f"paint {layer}")

def contacts_in_sd(cx0, cy0, sd, dh, is_drain=False):
    """S/D 영역에 콘택트 배열 좌표를 계산하여 반환.
    is_drain=True이면 게이트→콘택트 간격(GATE_CT_SPACE) 적용."""
    c_x0 = cx0 + (GATE_CT_SPACE if is_drain else DIFF_ENC_CT); c_x1 = c_x0 + CT
    avail = dh - 2 * DIFF_ENC_CT_1; nc = max(1, (avail - CT) // CT_PITCH + 1)
    arr_h = (nc - 1) * CT_PITCH + CT; sy = cy0 + (dh - arr_h) // 2
    return [(c_x0, sy + i*CT_PITCH, c_x1, sy + i*CT_PITCH + CT) for i in range(nc)]

def paint_cts(cts, layer):
    """콘택트 배열을 지정 레이어(ndiffc/pdiffc 등)로 페인트."""
    for c in cts: bp(*c, layer)

def paint_li1(cts):
    """콘택트 배열 위에 locali 스트립 페인트 (최소 면적 보장)."""
    if not cts: return
    x0, x1 = cts[0][0], cts[0][2]
    y0, y1 = cts[0][1] - LI_ENC_CT, cts[-1][3] + LI_ENC_CT
    w, h = x1-x0, y1-y0
    if w*h < LI_MIN_AREA:
        nh = (LI_MIN_AREA+w-1)//w; e = nh-h; y0 -= e//2; y1 += (e+1)//2
    bp(x0, y0, x1, y1, "locali")

def paint_mcon(cts):
    """콘택트 위에 viali(mcon) 페인트 → met1 접근."""
    for c in cts: bp(*c, "viali")

def paint_via1(vx0, vy0):
    """via1 + met1/met2 감싸기를 (vx0,vy0) 코너에 페인트. 26×26 + surround."""
    vx1 = vx0 + VIA1_MIN_W; vy1 = vy0 + VIA1_MIN_W
    bp(vx0, vy0, vx1, vy1, "via1")
    bp(vx0, vy0 - VIA1_SURR, vx1 + VIA1_SURR, vy1 + VIA1_SURR, "metal1")
    bp(vx0, vy0 - VIA1_SURR, vx1 + VIA1_SURR, vy1 + VIA1_SURR, "metal2")
    return (vx0, vy0, vx1, vy1)

def m1_on_cts(cts, ey0=None, ey1=None):
    """콘택트 배열 위에 met1 사각형 페인트 (mcon 감싸기 + 최소 면적 보장)."""
    x0 = cts[0][0]-M1_ENC_MCON; x1 = cts[0][2]+M1_ENC_MCON
    y0 = cts[0][1]-M1_ENC_MCON_1; y1 = cts[-1][3]+M1_ENC_MCON_1
    if ey0 is not None: y0 = min(y0, ey0)
    if ey1 is not None: y1 = max(y1, ey1)
    w, h = x1-x0, y1-y0
    if w*h < M1_MIN_AREA:
        nh = (M1_MIN_AREA+w-1)//w; e = nh-h; y0 -= e//2; y1 += (e+1)//2
    bp(x0, y0, x1, y1, "metal1"); return (x0, y0, x1, y1)

def ensure_m1_area(x0, y0, x1, y1):
    """met1 사각형이 최소 면적(M1_MIN_AREA)을 만족하도록 Y 방향 확장."""
    w, h = x1-x0, y1-y0
    if w*h < M1_MIN_AREA:
        nh = (M1_MIN_AREA+w-1)//w; e = nh-h; y0 -= e//2; y1 += (e+1)//2
    return x0, y0, x1, y1

pw = CT + 2 * POLY_ENC_CT_1  # 33λ (polycont poly 패드 폭)

# === TCL 헤더: 기술 파일 로드 + 셀 초기화 ===
emit("tech load $PDK_ROOT/sky130B/libs.tech/magic/sky130B.tech")
emit("drc style drc(full)"); emit("drc off"); emit("snap internal")
emit("cellname delete wl_driver"); emit("edit")

# === Nwell 2개 (LV + HV 분리) ===
emit("\n# === NWELL ===")
bp(LV_NW_X0, LV_NW_Y0, LV_NW_X1, LV_NW_Y1, "nwell")  # LV nwell (Col0)
bp(HV_NW_X0, HV_NW_Y0, HV_NW_X1, HV_NW_Y1, "nwell")   # HV nwell (Col1~3)

# === 디바이스 생성 (4컬럼 루프) ===
cd = []  # 각 컬럼의 좌표/콘택트 정보 저장 (나중에 라우팅에서 참조)
for ci in range(4):
    cx = col_x[ci]; dw = col_dw[ci]; gl = col_gl[ci]; sd_ = col_sd[ci]
    hv = col_hv[ci]; wn = col_wn[ci]; wp = col_wp[ci]
    pe = POLY_EXT_HV if hv else POLY_EXT  # poly 확장 길이
    # HV 여부에 따라 Magic 레이어 이름 선택 (mv 접두사 = 5V MV 디바이스)
    nl = "mvndiff" if hv else "ndiff"; pl = "mvpdiff" if hv else "pdiff"
    ncl = "mvndiffc" if hv else "ndiffc"; pcl_ = "mvpdiffc" if hv else "pdiffc"
    nml = "mvnmos" if hv else "nmos"; pml = "mvpmos" if hv else "pmos"

    emit(f"\n# === Col{ci} devices ===")
    # 각 행 내에서 디바이스를 수직 중앙 정렬
    nd0 = Y_ND_B + (N_H-wn)//2; nd1 = nd0+wn  # NFET diff 상하단
    pd0 = Y_PD_B + (P_H-wp)//2; pd1 = pd0+wp   # PFET diff 상하단
    gx0 = cx+sd_; gx1 = gx0+gl                   # 게이트 poly 좌우 경계
    src_cx = cx + sd_//2  # 소스 S/D 영역 중심 (polycont 배치 기준)

    # Diff + Gate 영역 페인트 (diff 위에 nmos/pmos 오버페인트)
    bp(cx, nd0, cx+dw, nd1, nl); bp(gx0, nd0, gx1, nd1, nml)
    bp(cx, pd0, cx+dw, pd1, pl); bp(gx0, pd0, gx1, pd1, pml)

    # --- Poly + Polycont 생성 ---
    if col_gate_type[ci] == "unified":
        # Unified: NFET~PFET 연속 poly (동일 신호이므로 하나로 연결)
        bp(gx0, nd0-pe, gx1, pd1+pe, "poly")
        # 갭 중앙에 polycont 1개 배치
        pc_b = (Y_PCN_B + Y_PCP_B) // 2; pc_t = pc_b + CT
        pcx0 = src_cx - CT//2; pcx1 = pcx0 + CT       # polycont 좌표
        ppx0 = src_cx - pw//2; ppx1 = ppx0 + pw        # poly 패드 좌표
        bp(ppx0, pc_b-POLY_ENC_CT_1, ppx1, pc_t+POLY_ENC_CT_1, "poly")  # 패드
        bp(ppx0, pc_b-POLY_ENC_CT_1, gx1, pc_t+POLY_ENC_CT_1, "poly")   # 게이트 poly로 연결
        bp(pcx0, pc_b, pcx1, pc_t, "polycont")
        # locali (최소 면적 보장)
        ly0, ly1 = pc_b, pc_t
        if pw*(ly1-ly0) < LI_MIN_AREA:
            e = (LI_MIN_AREA//pw)-(ly1-ly0)+2; ly0 -= e//2; ly1 += (e+1)//2
        bp(ppx0, ly0, ppx1, ly1, "locali")
        gate_info = {"type": "unified", "pcx0": pcx0, "pcx1": pcx1,
                     "ppx0": ppx0, "ppx1": ppx1, "pc_b": pc_b, "pc_t": pc_t}
    else:
        # Split: NFET와 PFET poly를 분리 (다른 게이트 신호)
        bp(gx0, nd0-pe, gx1, Y_PCN_PAD_T, "poly")     # NFET poly (아래~PC_N)
        bp(gx0, Y_PCP_PAD_B, gx1, pd1+pe, "poly")      # PFET poly (PC_P~위)

        # NFET polycont: PC_N 위치 (갭 하단, NFET 게이트 신호)
        pcx0_n = src_cx - CT//2; pcx1_n = pcx0_n + CT
        ppx0_n = src_cx - pw//2; ppx1_n = ppx0_n + pw
        bp(ppx0_n, Y_PCN_PAD_B, ppx1_n, Y_PCN_PAD_T, "poly")      # 패드
        bp(ppx0_n, Y_PCN_PAD_B, gx1, Y_PCN_PAD_T, "poly")          # 게이트 poly로 연결
        bp(pcx0_n, Y_PCN_B, pcx1_n, Y_PCN_T, "polycont")
        ly0, ly1 = Y_PCN_B, Y_PCN_T
        if pw*(ly1-ly0) < LI_MIN_AREA:
            e = (LI_MIN_AREA//pw)-(ly1-ly0)+2; ly0 -= e//2; ly1 += (e+1)//2
        bp(ppx0_n, ly0, ppx1_n, ly1, "locali")

        # PFET polycont: PC_P 위치 (갭 상단, PFET 게이트 신호)
        pcx0_p = src_cx - CT//2; pcx1_p = pcx0_p + CT
        ppx0_p = src_cx - pw//2; ppx1_p = ppx0_p + pw
        bp(ppx0_p, Y_PCP_PAD_B, ppx1_p, Y_PCP_PAD_T, "poly")      # 패드
        bp(ppx0_p, Y_PCP_PAD_B, gx1, Y_PCP_PAD_T, "poly")          # 게이트 poly로 연결
        bp(pcx0_p, Y_PCP_B, pcx1_p, Y_PCP_T, "polycont")
        ly0, ly1 = Y_PCP_B, Y_PCP_T
        if pw*(ly1-ly0) < LI_MIN_AREA:
            e = (LI_MIN_AREA//pw)-(ly1-ly0)+2; ly0 -= e//2; ly1 += (e+1)//2
        bp(ppx0_p, ly0, ppx1_p, ly1, "locali")

        gate_info = {"type": "split",
                     "n_pcx0": pcx0_n, "n_pcx1": pcx1_n, "n_ppx0": ppx0_n, "n_ppx1": ppx1_n,
                     "n_pc_b": Y_PCN_B, "n_pc_t": Y_PCN_T,
                     "p_pcx0": pcx0_p, "p_pcx1": pcx1_p, "p_ppx0": ppx0_p, "p_ppx1": ppx1_p,
                     "p_pc_b": Y_PCP_B, "p_pc_t": Y_PCP_T}

    # --- S/D 콘택트 배열 생성 ---
    dx0 = cx+sd_+gl  # 드레인 S/D 영역 X 시작
    sn = contacts_in_sd(cx, nd0, sd_, wn)              # NFET 소스 콘택트
    dn = contacts_in_sd(dx0, nd0, sd_, wn, True)       # NFET 드레인 콘택트
    sp = contacts_in_sd(cx, pd0, sd_, wp)              # PFET 소스 콘택트
    dp = contacts_in_sd(dx0, pd0, sd_, wp, True)       # PFET 드레인 콘택트
    paint_cts(sn, ncl); paint_cts(dn, ncl)             # N-diff 콘택트 페인트
    paint_cts(sp, pcl_); paint_cts(dp, pcl_)           # P-diff 콘택트 페인트
    paint_li1(sn); paint_li1(dn); paint_li1(sp); paint_li1(dp)  # locali 스트립

    # 이 컬럼의 좌표 정보 저장 (라우팅 단계에서 사용)
    cd.append({"nd0":nd0,"nd1":nd1,"pd0":pd0,"pd1":pd1,"gx0":gx0,"gx1":gx1,
               "sn":sn,"dn":dn,"sp":sp,"dp":dp,"wn":wn,"wp":wp,
               "src_cx":src_cx,"gate":gate_info})

# === 기판 탭 (ptap: VSS 연결, ntap: VDD/VWL 연결) ===
emit("\n# === TAPS ===")
for ci in range(4):
    cx = col_x[ci]; dw = col_dw[ci]; hv = col_hv[ci]
    # HV 여부에 따라 탭 레이어 이름 선택 (mv 접두사 = 5V)
    ptl = "mvptapc" if hv else "ptapc"; ntl = "mvntapc" if hv else "ntapc"
    ptd = "mvptap" if hv else "ptap"; ntd = "mvntap" if hv else "ntap"
    # p-substrate 탭 (NFET 아래, VSS 연결): 콘택트 2개 + diff + locali
    ly0 = Y_PTAP_B+TAP_ENC_LICON; ly1 = ly0+CT
    t0 = cx+DIFF_ENC_CT; t1 = t0+CT; t2 = cx+dw-DIFF_ENC_CT-CT; t3 = t2+CT
    bp(t0, ly0, t1, ly1, ptl); bp(t2, ly0, t3, ly1, ptl)
    bp(cx, Y_PTAP_B, cx+dw, Y_PTAP_T, ptd)
    bp(t0, ly0-LI_ENC_CT, t3, ly1+LI_ENC_CT, "locali")
    # n-well 탭 (PFET 위, VDD/VWL 연결): 콘택트 2개 + diff + locali
    ny0 = Y_NTAP_B+TAP_ENC_LICON; ny1 = ny0+CT
    bp(t0, ny0, t1, ny1, ntl); bp(t2, ny0, t3, ny1, ntl)
    bp(cx, Y_NTAP_B, cx+dw, Y_NTAP_T, ntd)
    bp(t0, ny0-LI_ENC_CT, t3, ny1+LI_ENC_CT, "locali")

# === 전원 레일 (met1) ===
emit("\n# === POWER ===")
bp(0, Y_VSS_B, CELL_W, Y_VSS_T, "metal1")                              # VSS (전체 폭)
bp(COL1_X-MARGIN, Y_VWL_B, COL3_X+DW_HV+MARGIN, Y_VWL_T, "metal1")    # VWL (Col1~3만)
bp(COL0_X-MARGIN, Y_VDD_B, COL0_X+DW+MARGIN, Y_VDD_T, "metal1")        # VDD (Col0만)

# --- NFET 소스 → VSS 연결 ---
# 각 컬럼의 NFET 소스 콘택트 → mcon → met1 → VSS 레일
emit("\n# === SRC -> VSS ===")
for ci in range(4):
    col = cd[ci]; cx = col_x[ci]; dw = col_dw[ci]
    paint_mcon(col["sn"])  # NFET 소스 mcon
    x0 = col["sn"][0][0]-M1_ENC_MCON; x1 = col["sn"][0][2]+M1_ENC_MCON
    bp(x0, Y_VSS_T, x1, col["sn"][-1][3]+M1_ENC_MCON_1, "metal1")  # met1 수직 연결
    # ptap 콘택트도 mcon → met1로 VSS 레일에 연결
    ly0 = Y_PTAP_B+TAP_ENC_LICON; ly1 = ly0+CT
    t0 = cx+DIFF_ENC_CT; t1 = t0+CT; t2 = cx+dw-DIFF_ENC_CT-CT; t3 = t2+CT
    bp(t0, ly0, t1, ly1, "viali"); bp(t0-M1_ENC_MCON, Y_VSS_T, t1+M1_ENC_MCON, ly1+M1_ENC_MCON_1, "metal1")
    bp(t2, ly0, t3, ly1, "viali"); bp(t2-M1_ENC_MCON, Y_VSS_T, t3+M1_ENC_MCON, ly1+M1_ENC_MCON_1, "metal1")

# --- PFET 소스 → VDD/VWL 연결 ---
# Col0: VDD 레일로, Col1~3: VWL 레일로 연결
emit("\n# === SRC -> VDD/VWL ===")
for ci in range(4):
    col = cd[ci]; cx = col_x[ci]; dw = col_dw[ci]
    rb = Y_VDD_B if ci == 0 else Y_VWL_B  # Col0→VDD, Col1~3→VWL
    paint_mcon(col["sp"])  # PFET 소스 mcon
    x0 = col["sp"][0][0]-M1_ENC_MCON; x1 = col["sp"][0][2]+M1_ENC_MCON
    bp(x0, col["sp"][0][1]-M1_ENC_MCON_1, x1, rb, "metal1")  # met1 수직 연결
    # ntap 콘택트도 mcon → met1로 VDD/VWL 레일에 연결
    ny0 = Y_NTAP_B+TAP_ENC_LICON; ny1 = ny0+CT
    t0 = cx+DIFF_ENC_CT; t1 = t0+CT; t2 = cx+dw-DIFF_ENC_CT-CT; t3 = t2+CT
    bp(t0, ny0, t1, ny1, "viali"); bp(t0-M1_ENC_MCON, ny0-M1_ENC_MCON_1, t1+M1_ENC_MCON, rb, "metal1")
    bp(t2, ny0, t3, ny1, "viali"); bp(t2-M1_ENC_MCON, ny0-M1_ENC_MCON_1, t3+M1_ENC_MCON, rb, "metal1")

# === 드레인 met1 수직 버스 (갭을 관통하여 N↔P 드레인 연결) ===
# 각 컬럼의 NFET 드레인과 PFET 드레인을 met1으로 수직 연결 (동일 넷)
emit("\n# === DRAIN MET1 BUSES ===")
drn_bus = []  # 각 컬럼의 드레인 버스 좌표 저장
for ci in range(4):
    col = cd[ci]
    emit(f"# Col{ci} drain met1 bus")
    paint_mcon(col["dn"]); paint_mcon(col["dp"])  # N/P 드레인 mcon
    n_m1 = m1_on_cts(col["dn"])   # NFET 드레인 met1
    p_m1 = m1_on_cts(col["dp"])   # PFET 드레인 met1
    # 두 met1 패드를 수직으로 연결하는 버스
    bx0 = min(n_m1[0], p_m1[0]); bx1 = max(n_m1[2], p_m1[2])
    bp(bx0, n_m1[1], bx1, p_m1[3], "metal1")
    drn_bus.append((bx0, n_m1[1], bx1, p_m1[3]))

# === 게이트 mcon + met1 패드 ===
# 각 polycont에 viali(mcon) + met1 패드를 추가하여 met2 라우팅과 연결 준비.
# Unified 컬럼: 패드 1개 (key: "u")
# Split 컬럼: 패드 2개 (key: "n" = NFET용, "p" = PFET용)
emit("\n# === GATE MET1 PADS ===")
gate_pads = {}  # key: (컬럼번호, "n"/"p"/"u") → (m1_x0, m1_y0, m1_x1, m1_y1)

for ci in range(4):
    col = cd[ci]; gi = col["gate"]
    if gi["type"] == "unified":
        # Single mcon + met1 pad
        bp(gi["pcx0"], gi["pc_b"], gi["pcx1"], gi["pc_t"], "viali")
        gm = ensure_m1_area(gi["ppx0"]-M1_ENC_MCON_1+POLY_ENC_CT_1, gi["pc_b"]-M1_ENC_MCON,
                             gi["ppx1"]+M1_ENC_MCON_1-POLY_ENC_CT_1, gi["pc_t"]+M1_ENC_MCON)
        # Actually, met1 pad should enclose the mcon:
        gm = ensure_m1_area(gi["pcx0"]-M1_ENC_MCON_1, gi["pc_b"]-M1_ENC_MCON,
                             gi["pcx1"]+M1_ENC_MCON_1, gi["pc_t"]+M1_ENC_MCON)
        bp(*gm, "metal1")
        gate_pads[(ci, "u")] = gm
    else:
        # NFET gate mcon + met1 pad
        bp(gi["n_pcx0"], gi["n_pc_b"], gi["n_pcx1"], gi["n_pc_t"], "viali")
        gm_n = ensure_m1_area(gi["n_pcx0"]-M1_ENC_MCON_1, gi["n_pc_b"]-M1_ENC_MCON,
                               gi["n_pcx1"]+M1_ENC_MCON_1, gi["n_pc_t"]+M1_ENC_MCON)
        bp(*gm_n, "metal1")
        gate_pads[(ci, "n")] = gm_n
        # PFET gate mcon + met1 pad
        bp(gi["p_pcx0"], gi["p_pc_b"], gi["p_pcx1"], gi["p_pc_t"], "viali")
        gm_p = ensure_m1_area(gi["p_pcx0"]-M1_ENC_MCON_1, gi["p_pc_b"]-M1_ENC_MCON,
                               gi["p_pcx1"]+M1_ENC_MCON_1, gi["p_pc_t"]+M1_ENC_MCON)
        bp(*gm_p, "metal1")
        gate_pads[(ci, "p")] = gm_p

# 게이트 met1 패드 ↔ 드레인 met1 버스 간 X 간격 검증 (M1_SPACE 이상 필요)
for ci in range(4):
    db = drn_bus[ci]
    if col_gate_type[ci] == "unified":
        gm = gate_pads[(ci, "u")]
        gap_x = db[0] - gm[2]
        print(f"  Col{ci} unified: gate_right={gm[2]}, drain_left={db[0]}, gap={gap_x}")
        assert gap_x >= M1_SPACE, f"Col{ci}: gate-drain met1 gap {gap_x} < {M1_SPACE}!"
    else:
        for sub in ["n", "p"]:
            gm = gate_pads[(ci, sub)]
            gap_x = db[0] - gm[2]
            print(f"  Col{ci} {sub}: gate_right={gm[2]}, drain_left={db[0]}, gap={gap_x}")
            assert gap_x >= M1_SPACE, f"Col{ci} {sub}: gate-drain met1 gap {gap_x} < {M1_SPACE}!"

# === 게이트 라우팅 (met2 수평 배선 + via1, 3트랙) ===
# 컬럼 간 게이트 신호를 met2 수평 배선으로 연결.
# via1로 met1(게이트 패드 / 드레인 버스) ↔ met2 트랙 전환.
emit("\n# === GATE ROUTING (met2) ===")

# 신호 라우팅 계획 (Col2에서 met1 strap 교차 방지를 위해 수정된 버전):
#   Track 1 (Y1, 하단): INB (Col0 드레인 → Col2 N-gate)
#   Track 2 (Y2, 중앙): IN  (Col0 gate → Col1 N-gate) + Q (Col1 드레인 → Col2 P-gate → Col3 gate)
#   Track 3 (Y3, 상단): QB  (Col2 드레인 → Col1 P-gate)
#
# 핵심: Split-gate 컬럼에서 N-gate polycont(PCN)은 아래쪽, P-gate polycont(PCP)은 위쪽.
# met1 strap 교차를 피하려면:
#   - N-gate 신호는 낮은 트랙으로 (Track 1 또는 2)
#   - P-gate 신호는 높은 트랙으로 (Track 2 또는 3)
#
# Col1: N-gate(IN)→Track2, P-gate(QB)→Track3 → strap 간격 OK
# Col2: N-gate(INB)→Track1, P-gate(Q)→Track2 → strap 간격 OK
# Track 2 공유: IN(Col0~Col1 구간) + Q(Col1~Col3 구간) → X 간격 OK

def place_gate_via1(pad_key, track_cy, label=""):
    """게이트 met1 패드 위에 via1 배치. met1을 트랙 Y까지 확장하여 연결."""
    gm = gate_pads[pad_key]
    vx0 = gm[0]
    vy0 = track_cy - VIA1_MIN_W // 2
    emit(f"# {label}: via1 on {pad_key}")
    v = paint_via1(vx0, vy0)
    # met1을 mcon 패드~via1까지 수직 확장 (strap)
    m1_y0 = min(gm[1], vy0 - VIA1_SURR)
    m1_y1 = max(gm[3], vy0 + VIA1_MIN_W + VIA1_SURR)
    m1_x1 = max(gm[2], vx0 + VIA1_MIN_W + VIA1_SURR)
    bp(gm[0], m1_y0, m1_x1, m1_y1, "metal1")
    # met2 배선의 X 범위 반환 (수평 met2 연결 시 사용)
    m2_x0 = vx0 - M2_ENC_VIA
    m2_x1 = vx0 + VIA1_MIN_W + VIA1_SURR + M2_ENC_VIA
    return (vx0, vy0, m2_x0, m2_x1)

def place_drain_via1(ci, track_cy, label=""):
    """드레인 met1 버스 위에 via1 배치. 트랙 Y 높이에서 met2로 전환."""
    db = drn_bus[ci]
    dcx = (db[0] + db[2]) // 2      # 드레인 버스 X 중심
    vx0 = dcx - VIA1_MIN_W // 2
    vy0 = track_cy - VIA1_MIN_W // 2
    emit(f"# {label}: via1 on Col{ci} drain")
    v = paint_via1(vx0, vy0)
    # 드레인 버스 met1을 via1까지 확장 (이미 수직으로 길지만 via surround 보장)
    bp(min(db[0], vx0), min(db[1], vy0-VIA1_SURR),
       max(db[2], vx0+VIA1_MIN_W+VIA1_SURR), db[3], "metal1")
    m2_x0 = vx0 - M2_ENC_VIA
    m2_x1 = vx0 + VIA1_MIN_W + VIA1_SURR + M2_ENC_VIA
    return (vx0, vy0, m2_x0, m2_x1)

# --- Track 1 (Y1): INB 신호 ---
# Col0 드레인(INB) → met2 수평 → Col2 N-gate(INB)
emit("# Track Y1: INB")
inb_src = place_drain_via1(0, t1_cy, "INB src Col0-drain")    # 시작: Col0 드레인
inb_dst = place_gate_via1((2, "n"), t1_cy, "INB dst Col2-N")  # 끝: Col2 N-gate
t1_vy0 = t1_cy - VIA1_MIN_W // 2
inb_m2_y0 = t1_vy0 - VIA1_SURR - M2_ENC_VIA
inb_m2_y1 = t1_vy0 + VIA1_MIN_W + VIA1_SURR + M2_ENC_VIA
bp(inb_src[2], inb_m2_y0, inb_dst[3], inb_m2_y1, "metal2")   # met2 수평 배선

# --- Track 2 (Y2): IN + Q 공유 트랙 ---
# IN: Col0 gate(IN) → met2 → Col1 N-gate(IN)
emit("# Track Y2: IN + Q")
in_src = place_gate_via1((0, "u"), t2_cy, "IN src Col0")      # IN 시작: Col0 gate
in_dst = place_gate_via1((1, "n"), t2_cy, "IN dst Col1-N")    # IN 끝: Col1 N-gate
in_m2_x0 = in_src[2]; in_m2_x1 = in_dst[3]
t2_vy0 = t2_cy - VIA1_MIN_W // 2
in_m2_y0 = t2_vy0 - VIA1_SURR - M2_ENC_VIA
in_m2_y1 = t2_vy0 + VIA1_MIN_W + VIA1_SURR + M2_ENC_VIA
bp(in_m2_x0, in_m2_y0, in_m2_x1, in_m2_y1, "metal2")         # IN met2 배선

# Q: Col1 드레인(Q) → Col2 P-gate(Q) → Col3 gate(Q)
q_src = place_drain_via1(1, t2_cy, "Q src Col1-drain")        # Q 시작: Col1 드레인
q_mid = place_gate_via1((2, "p"), t2_cy, "Q mid Col2-P")      # Q 중간: Col2 P-gate
q_dst = place_gate_via1((3, "u"), t2_cy, "Q dst Col3")        # Q 끝: Col3 gate
q_m2_x0 = q_src[2]; q_m2_x1 = q_dst[3]
bp(q_m2_x0, in_m2_y0, q_m2_x1, in_m2_y1, "metal2")           # Q met2 배선

# Track 2에서 IN↔Q met2 X 간격 검증 (같은 Y에 2개 배선이므로 X 간격 필요)
in_q_gap = q_m2_x0 - in_m2_x1
print(f"  IN-Q met2 x-gap on Track 2: {in_q_gap} (min {M2_SPACE})")
assert in_q_gap >= M2_SPACE, f"IN-Q met2 gap {in_q_gap} < {M2_SPACE}!"

# --- Track 3 (Y3): QB 신호 ---
# Col2 드레인(QB) → met2 수평 → Col1 P-gate(QB)
emit("# Track Y3: QB")
qb_src = place_drain_via1(2, t3_cy, "QB src Col2-drain")      # 시작: Col2 드레인
qb_dst = place_gate_via1((1, "p"), t3_cy, "QB dst Col1-P")    # 끝: Col1 P-gate
t3_vy0 = t3_cy - VIA1_MIN_W // 2
qb_m2_y0 = t3_vy0 - VIA1_SURR - M2_ENC_VIA
qb_m2_y1 = t3_vy0 + VIA1_MIN_W + VIA1_SURR + M2_ENC_VIA
# QB는 Col1 P-gate ← Col2 드레인 방향 (역방향이므로 min/max로 범위 결정)
qb_m2_x0 = min(qb_src[2], qb_dst[2])
qb_m2_x1 = max(qb_src[3], qb_dst[3])
bp(qb_m2_x0, qb_m2_y0, qb_m2_x1, qb_m2_y1, "metal2")        # QB met2 배선

# === DRC 검증: met2 트랙 간 Y 간격 ===
for a_y1, b_y0, na, nb in [(inb_m2_y1, in_m2_y0, "Y1", "Y2"),
                             (in_m2_y1, qb_m2_y0, "Y2", "Y3")]:
    gap_y = b_y0 - a_y1
    print(f"  {na}-{nb} met2 y-gap: {gap_y} (min {M2_SPACE})")
    assert gap_y >= M2_SPACE, f"{na}-{nb} met2 y-gap {gap_y} < {M2_SPACE}!"

# === DRC 검증: Split-gate 컬럼에서 met1 strap 간 Y 간격 ===
# Col1: N-gate strap(→Track2) ↔ P-gate strap(→Track3) 간격
col1_n_pad = gate_pads[(1, "n")]
col1_p_pad = gate_pads[(1, "p")]
col1_n_strap_y1 = max(col1_n_pad[3], t2_cy - VIA1_MIN_W//2 + VIA1_MIN_W + VIA1_SURR)
col1_p_strap_y0 = min(col1_p_pad[1], t3_cy - VIA1_MIN_W//2 - VIA1_SURR)
col1_strap_gap = col1_p_strap_y0 - col1_n_strap_y1
print(f"  Col1 met1 strap y-gap: {col1_strap_gap} (min {M1_SPACE})")
assert col1_strap_gap >= M1_SPACE, f"Col1 strap gap {col1_strap_gap} < {M1_SPACE}!"

# Col2: N-gate strap(→Track1) ↔ P-gate strap(→Track2) 간격
col2_n_pad = gate_pads[(2, "n")]
col2_p_pad = gate_pads[(2, "p")]
col2_n_strap_y1 = max(col2_n_pad[3], t1_cy - VIA1_MIN_W//2 + VIA1_MIN_W + VIA1_SURR)
col2_p_strap_y0 = min(col2_p_pad[1], t2_cy - VIA1_MIN_W//2 - VIA1_SURR)
col2_strap_gap = col2_p_strap_y0 - col2_n_strap_y1
print(f"  Col2 met1 strap y-gap: {col2_strap_gap} (min {M1_SPACE})")
assert col2_strap_gap >= M1_SPACE, f"Col2 strap gap {col2_strap_gap} < {M1_SPACE}!"

# === 라벨 & 포트 (LVS 추출용) ===
# Magic에서 SPICE 추출 시 포트 이름으로 사용됨 (label + port make)
emit("\n# === LABELS ===")
in_pad = gate_pads[(0, "u")]     # IN: Col0 게이트 met1 패드 위
out_bus = drn_bus[3]              # OUT: Col3 드레인 met1 버스 위
pins = [
    ("IN",  *in_pad, "metal1"),   # 입력 신호 (1.8V 디지털)
    ("OUT", *out_bus, "metal1"),   # 출력 신호 (고전압 VWL 레벨)
    ("VDD", COL0_X-MARGIN, Y_VDD_B, COL0_X+DW+MARGIN, Y_VDD_T, "metal1"),   # 1.8V 전원
    ("VWL", COL1_X-MARGIN, Y_VWL_B, COL3_X+DW_HV+MARGIN, Y_VWL_T, "metal1"), # 고전압 전원
    ("VSS", 0, Y_VSS_B, CELL_W, Y_VSS_T, "metal1"),                           # 접지
]
for i, (nm, x0, y0, x1, y1, ly) in enumerate(pins):
    emit(f"box {x0} {y0} {x1} {y1}"); emit(f"label {nm} s {ly}"); emit(f"port make {i+1}")

# === 저장 + DRC 체크 + SPICE 추출 + GDS 출력 ===
emit("\n# === SAVE ===")
emit("save wl_driver")
emit("drc on"); emit("select top cell"); emit("drc check"); emit("drc catchup")
emit(f"box 0 0 {CELL_W} {Y_VDD_T}")
emit("drc count total")
# flatten 후 추출 (계층 문제 방지)
emit("flatten wl_driver_flat"); emit("load wl_driver_flat"); emit("select top cell")
emit("extract all"); emit("ext2spice lvs"); emit("ext2spice")  # → wl_driver_flat.spice
emit("load wl_driver"); emit("gds write wl_driver.gds"); emit("quit -noprompt")

# === TCL 파일 출력 ===
out = os.path.expandvars("$PROJECT_ROOT/analog/layout/wl_driver/wl_driver_gen.tcl")
with open(out, "w") as f: f.write("\n".join(T))
print(f"Generated {out} ({len(T)} lines)")
