"""
FDS-Mechanical70s (1970s 機械式活字・タングステン電球光学縮小投影)
徹底比較・検証レンダリングスクリプト

出力先: assets/fds_mechanical_strict_comparison_report.png

検証ポイント:
1. モノクロ銀塩写真背景における「純白紙白（Paper White, #F8F6F0）」の発色と、
   未感光キャパシティ（Headroom）によるハイライト埋もれの再現。
2. 70sヴィンテージカラー写真背景における「タングステン温白色・象牙色（Bulb Warm Ivory, #FFF2CC）」
   および電球色アンバー（Bulb Amber）の電球光の質感。
3. 80s 7セグLED（FDS7Strict）や 90s ドット（FDSDotStrict）との世代間比較による、
   DIN 1451 / JIS工業彫刻活字ならではの重厚なレトロ感。
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

from film_config import DateStampConfig
from film_stamp import render_film_date_stamp, render_date_mask, get_font_file_and_shear

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def load_jp_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/meiryo.ttc",
        "C:/Windows/Fonts/YuGothB.ttc",
        "C:/Windows/Fonts/msgothic.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def make_synthetic_photo_bg(vw: int, vh: int, crop_w: int, crop_h: int, bg_type: str, seed: int = 74) -> Image.Image:
    """70sモノクロ銀塩写真（暗部〜ハイライト階調）および70sヴィンテージカラー背景を合成"""
    rng = np.random.default_rng(seed)
    bg_np = np.zeros((vh, vw, 3), dtype=np.float32)

    x0, y0 = vw - crop_w, vh - crop_h
    yy, xx = np.mgrid[0:crop_h, 0:crop_w].astype(np.float32)
    rx = xx / max(1.0, float(crop_w - 1))
    ry = yy / max(1.0, float(crop_h - 1))

    if bg_type == "mono_dark":
        # Tri-X / Neopan SS 暗室プリントのシャドウ〜中間調 (Paper White が鮮明に浮かび上がる)
        luma = 0.10 + 0.18 * rx + 0.06 * np.sin(ry * 6.0)
        grain = rng.normal(0.0, 0.018, (crop_h, crop_w)).astype(np.float32)
        val = np.clip(luma + grain, 0.04, 0.45)
        patch = np.stack([val * 0.98, val * 0.98, val * 0.96], axis=-1)
    elif bg_type == "mono_highlight_gradient":
        # 左側シャドウ (0.12) から右側ハイライト白飛び (0.96) への連続グラデーション（Headroom埋もれ検証）
        luma = np.clip(0.10 + 0.88 * (rx ** 1.35), 0.08, 0.97)
        grain = rng.normal(0.0, 0.014, (crop_h, crop_w)).astype(np.float32) * (1.0 - 0.6 * luma)
        val = np.clip(luma + grain, 0.05, 0.98)
        patch = np.stack([val * 0.97, val * 0.96, val * 0.94], axis=-1)
    elif bg_type == "vintage_70s_color":
        # Kodacolor II / Fujicolor F-II 70s ウォームヴィンテージカラー
        r = 0.20 + 0.22 * rx + 0.05 * ry
        g = 0.16 + 0.16 * rx + 0.04 * ry
        b = 0.11 + 0.10 * rx + 0.02 * ry
        grain = rng.normal(0.0, 0.015, (crop_h, crop_w, 1)).astype(np.float32)
        patch = np.clip(np.stack([r, g, b], axis=-1) + grain, 0.05, 0.65)
    else:
        # 70s 室内タングステン・夕景ディープシャドウ
        r = 0.12 + 0.14 * rx
        g = 0.10 + 0.11 * rx
        b = 0.13 + 0.09 * rx
        grain = rng.normal(0.0, 0.015, (crop_h, crop_w, 1)).astype(np.float32)
        patch = np.clip(np.stack([r, g, b], axis=-1) + grain, 0.04, 0.50)

    bg_np[y0:vh, x0:vw] = patch
    return Image.fromarray((bg_np * 255.0 + 0.5).astype(np.uint8))


def render_stamp_crop(
    font_type: str,
    date_str: str,
    preset_color: str,
    exposure: float = 1.05,
    core_glow: float = 0.85,
    halation: float = 0.75,
    irregularity: float = 0.75,
    font_scale: float = 1.15,
    crop_w: int = 470,
    crop_h: int = 108,
    bg_type: str = "mono_dark",
) -> Image.Image:
    """仮想写真 (1280x960) の右下にスタンプを露光合成し、検証領域をクロップ"""
    vw, vh = 1280, 960
    bg = make_synthetic_photo_bg(vw, vh, crop_w, crop_h, bg_type=bg_type)
    x0, y0 = vw - crop_w, vh - crop_h

    cfg = DateStampConfig(
        font_type=font_type,
        date_string=date_str,
        preset_color=preset_color,
        exposure_intensity=exposure,
        core_glow=core_glow,
        halation=halation,
        irregularity=irregularity,
        show_time=(":" in date_str),
        font_scale=font_scale,
        margin_x=0.75,
        margin_y=0.75,
        optical_burn=True,
    )
    stamped = render_film_date_stamp(bg, config=cfg, seed=74)
    return stamped.crop((x0, y0, vw, vh))


def generate_strict_mechanical_comparison_report():
    W, H = 1600, 1520
    canvas = Image.new("RGB", (W, H), (15, 17, 22))
    draw = ImageDraw.Draw(canvas)

    f_title = load_jp_font(24)
    f_sub = load_jp_font(15)
    f_sec = load_jp_font(20)
    f_label = load_jp_font(17)
    f_small = load_jp_font(14)

    # ヘッダー
    draw.text(
        (40, 22),
        "FilmDateStamp - 『FDS-Mechanical70s』1970年代 機械式活字・タングステン電球縮小投影 光学比較検証レポート",
        fill=(248, 246, 240),
        font=f_title,
    )
    draw.text(
        (40, 60),
        "Canon Canodate E (1970) / Datematic (1974) / Data Back A (1977) 完全準拠：モノクロ純白紙白 (#F8F6F0)・ハイライト埋もれ・タングステン温白色 (#FFF2CC)",
        fill=(185, 195, 215),
        font=f_sub,
    )
    draw.line([(40, 94), (W - 40, 94)], fill=(65, 72, 88), width=2)

    # ==========================================================================
    # Section 1: 1970s 発光物理検証（モノクロ純白 Paper White & ハイライト埋もれ / 70s タングステン温白色）
    # ==========================================================================
    y_cursor = 108
    draw.text(
        (40, y_cursor),
        "【1】1970s 銀塩光学物理検証：モノクローム紙白（Paper White #F8F6F0 & ハイライト埋もれ） vs 70s カラー電球光（Bulb Warm Ivory #FFF2CC）",
        fill=(255, 225, 150),
        font=f_sec,
    )
    y_cursor += 34

    phys_cards = [
        {
            "title": "① モノクロ銀塩 暗部〜中間調: Paper White (#F8F6F0)",
            "desc": "ネガ上のDmax遮光により印画紙の純白（バライタ紙白）が白抜き発現",
            "date_str": "'71 12 25",
            "preset_color": "Paper White (Monochrome)",
            "bg_type": "mono_dark",
            "exposure": 1.10,
            "core_glow": 0.90,
            "halation": 0.45,
            "badge": (95, 100, 112),
        },
        {
            "title": "② モノクロ ハイライト埋もれ検証 (Headroom Saturation)",
            "desc": "背景が明るい空や白壁（右側）に向かい、未感光余力が尽きて白に自然同化",
            "date_str": "'74 08 15",
            "preset_color": "Paper White (Monochrome)",
            "bg_type": "mono_highlight_gradient",
            "exposure": 1.05,
            "core_glow": 0.85,
            "halation": 0.45,
            "badge": (115, 120, 135),
        },
        {
            "title": "③ 70s ヴィンテージカラー: Bulb Warm Ivory (#FFF2CC)",
            "desc": "2600Kタングステン豆電球の連続スペクトルによる温かい象牙色〜琥珀フレア",
            "date_str": "'74 11 03",
            "preset_color": "Bulb Warm Ivory",
            "bg_type": "vintage_70s_color",
            "exposure": 1.10,
            "core_glow": 0.90,
            "halation": 0.85,
            "badge": (185, 130, 45),
        },
    ]

    card_w = 492
    card_h = 200
    for idx, pc in enumerate(phys_cards):
        cx = 40 + idx * (card_w + 22)
        draw.rounded_rectangle([(cx, y_cursor), (cx + card_w, y_cursor + card_h)], radius=8, fill=(24, 27, 34), outline=(65, 75, 92))
        draw.rounded_rectangle([(cx + 12, y_cursor + 10), (cx + card_w - 12, y_cursor + 40)], radius=4, fill=pc["badge"])
        draw.text((cx + 20, y_cursor + 13), pc["title"], fill=(255, 255, 255), font=f_label)
        draw.text((cx + 14, y_cursor + 46), pc["desc"], fill=(210, 220, 235), font=f_small)

        crop = render_stamp_crop(
            font_type="FDS_Mechanical_70s (70s Mechanical)",
            date_str=pc["date_str"],
            preset_color=pc["preset_color"],
            exposure=pc["exposure"],
            core_glow=pc["core_glow"],
            halation=pc["halation"],
            crop_w=card_w - 24,
            crop_h=112,
            bg_type=pc["bg_type"],
        )
        canvas.paste(crop, (cx + 12, y_cursor + 74))
        draw.rectangle([(cx + 12, y_cursor + 74), (cx + card_w - 12, y_cursor + 74 + 112)], outline=(95, 105, 125))

    y_cursor += card_h + 22

    # ==========================================================================
    # Section 2: 写真史3世代（70s 機械式活字 vs 80s 7セグLED vs 90s カプセルドット）徹底比較
    # ==========================================================================
    draw.text(
        (40, y_cursor),
        "【2】カメラ日付写し込み 3世代比較：70s 機械式活字 (FDSMechanical70s) vs 80s 7セグLED (FDS7Strict) vs 90s 写ルンですドット (FDSDotStrict)",
        fill=(255, 185, 95),
        font=f_sec,
    )
    y_cursor += 34

    gen_rows = [
        {
            "title": "第1世代 [1970s]: FDSMechanical70s-Regular (機械式活字ドラム + 2600K豆電球縮小投影)",
            "font_type": "FDS_Mechanical_70s (70s Mechanical)",
            "badge": (175, 125, 45),
            "note": "★DIN 1451 / JIS工業彫刻準拠: カプセル『0』・45°カギ鼻『1』・クローズド『4』・等幅620ピッチの重厚な活字感",
        },
        {
            "title": "第2世代 [1980s]: FDS7Strict-Compact (諏訪精工舎 7セグメントGaAsP赤色/アンバーLED)",
            "font_type": "FDS7_Strict_Compact (80s -7°)",
            "badge": (185, 70, 30),
            "note": "・80s クォーツデート標準: 前傾-7.0°、7分割セグメントギャップ、35°マイターカットによる電子回路的なシャープさ",
        },
        {
            "title": "第3世代 [1990s]: FDSDotStrict-Regular (写ルンです・90sコンパクト機 5×7カプセルドット)",
            "font_type": "FDS_Dot_Strict (90s Dot Matrix)",
            "badge": (140, 85, 45),
            "note": "・90s マイクロドットパルス露光: 5×7縦長カプセルドットが乳剤内で光学融合する軽快なスナップ感",
        },
    ]

    for row in gen_rows:
        rh = 166
        draw.rounded_rectangle([(40, y_cursor), (W - 40, y_cursor + rh)], radius=8, fill=(22, 26, 34), outline=(55, 64, 82))
        draw.rounded_rectangle([(55, y_cursor + 10), (55 + 735, y_cursor + 40)], radius=4, fill=row["badge"])
        draw.text((65, y_cursor + 13), row["title"], fill=(255, 255, 255), font=f_label)
        draw.text((805, y_cursor + 15), row["note"], fill=(215, 225, 240), font=f_small)

        # 左: モノクロ Paper White 比較
        c_mono = render_stamp_crop(
            font_type=row["font_type"],
            date_str="'74 10 14",
            preset_color="Paper White (Monochrome)",
            exposure=1.08,
            core_glow=0.85,
            halation=0.45,
            crop_w=465,
            crop_h=100,
            bg_type="mono_dark",
        )
        canvas.paste(c_mono, (55, y_cursor + 52))
        draw.rectangle([(55, y_cursor + 52), (55 + 465, y_cursor + 52 + 100)], outline=(85, 95, 115))
        draw.text((62, y_cursor + 56), "Monochrome Paper White ('74 10 14)", fill=(235, 235, 230), font=f_small)

        # 中: 70s Bulb Warm Ivory 比較
        c_ivory = render_stamp_crop(
            font_type=row["font_type"],
            date_str="'74 10 14",
            preset_color="Bulb Warm Ivory",
            exposure=1.10,
            core_glow=0.85,
            halation=0.85,
            crop_w=465,
            crop_h=100,
            bg_type="vintage_70s_color",
        )
        canvas.paste(c_ivory, (540, y_cursor + 52))
        draw.rectangle([(540, y_cursor + 52), (540 + 465, y_cursor + 52 + 100)], outline=(85, 95, 115))
        draw.text((547, y_cursor + 56), "70s Bulb Warm Ivory (#FFF2CC)", fill=(255, 242, 204), font=f_small)

        # 右: Bulb Amber / Classic 強露光比較
        c_amber = render_stamp_crop(
            font_type=row["font_type"],
            date_str="77-04-29",
            preset_color="Bulb Amber",
            exposure=1.18,
            core_glow=0.90,
            halation=1.15,
            crop_w=520,
            crop_h=100,
            bg_type="dark_tungsten",
        )
        canvas.paste(c_amber, (1025, y_cursor + 52))
        draw.rectangle([(1025, y_cursor + 52), (1025 + 520, y_cursor + 52 + 100)], outline=(85, 95, 115))
        draw.text((1032, y_cursor + 56), "Tungsten Amber Glow (77-04-29)", fill=(255, 210, 128), font=f_small)

        y_cursor += rh + 14

    # ==========================================================================
    # Section 3: 純粋ベクターマスク拡大検証（全収録グリフ & 1970s工業彫刻幾何特徴）
    # ==========================================================================
    y_cursor += 6
    draw.text(
        (40, y_cursor),
        "【3】純粋グリフマスク拡大検証：1000 UPM・等幅 620u・CapHeight 720u・ストローク厚 96u・角丸 R=20/12u の工業彫刻ジオメトリ",
        fill=(140, 225, 255),
        font=f_sec,
    )
    y_cursor += 32

    box_h = 370
    draw.rounded_rectangle([(40, y_cursor), (W - 40, y_cursor + box_h)], radius=8, fill=(20, 23, 30), outline=(60, 70, 90))

    glyph_rows = [
        (
            "NEW: FDSMechanical70s-Regular (1970s 機械式活字: カプセル『0』/ 45°カギ鼻『1』/ クローズド『4』/ 点対称『6,9』)",
            "FDS_Mechanical_70s (70s Mechanical)",
            (248, 246, 240),
        ),
        (
            "REF 1: FDS7Strict-SLR (1980s 7セグメントLED直立型: セグメント分割・六角テーパー)",
            "FDS7_Strict_SLR (80s 0°)",
            (255, 160, 90),
        ),
        (
            "REF 2: FDSDotStrict-Regular (1990s 5×7 カプセルドットマトリクス)",
            "FDS_Dot_Strict (90s Dot Matrix)",
            (160, 220, 255),
        ),
    ]

    sample_text = "'0123456789 - . : /"
    for idx, (label, ftype, col) in enumerate(glyph_rows):
        ry = y_cursor + 16 + idx * 116
        draw.text((60, ry), label, fill=col, font=f_label)
        fpath, shear = get_font_file_and_shear(ftype)
        mask, mw, mh = render_date_mask(sample_text, fpath, font_size=56, shear_deg=shear)
        mask_np = np.asarray(mask, dtype=np.float32) / 255.0
        rgb_mask = np.zeros((mh, mw, 3), dtype=np.uint8)
        rgb_mask[..., 0] = (mask_np * col[0]).astype(np.uint8)
        rgb_mask[..., 1] = (mask_np * col[1]).astype(np.uint8)
        rgb_mask[..., 2] = (mask_np * col[2]).astype(np.uint8)
        canvas.paste(Image.fromarray(rgb_mask), (60, ry + 32))

    # 右側ミクロ拡大ボックス: '0', '1', '4' の象徴的ディテール拡大
    micro_x = 1070
    micro_y = y_cursor + 16
    micro_w = 468
    micro_h = 338
    draw.rounded_rectangle([(micro_x, micro_y), (micro_x + micro_w, micro_y + micro_h)], radius=6, fill=(28, 32, 42), outline=(95, 110, 140))
    draw.text((micro_x + 16, micro_y + 12), "【ミクロ拡大】『'014』活字ディテール検証", fill=(255, 230, 145), font=f_label)

    mech_path, _ = get_font_file_and_shear("FDS_Mechanical_70s (70s Mechanical)")
    big_mask, bmw, bmh = render_date_mask("'014", mech_path, font_size=145, shear_deg=0.0)
    bm_np = np.asarray(big_mask, dtype=np.float32) / 255.0
    bm_rgb = np.zeros((bmh, bmw, 3), dtype=np.uint8)
    bm_rgb[..., 0] = (bm_np * 248).astype(np.uint8)
    bm_rgb[..., 1] = (bm_np * 242).astype(np.uint8)
    bm_rgb[..., 2] = (bm_np * 215).astype(np.uint8)
    canvas.paste(Image.fromarray(bm_rgb), (micro_x + 24, micro_y + 54))

    spec_notes = [
        "・『'』: 幅70・傾斜-18°の重厚なクォーツダッシュ",
        "・『0』: 左右垂直直線＋上下R=190半円のStadium形状",
        "         (広いカウンター幅188uで縮小投影時の黒潰れ防止)",
        "・『1』: 頂点から左下45°へ突き出すカギ鼻ビーク＋台座なし",
        "・『4』: 頂点が閉じたクローズド・トライアングル＋右突出バー",
    ]
    for i, note in enumerate(spec_notes):
        draw.text((micro_x + 18, micro_y + 195 + i * 26), note, fill=(215, 225, 240), font=f_small)

    out_path = os.path.join(ASSETS_DIR, "fds_mechanical_strict_comparison_report.png")
    canvas.save(out_path)
    print(f"[OK] Saved strict mechanical comparison report: {out_path}")


if __name__ == "__main__":
    generate_strict_mechanical_comparison_report()
