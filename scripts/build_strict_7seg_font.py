"""
FilmDateStamp - 1980s 諏訪精工舎（セイコーエプソン）クォーツデート仕様完全準拠
オリジナル7セグメントTrueTypeフォント『FDS7Strict』シリーズ自動ビルドスクリプト

仕様（1000 UPM基準）:
- 文字総描画幅 (W): 400 units / 文字総描画高さ (H): 800 units (Y: 50 〜 850, W/H = 0.500 スリム比率)
- セグメント基本厚 (S): 80 units (高さの 10.0%)
- セグメント間ギャップ (G): 28 units (高さの 3.5%)
- セグメント先端形状: 35°カット + 先端フラット面 (幅 18 units)
- スラント角:
  1. FDS7Strict-SLR.ttf     :  0.0° (直立型 / 一眼レフデータバック Nikon MF-14, Olympus Recordata 等)
  2. FDS7Strict-Compact.ttf : -7.0° (前傾型 / 80sコンパクト機 Canon Autoboy, Nikon L35AD ピカイチ等)
"""

import os
import math
from typing import List, Tuple, Dict
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

Point = Tuple[float, float]
Polygon = List[Point]

# ==============================================================================
# 1. 基本メトリクス・幾何定数定義 (1000 UPM)
# ==============================================================================
UPM = 1000
ASCENDER = 900
DESCENDER = -100
CAP_HEIGHT = 800
Y_BASE = 50.0
Y_TOP = 850.0

# 35°カットに伴うインセット量 (62 / tan(55°) ≈ 43.4, 31 / tan(55°) ≈ 21.7)
DX_OUTER = 43.0   # 外周フラット辺から内辺までの35°テーパー水平長
DY_OUTER = 43.0   # 外周フラット辺から内辺までの35°テーパー垂直長
DX_G = 22.0       # 中央Gセグメント両端の35°テーパー水平長


def get_base_segments() -> Dict[str, Polygon]:
    """
    直立型 (0.0°) における A〜G の7セグメント多角形座標（時計回り: CW）を定義する。
    TrueType (glyf) の外周輪郭規約に従い、全て時計回り（Clockwise）で頂点を構成する。

    各セグメントの仕様（第6.3〜6.4節準拠）:
    - A (最上段水平): Y_center=810 (Y: 770..850), X: 54..346, 上辺水平・両端下向き35°カット・先端フラット幅18
    - B (右上段垂直): X_center=360 (X: 320..400), Y: 478..770, 右辺垂直・両端内向き35°カット・先端フラット幅18
    - C (右下段垂直): X_center=360 (X: 320..400), Y: 130..422, 右辺垂直・両端内向き35°カット・先端フラット幅18
    - D (最下段水平): Y_center=90  (Y: 50..130),  X: 54..346, 下辺水平・両端上向き35°カット・先端フラット幅18
    - E (左下段垂直): X_center=40  (X: 0..80),    Y: 130..422, 左辺垂直・両端内向き35°カット・先端フラット幅18
    - F (左上段垂直): X_center=40  (X: 0..80),    Y: 478..770, 左辺垂直・両端内向き35°カット・先端フラット幅18
    - G (中央水平)  : Y_center=450 (Y: 410..490), X: 54..346, 六角形＋両端フラット幅18の八角形台形接合
    """
    # Segment A: Y in [770, 850], X in [54, 346]
    seg_a: Polygon = [
        (54, 850),                  # 左上角
        (346, 850),                 # 右上角 (上辺水平)
        (346, 832),                 # 右端フラット面 (幅18)
        (346 - DX_OUTER, 770),      # 右下内角 (35°カット)
        (54 + DX_OUTER, 770),       # 左下内角 (下辺水平)
        (54, 832),                  # 左端フラット面 (幅18)
    ]

    # Segment B: X in [320, 400], Y in [478, 770]
    seg_b: Polygon = [
        (382, 770),                 # 上端フラット面左 (幅18)
        (400, 770),                 # 右上角
        (400, 478),                 # 右下角 (外側垂直)
        (382, 478),                 # 下端フラット面左 (幅18)
        (320, 478 + DY_OUTER),      # 左下内角 (35°カット)
        (320, 770 - DY_OUTER),      # 左上内角 (内辺垂直)
    ]

    # Segment C: X in [320, 400], Y in [130, 422]
    seg_c: Polygon = [
        (382, 422),                 # 上端フラット面左 (幅18)
        (400, 422),                 # 右上角
        (400, 130),                 # 右下角 (外側垂直)
        (382, 130),                 # 下端フラット面左 (幅18)
        (320, 130 + DY_OUTER),      # 左下内角 (35°カット)
        (320, 422 - DY_OUTER),      # 左上内角 (内辺垂直)
    ]

    # Segment D: Y in [50, 130], X in [54, 346]
    seg_d: Polygon = [
        (54, 68),                   # 左端フラット面上 (幅18)
        (54 + DX_OUTER, 130),       # 左上内角 (35°カット)
        (346 - DX_OUTER, 130),      # 右上内角 (上辺水平)
        (346, 68),                  # 右端フラット面上 (幅18)
        (346, 50),                  # 右下角
        (54, 50),                   # 左下角 (下辺水平)
    ]

    # Segment E: X in [0, 80], Y in [130, 422]
    seg_e: Polygon = [
        (0, 422),                   # 左上角
        (18, 422),                  # 上端フラット面右 (幅18)
        (80, 422 - DY_OUTER),       # 右上内角 (35°カット)
        (80, 130 + DY_OUTER),       # 右下内角 (内辺垂直)
        (18, 130),                  # 下端フラット面右 (幅18)
        (0, 130),                   # 左下角 (外側垂直)
    ]

    # Segment F: X in [0, 80], Y in [478, 770]
    seg_f: Polygon = [
        (0, 770),                   # 左上角
        (18, 770),                  # 上端フラット面右 (幅18)
        (80, 770 - DY_OUTER),       # 右上内角 (35°カット)
        (80, 478 + DY_OUTER),       # 右下内角 (内辺垂直)
        (18, 478),                  # 下端フラット面右 (幅18)
        (0, 478),                   # 左下角 (外側垂直)
    ]

    # Segment G: Y in [410, 490], X in [54, 346]
    # 中央 Y=450 を軸に上下対称、先端フラット幅18 (Y: 441..459)、上下35°カット
    seg_g: Polygon = [
        (54, 459),                  # 左端フラット上
        (54 + DX_G, 490),           # 左上角
        (346 - DX_G, 490),          # 右上角 (上辺水平)
        (346, 459),                 # 右端フラット上
        (346, 441),                 # 右端フラット下 (先端幅18)
        (346 - DX_G, 410),          # 右下角
        (54 + DX_G, 410),           # 左下角 (下辺水平)
        (54, 441),                  # 左端フラット下 (先端幅18)
    ]

    return {
        "A": seg_a,
        "B": seg_b,
        "C": seg_c,
        "D": seg_d,
        "E": seg_e,
        "F": seg_f,
        "G": seg_g,
    }


def make_chamfered_box(x_min: float, y_min: float, x_max: float, y_max: float, chamfer: float = 10.0) -> Polygon:
    """
    ドット系素子（アポストロフィ・コロン・ピリオド）用の微細面取り八角形（CW）を生成する。
    ピン角をわずかに落とすことで実機LEDマスクの光学的柔和さを表現する。
    """
    c = min(chamfer, (x_max - x_min) * 0.25, (y_max - y_min) * 0.25)
    if c <= 0.5:
        return [
            (x_min, y_max),
            (x_max, y_max),
            (x_max, y_min),
            (x_min, y_min),
        ]
    return [
        (x_min, y_max - c),
        (x_min + c, y_max),
        (x_max - c, y_max),
        (x_max, y_max - c),
        (x_max, y_min + c),
        (x_max - c, y_min),
        (x_min + c, y_min),
        (x_min, y_min + c),
    ]


# 数字・記号ごとの点灯セグメント定義
DIGIT_SEGMENTS: Dict[str, List[str]] = {
    "zero":  ["A", "B", "C", "D", "E", "F"],
    "one":   ["B", "C"],
    "two":   ["A", "B", "G", "E", "D"],
    "three": ["A", "B", "G", "C", "D"],
    "four":  ["F", "G", "B", "C"],
    "five":  ["A", "F", "G", "C", "D"],
    "six":   ["A", "F", "G", "E", "C", "D"],
    "seven": ["A", "B", "C"],
    "eight": ["A", "B", "C", "D", "E", "F", "G"],
    "nine":  ["A", "B", "C", "D", "F", "G"],
}


def transform_polygons(polygons: List[Polygon], slant_deg: float) -> List[Polygon]:
    """
    指定されたスラント角 (例: 0.0° または -7.0°) に基づいてポリゴン群をシアー変換し、
    整数座標へ丸める。
    前傾 -7.0° は上に行くほど右(+X)へ傾く（x' = x + (y - Y_BASE) * tan(|slant_deg|)）。
    """
    shear = math.tan(math.radians(abs(slant_deg))) if slant_deg != 0.0 else 0.0
    result: List[Polygon] = []
    for poly in polygons:
        new_poly: Polygon = []
        for x, y in poly:
            nx = round(x + (y - Y_BASE) * shear)
            ny = round(y)
            new_poly.append((nx, ny))
        result.append(new_poly)
    return result


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


def build_strict_7seg_font(
    output_path: str,
    family_name: str,
    style_name: str,
    ps_name: str,
    slant_deg: float = 0.0,
):
    """
    指定パラメータで FDS7Strict TrueType フォントをゼロスクラッチでビルドし保存する。
    """
    segments = get_base_segments()

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

    # 1. .notdef (外枠豆腐、非表示に近い極細枠または空グリフ)
    notdef_poly = [
        [(40, 850), (360, 850), (360, 50), (40, 50)],
        [(80, 90), (320, 90), (320, 810), (80, 810)],  # 内穴は反時計回り (CCW)
    ]
    glyphs[".notdef"] = build_tt_glyph(transform_polygons(notdef_poly, slant_deg))
    metrics[".notdef"] = (540, 40)

    # 2. space (空白: 桁アドバンス幅 460 units — 数字1桁分より少し引き締まった実機空白ピッチ)
    glyphs["space"] = build_tt_glyph([])
    metrics["space"] = (460, 0)

    # 3. 数字 0 〜 9 (Advance Width: 540 units = 描画幅400 + 字間140)
    for gname, seg_keys in DIGIT_SEGMENTS.items():
        polys = [segments[k] for k in seg_keys]
        t_polys = transform_polygons(polys, slant_deg)
        glyphs[gname] = build_tt_glyph(t_polys)
        lsb = min(pt[0] for p in t_polys for pt in p)
        metrics[gname] = (540, int(lsb))

    # 4. quotesingle (' アポストロフィ: X: 220..300, Y: 690..830, 幅80×高さ140, Advance Width: 360)
    # 仕様書 6.5.1: 文字高の上部 70%〜95% に浮遊する独立した傾斜ドット
    apos_poly = [make_chamfered_box(220, 690, 300, 830, chamfer=8.0)]
    t_apos = transform_polygons(apos_poly, slant_deg)
    glyphs["quotesingle"] = build_tt_glyph(t_apos)
    metrics["quotesingle"] = (360, int(min(pt[0] for p in t_apos for pt in p)))

    # 5. colon (: コロン: X: 160..240, 下ドット Y: 210..290, 上ドット Y: 610..690, Advance Width: 400)
    # 仕様書 6.5.2: 80×80 units の微小角丸ドットが上下2点配置
    colon_polys = [
        make_chamfered_box(160, 210, 240, 290, chamfer=12.0),
        make_chamfered_box(160, 610, 240, 690, chamfer=12.0),
    ]
    t_colon = transform_polygons(colon_polys, slant_deg)
    glyphs["colon"] = build_tt_glyph(t_colon)
    metrics["colon"] = (400, int(min(pt[0] for p in t_colon for pt in p)))

    # 6. hyphen (- ハイフン: Segment G と完全同一 X: 54..346, Y: 410..490, Advance Width: 540)
    # 仕様書 6.5.3
    hyphen_polys = [segments["G"]]
    t_hyphen = transform_polygons(hyphen_polys, slant_deg)
    glyphs["hyphen"] = build_tt_glyph(t_hyphen)
    metrics["hyphen"] = (540, int(min(pt[0] for p in t_hyphen for pt in p)))

    # 7. period (. ピリオド: 右下DP素子 80×80 units, Y: 50..130)
    #    ※仕様書 6.5.4 (80×80 units, Y: 50..130)。
    #    先行する数字の右下に密着させつつ、後続の数字との字間も均等になるよう X: 60..140, Advance Width: 260 に配置
    period_polys = [make_chamfered_box(60, 50, 140, 130, chamfer=12.0)]
    t_period = transform_polygons(period_polys, slant_deg)
    glyphs["period"] = build_tt_glyph(t_period)
    metrics["period"] = (260, int(min(pt[0] for p in t_period for pt in p)))

    # 8. slash (/ スラッシュ: 日付区切りフォールバック用)
    slash_poly: Polygon = [
        (120, 130),
        (260, 770),
        (320, 770),
        (180, 130),
    ]
    t_slash = transform_polygons([slash_poly], slant_deg)
    glyphs["slash"] = build_tt_glyph(t_slash)
    metrics["slash"] = (460, int(min(pt[0] for p in t_slash for pt in p)))

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
        0x002E: "period",       # . Period / Decimal Point
        0x002C: "period",       # , Comma fallback
        0x002F: "slash",        # / Slash
    }

    # FontBuilder による TTF 構築
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
        "version": "Version 1.000; 1980s Suwa Seikosha Strict Spec",
        "psName": ps_name,
    }
    fb.setupNameTable(name_strings)

    italic_angle = float(slant_deg)
    fb.setupOS2(
        sTypoAscender=ASCENDER,
        sTypoDescender=DESCENDER,
        sTypoLineGap=0,
        usWinAscent=ASCENDER,
        usWinDescent=abs(DESCENDER),
        sxHeight=450,
        sCapHeight=CAP_HEIGHT,
        usWeightClass=700,
        fsSelection=0x0040 if slant_deg == 0.0 else 0x0001,
    )
    fb.setupPost(italicAngle=italic_angle, isFixedPitch=0)
    mac_style = 0x0002 if slant_deg != 0.0 else 0x0000
    # Mac epoch (1904-01-01) からの秒数: 2026-01-01 00:00:00 UTC = 3850080000
    ts_2026 = 3850080000
    fb.setupHead(unitsPerEm=UPM, macStyle=mac_style, created=ts_2026, modified=ts_2026)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fb.save(output_path)
    print(f"[OK] Built strict 7-segment font: {output_path} (slant={slant_deg} deg)")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fonts_dir = os.path.join(os.path.dirname(script_dir), "fonts")

    # 1. FDS7Strict-SLR.ttf (0.0° 直立型 / 一眼レフデータバック調)
    slr_path = os.path.join(fonts_dir, "FDS7Strict-SLR.ttf")
    build_strict_7seg_font(
        output_path=slr_path,
        family_name="FDS7 Strict SLR",
        style_name="Regular",
        ps_name="FDS7Strict-SLR",
        slant_deg=0.0,
    )

    # 2. FDS7Strict-Compact.ttf (-7.0° 前傾型 / 80sコンパクト機調)
    compact_path = os.path.join(fonts_dir, "FDS7Strict-Compact.ttf")
    build_strict_7seg_font(
        output_path=compact_path,
        family_name="FDS7 Strict Compact",
        style_name="Italic",
        ps_name="FDS7Strict-Compact",
        slant_deg=-7.0,
    )


if __name__ == "__main__":
    main()
