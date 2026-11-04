"""
FilmDateStamp - 1970年代 機械式活字・光学縮小投影カメラ
（Canon Canodate E [1970], Canon Datematic [1974], Canon Data Back A [1977] 等）
物理・工学・タイポグラフィ仕様完全準拠 オリジナルTrueTypeフォント『FDS-Mechanical70s』自動ビルドスクリプト

仕様（1000 UPM基準、調査レポート第3章・第5.1節準拠）:
- フォント名: FDSMechanical70s-Regular.ttf (Family: FDS Mechanical 70s)
- EMスクエア: 1000 Units Per Em (UPM)
- 等幅ピッチ (Advance Width): 620 units（円筒活字ドラムの均等分割ピッチに基づく完全等幅 Monospaced）
- キャップハイト (Cap Height): 720 units (Y: 0 〜 720)
- アセンダー / ディセンダー: Ascender = 800 units / Descender = -200 units
- 基本ストローク幅 (Stem Width): 96 units（DIN 1451 / JIS工業彫刻文字準拠モノライン）
- 角丸ラジアス (Corner Radius): 外角 R = 20 units、内角 R = 12 units（単玉縮小レンズの解像ボケ・イラジエーション再現）
- 標準文字描画幅: 380 units (X: 120 〜 500, W/H = 380/720 ≈ 0.528 縦長コンデンスド)
- スラント角: 0.0°（完全直立）
"""

import os
import math
from typing import List, Tuple, Dict, Optional
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

PointF = Tuple[float, float]
PointI = Tuple[int, int]
PolygonF = List[PointF]
PolygonI = List[PointI]

# ==============================================================================
# 1. 基本メトリクス・幾何定数定義 (1000 UPM)
# ==============================================================================
UPM = 1000
ASCENDER = 800
DESCENDER = -200
CAP_HEIGHT = 720
ADVANCE_WIDTH = 620

STEM = 96.0
R_OUTER = 20.0
R_INNER = 12.0

X_CENTER = 310.0
X_LEFT = 120.0
X_RIGHT = 500.0
Y_BOTTOM = 0.0
Y_TOP = 720.0


# ==============================================================================
# 2. 幾何学ユーティリティ（円弧生成・角丸フィレット・ポリゴン回転・Boolean合成）
# ==============================================================================
def arc_points(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    deg_start: float,
    deg_end: float,
    steps: int = 24,
    include_start: bool = True,
    include_end: bool = True,
) -> PolygonF:
    """中心 (cx, cy)、半径 (rx, ry) の楕円弧を deg_start から deg_end まで生成する"""
    pts: PolygonF = []
    for i in range(steps + 1):
        if i == 0 and not include_start:
            continue
        if i == steps and not include_end:
            continue
        t = i / float(steps)
        deg = deg_start + (deg_end - deg_start) * t
        rad = math.radians(deg)
        pts.append((cx + rx * math.cos(rad), cy + ry * math.sin(rad)))
    return pts


def fillet_polygon(
    pts: PolygonF,
    radii: Optional[List[float]] = None,
    default_outer_r: float = R_OUTER,
    default_inner_r: float = R_INNER,
    arc_steps: int = 6,
    is_hole: bool = False,
) -> PolygonF:
    """
    多角形の各頂点を指定ラジアス（外角 R=20, 内角 R=12）で滑らかに角丸フィレット化する。
    TrueType 外周（CW: 時計回り）を基準とし、is_hole=True（CCW: 反時計回り）にも対応。
    """
    n = len(pts)
    if n < 3:
        return pts

    out: PolygonF = []
    for i in range(n):
        p_prev = pts[(i - 1) % n]
        p_curr = pts[i]
        p_next = pts[(i + 1) % n]

        v1x, v1y = p_prev[0] - p_curr[0], p_prev[1] - p_curr[1]
        v2x, v2y = p_next[0] - p_curr[0], p_next[1] - p_curr[1]
        len1 = math.hypot(v1x, v1y)
        len2 = math.hypot(v2x, v2y)
        if len1 < 1e-3 or len2 < 1e-3:
            out.append(p_curr)
            continue

        u1x, u1y = v1x / len1, v1y / len1
        u2x, u2y = v2x / len2, v2y / len2

        # 外積で凸角（外角）か凹角（内角）かを判定
        # p_prev -> p_curr -> p_next の進行方向ベクトル d1 = -u1, d2 = u2
        cross = (-u1x) * u2y - (-u1y) * u2x
        dot = max(-1.0, min(1.0, u1x * u2x + u1y * u2y))
        angle = math.acos(dot)  # 2辺の挟み角 (0 .. pi)

        if abs(angle - math.pi) < 1e-2 or angle < 1e-2:
            out.append(p_curr)
            continue

        if radii is not None and i < len(radii):
            r = radii[i]
        else:
            # CW 外周では右折 (cross < 0) が外角、左折 (cross > 0) が内角
            is_outer = (cross < 0) if not is_hole else (cross > 0)
            r = default_outer_r if is_outer else default_inner_r

        if r <= 0.2:
            out.append(p_curr)
            continue

        half_ang = angle / 2.0
        tan_half = math.tan(half_ang)
        if tan_half < 1e-4:
            out.append(p_curr)
            continue

        # 頂点から接点までの距離
        dist = r / tan_half
        max_dist = min(len1, len2) * 0.45
        if dist > max_dist:
            dist = max_dist
            r = dist * tan_half

        t1x, t1y = p_curr[0] + u1x * dist, p_curr[1] + u1y * dist
        t2x, t2y = p_curr[0] + u2x * dist, p_curr[1] + u2y * dist

        # 角の二等分線方向にある円弧中心
        bx, by = u1x + u2x, u1y + u2y
        blen = math.hypot(bx, by)
        if blen < 1e-4:
            out.append(p_curr)
            continue
        bx /= blen
        by /= blen
        center_dist = math.hypot(dist, r)
        cx, cy = p_curr[0] + bx * center_dist, p_curr[1] + by * center_dist

        a1 = math.atan2(t1y - cy, t1x - cx)
        a2 = math.atan2(t2y - cy, t2x - cx)
        da = a2 - a1
        while da <= -math.pi:
            da += 2.0 * math.pi
        while da > math.pi:
            da -= 2.0 * math.pi

        for k in range(arc_steps + 1):
            ang = a1 + da * (k / float(arc_steps))
            out.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))

    return out


def quantize_polygons(polys: List[PolygonF]) -> List[PolygonI]:
    """浮動小数点ポリゴンリストを整数座標に変換し、連続重複頂点を除去する"""
    result: List[PolygonI] = []
    for poly in polys:
        q: PolygonI = []
        for x, y in poly:
            pt = (int(round(x)), int(round(y)))
            if not q or q[-1] != pt:
                q.append(pt)
        if len(q) > 1 and q[0] == q[-1]:
            q.pop()
        if len(q) >= 3:
            result.append(q)
    return result


def rotate_180_polygons(polys: List[PolygonF], cx: float = 310.0, cy: float = 360.0) -> List[PolygonF]:
    """(cx, cy) を中心に180度点対称回転する（回転により巻き方向CW/CCWはそのまま維持される）"""
    rotated: List[PolygonF] = []
    for poly in polys:
        rotated.append([(2.0 * cx - x, 2.0 * cy - y) for x, y in poly])
    return rotated


# ==============================================================================
# 3. 各グリフ（0〜9、記号）の厳密ベクターパス構築（第5.1節準拠）
# ==============================================================================
def build_glyph_0() -> List[PolygonF]:
    """
    '0': 幅 380 (X: 120..500), 高さ 720 (Y: 0..720)
    左右直線垂直、上下が半径 R=190 の半円弧の角丸カプセル形状（Stadium）。
    カウンター幅 188 units (X: 216..404, 内半径 R=94)。
    """
    # 外周 (CW): 左直線上昇 -> 上半円 (180° -> 0°) -> 右直線下降 -> 下半円 (0° -> -180°)
    outer = (
        arc_points(310.0, 530.0, 190.0, 190.0, 180.0, 0.0, steps=28)
        + arc_points(310.0, 190.0, 190.0, 190.0, 0.0, -180.0, steps=28)
    )
    # 内周カウンター (CCW): 上半円 (0° -> 180°) -> 左直線下降 -> 下半円 (180° -> 360°)
    inner = (
        arc_points(310.0, 530.0, 94.0, 94.0, 0.0, 180.0, steps=24)
        + arc_points(310.0, 190.0, 94.0, 94.0, 180.0, 360.0, steps=24)
    )
    return [outer, inner]


def build_glyph_1() -> List[PolygonF]:
    """
    '1': 幅 240 (X: 166..406), 高さ 720 (Y: 0..720)
    メインステム X: 310〜406 (幅96)。
    頂点から左下45°へ力強く突き出す明確なカギ鼻ビーク（先端 X=166 垂直カット）。
    底部は台座セリフなしのサンセリフ調。
    外角 R=20, 内角 R=12 でフィレット化しつつ、バウンディングボックス X: 166..406, Y: 0..720 を厳守。
    """
    # 頂点フラット X: 310..406, Y=720 から左下45°へ (166, 576) まで降り、
    # 先端 X=166 で垂直カット (Y: 576 -> 446)、そこから45°で内角 (310, 590) へ戻る
    raw_pts: PolygonF = [
        (310.0, 720.0),  # 0: カギ鼻開始頂点
        (406.0, 720.0),  # 1: 右上外角
        (406.0, 0.0),    # 2: 右下外角
        (310.0, 0.0),    # 3: 左下外角
        (310.0, 590.0),  # 4: カギ鼻脇の内角 (凹角 R=12)
        (166.0, 446.0),  # 5: カギ鼻先端下角
        (166.0, 576.0),  # 6: カギ鼻先端上角 (先端垂直カット X=166)
    ]
    radii = [12.0, R_OUTER, R_OUTER, R_OUTER, R_INNER, 12.0, 12.0]
    return [fillet_polygon(raw_pts, radii=radii)]


def build_glyph_2() -> List[PolygonF]:
    """
    '2': 幅 380 (X: 120..500), 高さ 720 (Y: 0..720)
    上部半円ループ (頂点 Y=720) + 直線斜角ステム + 水平ベースバー (Y: 0..96, X: 120..500, 右端垂直カット)。
    """
    # 外周・内周を連続した1本の閉曲線 (CW) として構築
    pts: PolygonF = []
    # 1. 左上のアーチ端 (X: 120..216, Y=520 付近) から上部の外周半円 (中心 310, 530, R=190)
    pts.extend(arc_points(310.0, 530.0, 190.0, 190.0, 175.0, -32.0, steps=28))
    # 2. 右上ループ下側から斜め直線ステム外縁を通って左下のベースバー角へ
    #    (-32° での接点付近 X≈471, Y≈429 から X=238, Y=96 へ降り、水平ベースバー右端 X=500 へ)
    pts.extend([
        (238.0, 96.0),
        (500.0, 96.0),
        (500.0, 0.0),
        (120.0, 0.0),
        (120.0, 96.0),
    ])
    # 3. 斜めステム上縁を通って上部ループ内周 (中心 310, 530, R=94) へ
    pts.extend(arc_points(310.0, 530.0, 94.0, 94.0, -32.0, 175.0, steps=20))

    # 角ばった頂点のみ局所フィレット化（ベースバー右端・左端・内角）
    # アーチ部分の頂点はラジアス0にして滑らかさを保持
    radii = [0.0] * len(pts)
    for i, (px, py) in enumerate(pts):
        if (abs(px - 238.0) < 1.0 and abs(py - 96.0) < 1.0):
            radii[i] = R_INNER
        elif (abs(px - 500.0) < 1.0 and py in (0.0, 96.0)) or (abs(px - 120.0) < 1.0 and py == 0.0):
            radii[i] = R_OUTER
        elif abs(px - 120.0) < 1.0 and abs(py - 96.0) < 1.0:
            radii[i] = 10.0
    return [fillet_polygon(pts, radii=radii)]


def build_glyph_3() -> List[PolygonF]:
    """
    '3': 幅 380 (X: 120..500), 高さ 720 (Y: 0..720)
    上下2つの円弧ループ、中央左への鋭いくびれ (X=260, Y=376)。端部は水平カット。
    """
    pts: PolygonF = []
    # 上ループ外周 (172° -> -58°, X: 122..495, Y: 387..720)
    pts.extend(arc_points(310.0, 540.0, 185.0, 180.0, 172.0, -58.0, steps=26))
    # 下ループ外周 (55° -> -175°, X: 120..500, Y: 0..360)
    pts.extend(arc_points(310.0, 195.0, 190.0, 195.0, 55.0, -175.0, steps=28))
    # 下ループ内周 (-175° -> 90°)
    pts.extend(arc_points(310.0, 195.0, 94.0, 99.0, -175.0, 90.0, steps=20))
    # 中央くびれ左端 (X=260, Y=326 -> 416)
    pts.append((260.0, 326.0))
    pts.append((260.0, 416.0))
    # 上ループ内周 (-90° -> 172°)
    pts.extend(arc_points(310.0, 540.0, 89.0, 84.0, -90.0, 172.0, steps=20))
    return [pts]


def build_glyph_4() -> List[PolygonF]:
    """
    '4': 幅 400 (X: 100..500), 高さ 720 (Y: 0..720)
    頂点が完全に閉じたクローズド・トライアングル (Closed 4)。
    右垂直ステム X: 350〜446 (Y: 0〜720)。
    水平クロスバー Y: 210〜306 (X: 100〜500、右側に突出)。
    左斜めステムが頂点から左下を結ぶ。
    """
    outer_raw: PolygonF = [
        (334.0, 720.0),  # 0: 頂点左上
        (446.0, 720.0),  # 1: 頂点右上
        (446.0, 306.0),  # 2: クロスバー右上内角
        (500.0, 306.0),  # 3: クロスバー右端上
        (500.0, 210.0),  # 4: クロスバー右端下
        (446.0, 210.0),  # 5: クロスバー右下内角
        (446.0, 0.0),    # 6: ステム右下
        (350.0, 0.0),    # 7: ステム左下
        (350.0, 210.0),  # 8: クロスバー左下内角
        (100.0, 210.0),  # 9: 左端下角
        (100.0, 306.0),  # 10: 左端斜め開始角
    ]
    outer_radii = [
        14.0, R_OUTER, R_INNER, 14.0, 14.0, R_INNER,
        R_OUTER, R_OUTER, R_INNER, R_OUTER, 12.0,
    ]
    outer = fillet_polygon(outer_raw, radii=outer_radii, is_hole=False)

    # 内側三角形カウンター (CCW: 反時計回り)
    # 右辺 X=350, 下辺 Y=306, 斜辺は外斜辺と平行 (幅96オフセット)
    inner_raw: PolygonF = [
        (350.0, 560.0),  # 上頂点
        (206.0, 306.0),  # 左下頂点
        (350.0, 306.0),  # 右下頂点
    ]
    inner = fillet_polygon(inner_raw, radii=[R_INNER, R_INNER, R_INNER], is_hole=True)
    return [outer, inner]


def build_glyph_5() -> List[PolygonF]:
    """
    '5': 幅 380 (X: 120..500), 高さ 720 (Y: 0..720)
    水平トップバー (Y: 624..720, X: 135..490) + ショート垂直ステム + 下部円弧ループ (X: 120..500, Y: 0..450)。
    """
    pts: PolygonF = [
        (135.0, 720.0),
        (490.0, 720.0),
        (490.0, 624.0),
        (231.0, 624.0),
        (231.0, 424.0),
    ]
    # 下部ループ外周: 中心 (310, 225), Rx=190, Ry=225 (X: 120..500, Y: 0..450)
    pts.extend(arc_points(310.0, 225.0, 190.0, 225.0, 112.0, -165.0, steps=30))
    # 下部ループ内周: 中心 (310, 225), Rx=94, Ry=129
    pts.extend(arc_points(310.0, 225.0, 94.0, 129.0, -165.0, 130.0, steps=22))
    pts.append((135.0, 355.0))

    radii = [0.0] * len(pts)
    radii[0] = R_OUTER
    radii[1] = R_OUTER
    radii[2] = R_OUTER
    radii[3] = R_INNER
    radii[4] = R_INNER
    radii[-1] = R_OUTER
    return [fillet_polygon(pts, radii=radii)]


def build_glyph_6() -> List[PolygonF]:
    """
    '6': 幅 380 (X: 120..500), 高さ 720 (Y: 0..720)
    上部斜めアームから下部円弧ループへ滑らかに連続、広い開口部アパーチャ。
    全ストロークが均一線幅 (96 units) を保つ工業彫刻ジオメトリ。
    """
    outer: PolygonF = []
    # 1. 左下ボウル接点 (120, 210) から左上アーチ開始点へ滑らかに立ち上がる外縁
    outer.append((120.0, 210.0))
    # 2. 上部アーチ外周: 中心 (320, 530), Rx=165, Ry=190 (頂点 Y=720, 右端 22° で開放)
    outer.extend(arc_points(320.0, 530.0, 165.0, 190.0, 158.0, 22.0, steps=22))
    # 3. 上部アーチ内周: 中心 (320, 530), Rx=69 (165-96), Ry=94 (190-96) (22° -> 158°)
    outer.extend(arc_points(320.0, 530.0, 69.0, 94.0, 22.0, 158.0, steps=18))
    # 4. 内側斜めアームから下部ボウル上縁 (112°) へ接続し、ボウル外周を時計回りに -180° (120, 210) まで巡る
    outer.extend(arc_points(310.0, 210.0, 190.0, 210.0, 112.0, -180.0, steps=34))

    # 端部の角のみ軽くフィレット化 (index 158°->22° の終端2箇所とボウル接続部)
    radii = [0.0] * len(outer)
    # 22° 外角 (index 23) と 22° 内角 (index 24)、ボウル接続内角 (index 42)
    radii[23] = 14.0
    radii[24] = 14.0
    radii[42] = R_INNER
    outer_filleted = fillet_polygon(outer, radii=radii, is_hole=False)

    # 内穴カウンター (CCW): 中心 (310, 210), Rx=94 (190-96), Ry=114 (210-96)
    inner = arc_points(310.0, 210.0, 94.0, 114.0, 0.0, 360.0, steps=28, include_end=False)
    return [outer_filleted, inner]


def build_glyph_7() -> List[PolygonF]:
    """
    '7': 幅 380 (X: 120..500), 高さ 720 (Y: 0..720)
    水平トップバー (Y: 624..720, X: 120..500) から左下 (X: 180..284, Y=0) へ
    まっすぐ降りるストレートステム（クロスバーなし）。
    """
    raw_pts: PolygonF = [
        (120.0, 720.0),  # 0: 左上
        (500.0, 720.0),  # 1: 右上
        (500.0, 616.0),  # 2: 右上斜め開始角
        (284.0, 0.0),    # 3: 底辺右
        (180.0, 0.0),    # 4: 底辺左
        (392.0, 624.0),  # 5: トップバー下内角
        (120.0, 624.0),  # 6: トップバー左下
    ]
    radii = [R_OUTER, R_OUTER, 16.0, 14.0, 14.0, R_INNER, R_OUTER]
    return [fillet_polygon(raw_pts, radii=radii)]


def build_glyph_8() -> List[PolygonF]:
    """
    '8': 幅 380 (X: 120..500), 高さ 720 (Y: 0..720)
    下ループ (幅 380: X: 120..500, Y: 0..400) に対し、
    上ループ (幅 340: X: 140..480, Y: 340..720) がわずかに小さい視覚的安定比率。
    """
    # 外周 (CW): 左くびれ (222°) -> 上ループ頂点 (90°) -> 右くびれ (-42°)
    #          -> 右くびれ (42°) -> 下ループ底点 (-90°) -> 左くびれ (-222°)
    outer: PolygonF = []
    outer.extend(arc_points(310.0, 530.0, 170.0, 190.0, 222.0, -42.0, steps=28))
    outer.extend(arc_points(310.0, 200.0, 190.0, 200.0, 42.0, -222.0, steps=32))

    # 上内穴カウンター (CCW): 中心 (310, 526), Rx=78, Ry=98
    inner_top = arc_points(310.0, 526.0, 78.0, 98.0, 0.0, 360.0, steps=24, include_end=False)
    # 下内穴カウンター (CCW): 中心 (310, 196), Rx=94, Ry=104
    inner_bot = arc_points(310.0, 196.0, 94.0, 104.0, 0.0, 360.0, steps=24, include_end=False)

    return [outer, inner_top, inner_bot]


def build_glyph_9() -> List[PolygonF]:
    """
    '9': 幅 380 (X: 120..500), 高さ 720 (Y: 0..720)
    「6」の (X=310, Y=360) を中心とする180度完全点対称回転。
    """
    return rotate_180_polygons(build_glyph_6(), cx=310.0, cy=360.0)


def build_glyph_apostrophe() -> List[PolygonF]:
    """
    ''' (アポストロフィ): 西暦2桁表示 ('74 等) 用
    X: 250〜370, Y: 500〜720。幅 70 units、傾斜角 -18° の太い長方形ダッシュ。
    """
    # Y=500..720 (高さ 220), 傾斜による水平シフト = 50 units (atan(50/220) ≈ 13°〜18° 相当), 幅 70 units
    # X範囲: 左下 250..320 -> 右上 300..370 (全体 X: 250..370, Y: 500..720)
    raw_pts: PolygonF = [
        (300.0, 720.0),
        (370.0, 720.0),
        (320.0, 500.0),
        (250.0, 500.0),
    ]
    return [fillet_polygon(raw_pts, radii=[10.0, 10.0, 10.0, 10.0])]


def build_glyph_hyphen() -> List[PolygonF]:
    """
    '-' (ハイフン): 中央高さ (Y=360 付近: Y: 312〜408) の太い水平バー (幅 300: X: 160〜460, 高さ 96)。
    """
    raw_pts: PolygonF = [
        (160.0, 408.0),
        (460.0, 408.0),
        (460.0, 312.0),
        (160.0, 312.0),
    ]
    return [fillet_polygon(raw_pts, radii=[R_OUTER, R_OUTER, R_OUTER, R_OUTER])]


def build_glyph_period() -> List[PolygonF]:
    """
    '.' (ピリオド): ベースライン上の角丸正方形ドット (96×96 units, X: 262〜358, Y: 0〜96)。
    """
    raw_pts: PolygonF = [
        (262.0, 96.0),
        (358.0, 96.0),
        (358.0, 0.0),
        (262.0, 0.0),
    ]
    return [fillet_polygon(raw_pts, radii=[16.0, 16.0, 16.0, 16.0])]


def build_glyph_colon() -> List[PolygonF]:
    """
    ':' (コロン): 時刻表示対応用の角丸正方形ドット上下2点 (96×96 units, X: 262〜358)。
    """
    bot: PolygonF = [(262.0, 196.0), (358.0, 196.0), (358.0, 100.0), (262.0, 100.0)]
    top: PolygonF = [(262.0, 556.0), (358.0, 556.0), (358.0, 460.0), (262.0, 460.0)]
    return [
        fillet_polygon(bot, radii=[16.0, 16.0, 16.0, 16.0]),
        fillet_polygon(top, radii=[16.0, 16.0, 16.0, 16.0]),
    ]


def build_glyph_slash() -> List[PolygonF]:
    """
    '/' (スラッシュ): 日付区切り用ストレート斜線 (X: 160〜460, Y: 0〜720, 幅 96)。
    """
    raw_pts: PolygonF = [
        (364.0, 720.0),
        (460.0, 720.0),
        (256.0, 0.0),
        (160.0, 0.0),
    ]
    return [fillet_polygon(raw_pts, radii=[14.0, 14.0, 14.0, 14.0])]


def build_tt_glyph(polygons: List[PolygonI]):
    """整数ポリゴンリストから TrueType Glyph オブジェクトを生成"""
    pen = TTGlyphPen(None)
    for poly in polygons:
        if not poly:
            continue
        pen.moveTo(poly[0])
        for pt in poly[1:]:
            pen.lineTo(pt)
        pen.closePath()
    return pen.glyph()


# ==============================================================================
# 4. フォントコンパイル処理
# ==============================================================================
def build_strict_mechanical_font(
    output_path: str,
    family_name: str = "FDS Mechanical 70s",
    style_name: str = "Regular",
    ps_name: str = "FDSMechanical70s-Regular",
):
    """
    1970年代の機械式活字・光学縮小投影カメラ仕様に完全準拠した
    FDSMechanical70s-Regular.ttf をゼロスクラッチ生成する。
    """
    glyph_builders = {
        "space": lambda: [],
        "zero": build_glyph_0,
        "one": build_glyph_1,
        "two": build_glyph_2,
        "three": build_glyph_3,
        "four": build_glyph_4,
        "five": build_glyph_5,
        "six": build_glyph_6,
        "seven": build_glyph_7,
        "eight": build_glyph_8,
        "nine": build_glyph_9,
        "quotesingle": build_glyph_apostrophe,
        "hyphen": build_glyph_hyphen,
        "period": build_glyph_period,
        "colon": build_glyph_colon,
        "slash": build_glyph_slash,
    }

    glyph_order = [".notdef"] + list(glyph_builders.keys())
    glyphs = {}
    metrics = {}

    # 1. .notdef (外枠 120..500, 0..720)
    notdef_polys: List[PolygonI] = [
        [(120, 720), (500, 720), (500, 0), (120, 0)],
        [(160, 40), (460, 40), (460, 680), (160, 680)],
    ]
    glyphs[".notdef"] = build_tt_glyph(notdef_polys)
    metrics[".notdef"] = (ADVANCE_WIDTH, 120)

    # 2. 全収録グリフの構築 (完全等幅 Advance Width = 620 units)
    for gname, builder_fn in glyph_builders.items():
        float_polys = builder_fn()
        int_polys = quantize_polygons(float_polys)
        glyphs[gname] = build_tt_glyph(int_polys)
        if int_polys:
            lsb = min(pt[0] for p in int_polys for pt in p)
        else:
            lsb = 0
        metrics[gname] = (ADVANCE_WIDTH, int(lsb))

    # Unicode cmap マッピング
    cmap = {
        0x0020: "space",
        0x00A0: "space",
        0x0030: "zero",
        0x0031: "one",
        0x0032: "two",
        0x0033: "three",
        0x0034: "four",
        0x0035: "five",
        0x0036: "six",
        0x0037: "seven",
        0x0038: "eight",
        0x0039: "nine",
        # アポストロフィ・引用符類
        0x0027: "quotesingle",  # ' ASCII Apostrophe
        0x0060: "quotesingle",  # ` Grave accent
        0x2018: "quotesingle",  # ‘ Left single quotation mark
        0x2019: "quotesingle",  # ’ Right single quotation mark
        0x201B: "quotesingle",  # ‛ Single high-reversed-9 quotation mark
        0x02BC: "quotesingle",  # ʼ Modifier letter apostrophe
        # 区切り記号類
        0x002D: "hyphen",       # - Hyphen-minus
        0x2010: "hyphen",       # ‐ Hyphen
        0x2013: "hyphen",       # – En dash
        0x2212: "hyphen",       # − Minus sign
        0x002E: "period",       # . Period
        0x002C: "period",       # , Comma fallback
        0x003A: "colon",        # : Colon
        0x002F: "slash",        # / Slash
    }

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASCENDER, descent=DESCENDER, lineGap=0)

    full_name = f"{family_name} {style_name}" if style_name != "Regular" else family_name
    name_strings = {
        "copyright": "Copyright (c) 2026 FilmDateStamp Project. Licensed under SIL Open Font License 1.1.",
        "familyName": family_name,
        "styleName": style_name,
        "uniqueFontIdentifier": f"FilmDateStamp:{ps_name}:2026",
        "fullName": full_name,
        "version": "Version 1.000; 1970s Mechanical Date Wheel & Optical Projection Strict Spec",
        "psName": ps_name,
    }
    fb.setupNameTable(name_strings)

    fb.setupOS2(
        sTypoAscender=ASCENDER,
        sTypoDescender=DESCENDER,
        sTypoLineGap=0,
        usWinAscent=ASCENDER,
        usWinDescent=abs(DESCENDER),
        sxHeight=500,
        sCapHeight=CAP_HEIGHT,
        usWeightClass=400,
        fsSelection=0x0040,  # REGULAR
    )
    fb.setupPost(italicAngle=0.0, isFixedPitch=1)
    ts_2026 = 3850080000
    fb.setupHead(unitsPerEm=UPM, macStyle=0x0000, created=ts_2026, modified=ts_2026)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fb.save(output_path)
    print(f"[OK] Built strict 1970s mechanical font: {output_path} (UPM={UPM}, CapHeight={CAP_HEIGHT}, Advance={ADVANCE_WIDTH})")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fonts_dir = os.path.join(os.path.dirname(script_dir), "fonts")
    out_path = os.path.join(fonts_dir, "FDSMechanical70s-Regular.ttf")
    build_strict_mechanical_font(output_path=out_path)


if __name__ == "__main__":
    main()
