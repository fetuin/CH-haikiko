#!/usr/bin/env python3
"""丸型ルーバーグリル: パラメータからSTEPを生成するCadQueryスクリプト。
使い方: pip install cadquery  の後、 python3 round_vent_grille_step.py [出力.step]
単位 mm。値は round_vent_grille.scad と同じで、写真からの推定値です。
+Z が前面(化粧面)側、z=HEIGHT が前面、z=0 が背面。タブ付きの桟が X 軸に沿います。"""
import math
import sys
import cadquery as cq

# ---- パラメータ ----
OUTER_D = 110.0        # フランジ外径
HEIGHT = 10.0          # 全高
FLANGE_T = 4.0         # フランジ外周の厚み
FLANGE_IN_R = 49.5     # フランジ前面の内周半径
FLANGE_ROUND = 1.0     # フランジ前面側の角丸半径

SPIGOT_RIM_IN = 46.6   # 差し込み部 背面リムの内周半径
SPIGOT_RIM_OUT = 48.6  # 差し込み部 背面リムの外周半径
PAD_R = 49.7           # 厚い帯の外周半径(はめ合い)
PAD_H = 2.2            # 厚い帯の高さ
PAD_START = 10.0       # 厚い帯の開始角度
PAD_SPAN = 42.0        # 厚い帯1本の角度範囲
PAD_COUNT = 3

# ルーバーリング: 前面内周, 前面外周, 背面内周, 背面外周 (半径)
RINGS = [
    (13.4, 16.7, 9.0, 11.0),
    (22.5, 26.0, 18.0, 20.0),
    (31.7, 35.6, 27.8, 29.8),
    (40.8, 44.4, 37.2, 39.2),
]
RING_EDGE = 0.3        # リング前面の面取り
RING_FLARE = 1.6       # リング壁のふくらみ

HUB_FRONT_R = 7.5
HUB_BACK_R = 5.1
HUB_BORE_R = 3.2
HUB_PEG_R = 1.6

SPOKE_W_FRONT = 1.5
SPOKE_W_BACK = 2.0
SPOKE_R_IN = 6.0       # HUB_BACK_R より小さくすると背面でハブとつながる

TAB_W = 8.0
TAB_T = 2.5
TAB_R_END = 54.5

SCOOP_ANGLE = 135.0    # 反対側にもう1か所
SCOOP_R = 49.0
SCOOP_LEN = 6.3
SCOOP_WID = 11.5
SCOOP_DEP = 2.2
SCOOP_TILT = 54.6
SCOOP_SHELL = 1.3
NOTCH_R = 48.0
NOTCH_SR = 5.8
NOTCH_ST = 7.8

RIB_COUNT = 3
RIB_START = 81.0
RIB_LEN = 3.2
RIB_T = 1.1

PIN_PAD_R = 1.7
PIN_PAD_T = 1.0
PRINT_ORIENTATION = True   # 前面を下にした印刷向き(同梱のSTLと同じ)。False で +Z が前面

# ---- 派生値 ----
R = OUTER_D / 2
H = HEIGHT
Z_FB = H - FLANGE_T
TOL = 1e-4


def rotz(shape, deg):
    return shape.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), deg)


def solid_of(wp):
    return wp.val()


def rev(wp):
    """XZ作業面の断面をZ軸まわりに一周回転する"""
    return solid_of(wp.close().revolve(360, (0, 0, 0), (0, 1, 0)))


def xz():
    return cq.Workplane("XZ")


def poly_rev(pts):
    return rev(xz().polyline(pts))


def flare_pts(r0, r1, n=8):
    z_top = H - RING_EDGE
    return [(r0 + (r1 - r0) * (i / n) ** RING_FLARE, z_top * i / n) for i in range(n + 1)]


def louver_ring(a, b, c, d):
    outer = flare_pts(d, b)
    inner = flare_pts(c, a)[::-1]
    wp = (xz().moveTo(*outer[0]).spline(outer[1:], includeCurrent=True,
                                        tangents=[(0, 1), (b - flare_pts(d, b)[-2][0], outer[-1][1] - outer[-2][1])])
          .lineTo(b - RING_EDGE, H).lineTo(a + RING_EDGE, H).lineTo(*inner[0])
          .spline(inner[1:], includeCurrent=True,
                  tangents=[(inner[1][0] - inner[0][0], inner[1][1] - inner[0][1]), (0, -1)]))
    return rev(wp)


def body_profile():
    c, d, fi, fr = SPIGOT_RIM_IN, SPIGOT_RIM_OUT, FLANGE_IN_R, FLANGE_ROUND
    inner = [(c + 0.4, 0.3 * H), (c + 1.47, 0.603 * H), (fi - 0.3, H - 0.3)]
    outer = [(d + 1.7, Z_FB - 0.5), (d + 1.0, Z_FB - 1.3), (d + 0.6, 0.5 * Z_FB), (d + 0.3, 0.25 * Z_FB), (d, 0.0)]
    q = math.radians(45)
    wp = (xz().moveTo(c, 0.0).spline(inner, includeCurrent=True)
          .lineTo(fi + 0.2, H).lineTo(R - fr, H)
          .threePointArc((R - fr + fr * math.sin(q), H - fr + fr * math.cos(q)), (R, H - fr))
          .lineTo(R, Z_FB + 0.5).lineTo(R - 0.4, Z_FB).lineTo(d + 2.8, Z_FB)
          .spline(outer, includeCurrent=True, tangents=[(-1, 0), (-0.1, -1)]))
    return rev(wp)


def hub_profile():
    f, b, k = HUB_FRONT_R, HUB_BACK_R, HUB_FRONT_R - HUB_BACK_R
    wall = [(b + k / 12, 0.25 * H), (b + k / 3, 0.5 * H), (b + k * 17 / 24, 0.75 * H), (f, H - 0.3)]
    wp = (xz().moveTo(HUB_BORE_R, 0.0).lineTo(b, 0.0).spline(wall, includeCurrent=True)
          .lineTo(f - 0.3, H).lineTo(1.2, H).lineTo(0.9, H - 0.25).lineTo(0.0, H - 0.35)
          .lineTo(0.0, 0.45 * H).lineTo(HUB_PEG_R - 0.4, 0.45 * H).lineTo(HUB_PEG_R - 0.1, 0.5 * H)
          .lineTo(HUB_PEG_R, 0.75 * H).lineTo(HUB_BORE_R - 0.2, 0.75 * H))
    return rev(wp)


def ellipsoid_local(grow=0.0):
    """角度0の位置に置いた傾き付き楕円体"""
    s = cq.Solid.makeSphere(1.0, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -90, 90, 360)
    m = cq.Matrix([[SCOOP_LEN + grow, 0, 0, 0], [0, SCOOP_WID + grow, 0, 0], [0, 0, SCOOP_DEP + grow, 0]])
    e = s.transformGeometry(m)
    # Y軸まわりに傾け、+X が外周かつ前面側へ向くようにする
    e = e.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), -SCOOP_TILT)
    return e.translate(cq.Vector(SCOOP_R, 0, 0.608 * H))


def scoop_cutter_local():
    """楕円体の下半分と、そのZ方向シルエットを押し上げた柱。床面より上をすべて取り除く"""
    a, b = SCOOP_LEN, SCOOP_DEP
    t = math.radians(SCOOP_TILT)
    rp = math.sqrt((a * math.cos(t)) ** 2 + (b * math.sin(t)) ** 2)   # 平面視の半径方向半径
    zp = (a * a - b * b) * math.sin(t) * math.cos(t) / rp             # シルエット端の高さ差
    phi = math.degrees(math.atan2(zp, rp))
    z0 = 0.608 * H
    upper = (cq.Workplane("XY").box(120, 120, 60, centered=(True, True, False)).val()
             .rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), -phi)
             .translate(cq.Vector(SCOOP_R, 0, z0)))
    lower_half = ellipsoid_local().cut(upper)
    # 平面視の楕円柱を、同じ傾斜面より上だけ残す
    column = (cq.Workplane("XY").workplane(offset=z0 - 20).center(SCOOP_R, 0)
              .ellipse(rp, SCOOP_WID).extrude(50).val())
    column = column.intersect(upper)
    return lower_half.fuse(column, glue=True, tol=TOL).clean()


def build():
    c, d = SPIGOT_RIM_IN, SPIGOT_RIM_OUT
    parts = []

    # フランジ+差し込み部
    parts.append(body_profile())

    # くぼみ裏のふくらみ
    keep = poly_rev([(c + 0.3, 0), (R - 0.6, 0), (R - 0.6, Z_FB + 0.5), (c + 1.6, Z_FB + 0.5)])
    dome0 = ellipsoid_local(SCOOP_SHELL)
    for k in (0, 180):
        parts.append(rotz(dome0, SCOOP_ANGLE + k).intersect(keep))

    # リブ
    fin = cq.Workplane("XY").box(RIB_LEN, RIB_T, Z_FB - 0.3, centered=False).val().translate(
        cq.Vector(d - 0.2, -RIB_T / 2, 0.3))
    for i in range(RIB_COUNT):
        parts.append(rotz(fin, RIB_START + i * 360 / RIB_COUNT))

    # 厚い帯
    band = poly_rev([(d - 0.5, 0), (PAD_R, 0), (PAD_R, PAD_H), (PAD_R - 0.5, PAD_H + 0.8), (d - 0.5, PAD_H + 0.8)])
    for i in range(PAD_COUNT):
        a0 = PAD_START + i * 360 / PAD_COUNT
        pts = [(0, 0)] + [(R * 1.6 * math.cos(math.radians(a0 + PAD_SPAN * f)),
                           R * 1.6 * math.sin(math.radians(a0 + PAD_SPAN * f))) for f in (0, 0.5, 1)]
        sec = cq.Workplane("XY").workplane(offset=-2).polyline(pts).close().extrude(H + 4).val()
        parts.append(band.intersect(sec))

    # ルーバーリング(最外周はくぼみの横を切り欠く)
    for r in RINGS[:-1]:
        parts.append(louver_ring(*r))
    last = louver_ring(*RINGS[-1])
    for k in (0, 180):
        notch = (cq.Workplane("XY").workplane(offset=-2).center(NOTCH_R, 0)
                 .ellipse(NOTCH_SR, NOTCH_ST).extrude(H + 4).val())
        last = last.cut(rotz(notch, SCOOP_ANGLE + k))
    parts.append(last)

    # 丸パッド
    for rr in [(r[2] + r[3]) / 2 for r in RINGS] + [(c + d) / 2]:
        for a in (0, 90, 180, 270):
            parts.append(rotz(cq.Solid.makeCylinder(PIN_PAD_R, PIN_PAD_T, cq.Vector(rr, 0, 0)), a))

    # タブ
    tab = (cq.Workplane("XY").box(TAB_R_END - c + 0.1, TAB_W, TAB_T, centered=False).val()
           .translate(cq.Vector(c - 0.1, -TAB_W / 2, 0))
           .intersect(cq.Solid.makeCylinder(TAB_R_END, TAB_T)))
    parts += [tab, rotz(tab, 180)]

    # ハブ
    parts.append(hub_profile())

    # 十字の桟
    env = poly_rev([(SPOKE_R_IN, 0), (d - 0.8, 0), (d + 0.4, 0.5 * H), (FLANGE_IN_R + 0.4, H), (SPOKE_R_IN, H)])
    trap = [(-SPOKE_W_BACK / 2, 0), (SPOKE_W_BACK / 2, 0), (SPOKE_W_FRONT / 2, H), (-SPOKE_W_FRONT / 2, H)]
    web_x = cq.Workplane("YZ").workplane(offset=-OUTER_D / 2).polyline(trap).close().extrude(OUTER_D).val()
    webs = web_x.fuse(rotz(web_x, 90), tol=TOL).intersect(env)
    parts.append(webs)

    model = parts[0].fuse(*parts[1:], tol=TOL)

    # くぼみと中央の穴
    cutter0 = scoop_cutter_local()
    for k in (0, 180):
        model = model.cut(rotz(cutter0, SCOOP_ANGLE + k), tol=TOL)
    bore = poly_rev([(0, -1), (HUB_BORE_R, -1), (HUB_BORE_R, 0), (HUB_BORE_R - 0.2, 0.75 * H),
                     (HUB_PEG_R, 0.75 * H), (HUB_PEG_R - 0.1, 0.5 * H), (HUB_PEG_R - 0.4, 0.45 * H), (0, 0.45 * H)])
    model = model.cut(bore, tol=TOL).clean()

    if PRINT_ORIENTATION:
        model = model.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180).translate(cq.Vector(0, 0, H))
    return model


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "round_vent_grille.step"
    m = build()
    print("valid", m.isValid(), "solids", len(m.Solids()), "faces", len(m.Faces()),
          "volume mm3", round(m.Volume(), 1))
    m.exportStep(out)
    print("wrote", out)
