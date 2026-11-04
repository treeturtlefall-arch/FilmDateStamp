"""
FilmDateStamp - 写ルンです・90sコンパクト機（富士フイルムCardia/Tiara、京セラT-Proof、リコーGR1等）
実機ドットマトリクス露光仕様完全準拠 オリジナルTrueTypeフォント『FDS-DotStrict』自動ビルドスクリプト

仕様（1000 UPM基準）:
- マトリクス解像度: 5列 × 7行（5×7 ドットマトリクス）
- ドット単体形状: 縦長カプセル型（Stadium / Pill Shape）
  - 幅 Dx = 65.0 units、高さ Dy = 80.0 units（縦長比 1.23:1）
  - 上下端は半径 R = 32.5 units の滑らかな半円、中央垂直直線部 15.0 units
- ピッチ:
  - 水平ピッチ Px = 75.0 units（列間ギャップ 10.0 units）
  - 垂直ピッチ Py = 100.0 units（行間ギャップ 20.0 units）
- 文字寸法: 描画全幅 W = 365.0 units (X: 50..415)、描画全高 H = 680.0 units (Y: 100..780, W/H ≈ 0.537)
- 仮想ボディ（Advance Width）: 480 units（等幅 Monospace）
- スラント角: 0.0°（完全直立）
"""

import os
import math
from typing import List, Tuple, Dict
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

Point = Tuple[int, int]
Polygon = List[Point]

# ==============================================================================
# 1. 基本メトリクス・幾何定数定義 (1000 UPM)
# ==============================================================================
UPM = 1000
ASCENDER = 900
DESCENDER = -100
CAP_HEIGHT = 680
ADVANCE_WIDTH = 480

GRID_COLS = 5
GRID_ROWS = 7

X_START = 50.0     # Col 0 左端 X 座標 (左マージン 50 units, 右マージン 480 - 415 = 65 units)
Y_BASE = 100.0     # Row 6 下端 Y 座標 (下マージン 100 units, 上マージン 1000 - 780 = 220 units)

DOT_W = 65.0       # ドット水平幅 Dx = 65.0 units
DOT_H = 80.0       # ドット垂直高 Dy = 80.0 units (縦長比 1.23:1)
DOT_R = 32.5       # 上下端半円半径 R = Dx / 2 = 32.5 units
PITCH_X = 75.0     # 水平ピッチ Px = 75.0 units (列間ギャップ 10.0 units)
PITCH_Y = 100.0    # 垂直ピッチ Py = 100.0 units (行間ギャップ 20.0 units)


# ==============================================================================
# 2. 全グリフのビットマップ点灯定義 (5列 x 7行, レポート第6.3節準拠)
# ==============================================================================
# 1 = 点灯 (Stadium Dot), 0 = 消灯
GLYPH_BITMAPS: Dict[str, List[List[int]]] = {
    '0': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
    '1': [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
    ],
    '2': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0],
        [1, 1, 1, 1, 1],
    ],
    '3': [
        [1, 1, 1, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [1, 1, 1, 1, 0],
    ],
    '4': [
        [0, 0, 0, 1, 0],
        [0, 0, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [1, 0, 0, 1, 0],
        [1, 1, 1, 1, 1],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0],
    ],
    '5': [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
    '6': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
    '7': [
        [1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0],
    ],
    '8': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
    '9': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
    "'": [  # 公式アポストロフィ (右上 Col 3, Row 0 から左下 Col 2, Row 1 への斜め2ドット)
        [0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ],
    ':': [  # コロン (Col 2 の Row 1 & Row 5)
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
    ],
    '-': [  # ハイフン (Row 3 中央横3ドット)
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ],
    '.': [  # ピリオド (最下段 Row 6, Col 1〜2)
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0],
    ],
    '/': [  # スラッシュ (対角線5ドット)
        [0, 0, 0, 0, 1],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0],
    ],
    ' ': [  # 空白 (全消灯)
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ],
}

CHAR_TO_GLYPH_NAME: Dict[str, str] = {
    ' ': "space",
    '0': "zero",
    '1': "one",
    '2': "two",
    '3': "three",
    '4': "four",
    '5': "five",
    '6': "six",
    '7': "seven",
    '8': "eight",
    '9': "nine",
    "'": "quotesingle",
    ':': "colon",
    '-': "hyphen",
    '.': "period",
    '/': "slash",
}


# ==============================================================================
# 3. スタジアム（カプセル）形状ベクター輪郭生成
# ==============================================================================
def make_stadium_dot(col: int, row: int, arc_steps: int = 12) -> Polygon:
    """
    指定されたマトリクス座標 (col: 0..4, row: 0..6) に配置される
    縦長カプセル型（Stadium / Pill Shape: 幅65 × 高さ80, 上下半円 R=32.5, 中央直線15.0）の
    時計回り（Clockwise）ポリゴン頂点列を生成する。

    - Col c の X 範囲: [50 + 75*c, 50 + 75*c + 65] -> Col 0..4 で X: 50..415 (全幅 365 units)
    - Row r の Y 範囲: [100 + 100*(6-r), 100 + 100*(6-r) + 80] -> Row 0..6 で Y: 100..780 (全高 680 units)
    """
    x_min = X_START + col * PITCH_X
    y_min = Y_BASE + (GRID_ROWS - 1 - row) * PITCH_Y

    xc = x_min + DOT_R              # ドット中心 X
    yc_bot = y_min + DOT_R          # 下側半円の中心 Y (y_min + 32.5)
    yc_top = y_min + DOT_H - DOT_R  # 上側半円の中心 Y (y_min + 47.5, 直線部高さ 15.0)

    pts: Polygon = []

    # 1. 上側半円: 左端 (theta = pi) -> 頂点 (theta = pi/2) -> 右端 (theta = 0) [時計回り]
    for k in range(arc_steps + 1):
        theta = math.pi * (1.0 - k / float(arc_steps))
        px = int(round(xc + DOT_R * math.cos(theta)))
        py = int(round(yc_top + DOT_R * math.sin(theta)))
        if not pts or pts[-1] != (px, py):
            pts.append((px, py))

    # 2. 下側半円: 右端 (theta = 0) -> 底点 (theta = -pi/2) -> 左端 (theta = -pi) [時計回り]
    for k in range(arc_steps + 1):
        theta = -math.pi * (k / float(arc_steps))
        px = int(round(xc + DOT_R * math.cos(theta)))
        py = int(round(yc_bot + DOT_R * math.sin(theta)))
        if not pts or pts[-1] != (px, py):
            pts.append((px, py))

    if len(pts) > 1 and pts[0] == pts[-1]:
        pts.pop()

    return pts


def bitmap_to_polygons(bitmap: List[List[int]]) -> List[Polygon]:
    """5×7 ビットマップ配列から点灯ドットのスタジアム輪郭リストを生成する"""
    polygons: List[Polygon] = []
    for row_idx, row_vals in enumerate(bitmap):
        for col_idx, val in enumerate(row_vals):
            if val:
                polygons.append(make_stadium_dot(col_idx, row_idx))
    return polygons


def build_tt_glyph(polygons: List[Polygon]):
    """ポリゴンリストから TrueType Glyph オブジェクトを生成"""
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
def build_strict_dot_font(
    output_path: str,
    family_name: str = "FDS Dot Strict",
    style_name: str = "Regular",
    ps_name: str = "FDSDotStrict-Regular",
):
    """
    実機5×7ドットマトリクス仕様に完全準拠した FDSDotStrict-Regular.ttf をゼロスクラッチ生成する。
    """
    glyph_order = [
        ".notdef",
        "space",
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "quotesingle",
        "colon",
        "hyphen",
        "period",
        "slash",
    ]

    glyphs = {}
    metrics = {}

    # 1. .notdef (外周5×7枠の極細矩形)
    notdef_poly: List[Polygon] = [
        [(50, 780), (415, 780), (415, 100), (50, 100)],
        [(80, 130), (385, 130), (385, 750), (80, 750)],  # 内穴は反時計回り (CCW)
    ]
    glyphs[".notdef"] = build_tt_glyph(notdef_poly)
    metrics[".notdef"] = (ADVANCE_WIDTH, 50)

    # 2. 全収録グリフの構築 (等幅 Advance Width = 480 units)
    for ch, gname in CHAR_TO_GLYPH_NAME.items():
        bitmap = GLYPH_BITMAPS[ch]
        polys = bitmap_to_polygons(bitmap)
        glyphs[gname] = build_tt_glyph(polys)
        if polys:
            lsb = min(pt[0] for p in polys for pt in p)
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
        0x003A: "colon",        # : Colon
        0x002D: "hyphen",       # - Hyphen-minus
        0x2010: "hyphen",       # ‐ Hyphen
        0x2013: "hyphen",       # – En dash
        0x2212: "hyphen",       # − Minus sign
        0x002E: "period",       # . Period
        0x002C: "period",       # , Comma fallback
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
        "version": "Version 1.000; 1990s 5x7 Capsule Dot Matrix Strict Spec",
        "psName": ps_name,
    }
    fb.setupNameTable(name_strings)

    fb.setupOS2(
        sTypoAscender=ASCENDER,
        sTypoDescender=DESCENDER,
        sTypoLineGap=0,
        usWinAscent=ASCENDER,
        usWinDescent=abs(DESCENDER),
        sxHeight=480,
        sCapHeight=CAP_HEIGHT,
        usWeightClass=400,
        fsSelection=0x0040,  # REGULAR
    )
    fb.setupPost(italicAngle=0.0, isFixedPitch=1)
    # Mac epoch (1904-01-01) からの秒数: 2026-01-01 00:00:00 UTC = 3850080000
    ts_2026 = 3850080000
    fb.setupHead(unitsPerEm=UPM, macStyle=0x0000, created=ts_2026, modified=ts_2026)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fb.save(output_path)
    print(f"[OK] Built strict 5x7 dot-matrix font: {output_path} (W=365, H=680, W/H={365/680:.3f}, advance={ADVANCE_WIDTH})")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fonts_dir = os.path.join(os.path.dirname(script_dir), "fonts")
    out_path = os.path.join(fonts_dir, "FDSDotStrict-Regular.ttf")
    build_strict_dot_font(output_path=out_path)


if __name__ == "__main__":
    main()
