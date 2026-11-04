"""
FilmDateStamp プリセット・ショーケース画像生成スクリプト (日・英対応版)
candidate フォルダの実写写真 (2003年 SO505i) をベースに、
全スタイルプリセット（Japanese, American, European, Y2K など）を
各時代の質感・色味に合わせた本物の写真上に焼き付けたギャラリー画像を日・英両言語で生成する。
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

from film_config import STYLE_PRESETS, DateStampConfig
from film_stamp import render_film_date_stamp

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
CANDIDATE_DIR = os.path.join(PROJECT_DIR, "candidate")
os.makedirs(ASSETS_DIR, exist_ok=True)

# 実写写真のロード
def load_candidate_img(filename: str) -> Image.Image:
    path = os.path.join(CANDIDATE_DIR, filename)
    return Image.open(path).convert("RGB")

IMG_DSC04 = load_candidate_img("DSC00004.JPG")
IMG_DSC05 = load_candidate_img("DSC00005.JPG")
IMG_DSC08 = load_candidate_img("DSC00008.JPG")
IMG_DSC34 = load_candidate_img("DSC00034.JPG")
IMG_KINKAKU = load_candidate_img("金閣寺.JPG")


def get_preset_background(preset_name: str, target_w: int, target_h: int) -> Image.Image:
    """各プリセットの世界観にマッチした実写切り出し＆トーン調整背景を返す"""
    if "Monochrome 70s" in preset_name:
        crop = IMG_KINKAKU.crop((200, 300, 1000, 700)).resize((target_w, target_h), Image.Resampling.LANCZOS)
        gray = ImageOps.grayscale(crop)
        arr = np.array(gray).astype(float)
        arr = np.clip((arr - 15) * 1.15, 0, 255).astype(np.uint8)
        return Image.fromarray(np.stack([arr, arr, arr], axis=-1))

    elif "Vintage 70s Color" in preset_name:
        crop = IMG_DSC04.crop((100, 400, 900, 800)).resize((target_w, target_h), Image.Resampling.LANCZOS)
        arr = np.array(crop).astype(float)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.15 + 10, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.05 + 5, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.85, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    elif "Japanese Tokyo 90s" in preset_name:
        return IMG_DSC04.crop((200, 480, 1200, 960)).resize((target_w, target_h), Image.Resampling.LANCZOS)

    elif "Japanese Snap (Disposable)" in preset_name:
        return IMG_KINKAKU.crop((300, 350, 1280, 850)).resize((target_w, target_h), Image.Resampling.LANCZOS)

    elif "American West Coast" in preset_name:
        crop = IMG_DSC08.crop((100, 200, 1100, 750)).resize((target_w, target_h), Image.Resampling.LANCZOS)
        arr = np.array(crop).astype(float)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.12 + 15, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.05 + 5, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    elif "American 80s (Red Quartz)" in preset_name:
        return IMG_DSC34.crop((100, 480, 1100, 960)).resize((target_w, target_h), Image.Resampling.LANCZOS)

    elif "European Classic" in preset_name:
        crop = IMG_DSC08.crop((200, 400, 1100, 900)).resize((target_w, target_h), Image.Resampling.LANCZOS)
        arr = np.array(crop).astype(float)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.10, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    elif "Y2K Digicam" in preset_name:
        return IMG_DSC05.crop((100, 400, 1100, 900)).resize((target_w, target_h), Image.Resampling.LANCZOS)

    elif "Compact Fine Dot" in preset_name:
        return IMG_DSC34.crop((300, 500, 1250, 950)).resize((target_w, target_h), Image.Resampling.LANCZOS)

    elif "Cyber Telemetry" in preset_name:
        crop = IMG_DSC04.crop((200, 480, 1100, 900)).resize((target_w, target_h), Image.Resampling.LANCZOS)
        arr = np.array(crop).astype(float)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.40, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.25 + 15, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.35 + 20, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    elif "Y2K Pop" in preset_name:
        return IMG_DSC05.crop((200, 300, 1200, 800)).resize((target_w, target_h), Image.Resampling.LANCZOS)

    elif "Arcane Occult" in preset_name:
        crop = IMG_DSC08.crop((0, 350, 900, 850)).resize((target_w, target_h), Image.Resampling.LANCZOS)
        arr = np.array(crop).astype(float)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.30 + 20, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 0.50, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.40, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    return IMG_DSC04.crop((200, 480, 1200, 960)).resize((target_w, target_h), Image.Resampling.LANCZOS)


PRESETS_JA = [
    ("Monochrome 70s (Canodate E)", "70年代銀塩モノクロ（YY MM DD / 機械式彫刻活字 / 印画紙白抜き）"),
    ("Vintage 70s Color (Datematic)", "70年代カラー（'YY MM DD / 機械式彫刻活字 / 電球色ウォームアイボリー）"),
    ("Japanese Tokyo 90s", "90年代日本の街角・日常スナップ（'YY MM DD / 80s 7セグ-7° / アンバー）"),
    ("Japanese Snap (Disposable)", "写ルンです風使い捨てカメラ（'YY MM DD HH:MM / 5×7カプセルドット / オレンジ）"),
    ("American West Coast", "90s西海岸・ロードトリップ（MM DD 'YY / 80s 7セグ-7° / ゴールデン）"),
    ("American 80s (Red Quartz)", "80年代モーテル・一眼レフ調（MM DD 'YY / 80s 7セグ直立 / クォーツレッド）"),
    ("European Classic (Paris/Berlin)", "欧州の石畳・上品な佇まい（DD.MM.YY / 80s 7セグ直立 / 控えめアンバー）"),
    ("Y2K Digicam (Early 2000s)", "2000年代初期コンデジLCD液晶（'YY MM DD HH:MM / 液晶等幅 / ゴールデン）"),
    ("Compact Fine Dot (Minimal)", "90sコンパクト機微細ドット（'YY MM DD HH:MM / カプセルドット / オレンジ）"),
    ("Cyber Telemetry (80s Sci-Fi)", "80s-90s宇宙探査・SF映画調（'YY MM DD HH:MM:SS / Michroma / サイバーグリーン）"),
    ("Y2K Pop (Heisei Fancy)", "平成トイカメラ・プリクラ電飾（'YY MM DD HH:MM / お餅丸文字 / ネオピンク）"),
    ("Arcane Occult (Crimson Script)", "禁断の魔導書・錬金術師の野帳（'YY MM DD / 古文書インク筆記 / 深紅）"),
]

PRESETS_EN = [
    ("Monochrome 70s (Canodate E)", "70s B&W silver print (YY MM DD / Mechanical engraving / Paper white)"),
    ("Vintage 70s Color (Datematic)", "70s warm color print ('YY MM DD / Mechanical engraving / Warm ivory bulb)"),
    ("Japanese Tokyo 90s", "90s Tokyo street snapshot ('YY MM DD / 80s 7-seg -7° slant / Amber Classic)"),
    ("Japanese Snap (Disposable)", "Disposable camera snapshot ('YY MM DD HH:MM / 5x7 Capsule Dot / Fuji Orange)"),
    ("American West Coast", "90s West Coast road trip (MM DD 'YY / 80s 7-seg -7° slant / Golden Yellow)"),
    ("American 80s (Red Quartz)", "80s motel & SLR data back (MM DD 'YY / 80s 7-seg 0° upright / Quartz Red)"),
    ("European Classic (Paris/Berlin)", "European cobblestone aesthetic (DD.MM.YY / 80s 7-seg 0° upright / Subtle Amber)"),
    ("Y2K Digicam (Early 2000s)", "Early 2000s compact digital LCD ('YY MM DD HH:MM / Monospace LCD / Golden Yellow)"),
    ("Compact Fine Dot (Minimal)", "90s high-end compact fine dots ('YY MM DD HH:MM / Capsule Dot / Fuji Orange)"),
    ("Cyber Telemetry (80s Sci-Fi)", "80s-90s space probe HUD ('YY MM DD HH:MM:SS / Michroma / Cyber Green)"),
    ("Y2K Pop (Heisei Fancy)", "Heisei retro toy camera & Purikura ('YY MM DD HH:MM / MochiyPop / Neo Pink)"),
    ("Arcane Occult (Crimson Script)", "Ancient alchemical grimoire ('YY MM DD / EagleLake cursive / Crimson Red)"),
]


def render_gallery(presets_list, is_english=False):
    card_w = 620
    card_h = 240
    cols = 2
    rows = (len(presets_list) + cols - 1) // cols

    padding = 30
    header_h = 100
    total_w = padding * 3 + card_w * cols
    total_h = header_h + padding + (card_h + padding) * rows

    canvas = Image.new("RGB", (total_w, total_h), (14, 16, 22))
    draw = ImageDraw.Draw(canvas)

    if is_english:
        f_title = "C:/Windows/Fonts/segoeuib.ttf"
        f_sub = "C:/Windows/Fonts/segoeui.ttf"
        title_font = ImageFont.truetype(f_title, 26) if os.path.exists(f_title) else ImageFont.load_default()
        subtitle_font = ImageFont.truetype(f_sub, 15) if os.path.exists(f_sub) else ImageFont.load_default()
        card_title_font = ImageFont.truetype(f_title, 18) if os.path.exists(f_title) else ImageFont.load_default()
        card_desc_font = ImageFont.truetype(f_sub, 13) if os.path.exists(f_sub) else ImageFont.load_default()

        hdr_title = "FilmDateStamp - Era & Aesthetic Presets Gallery"
        hdr_sub = "Authentic photo gallery demonstrating 12 era-defining styles on vintage photographic emulsion"
    else:
        jp_candidates = ["C:/Windows/Fonts/meiryo.ttc", "C:/Windows/Fonts/YuGothB.ttc", "C:/Windows/Fonts/msgothic.ttc"]
        jp_path = next((c for c in jp_candidates if os.path.exists(c)), None)
        title_font = ImageFont.truetype(jp_path, 26) if jp_path else ImageFont.load_default()
        subtitle_font = ImageFont.truetype(jp_path, 15) if jp_path else ImageFont.load_default()
        card_title_font = ImageFont.truetype(jp_path, 18) if jp_path else ImageFont.load_default()
        card_desc_font = ImageFont.truetype(jp_path, 13) if jp_path else ImageFont.load_default()

        hdr_title = "FilmDateStamp - 新スタイルプリセット ショーケース"
        hdr_sub = "地域・文化・時代を想起させる日付スタンププリセットのレンダリング一覧"

    draw.text((padding, 25), hdr_title, fill=(255, 255, 255), font=title_font)
    draw.text((padding, 65), hdr_sub, fill=(170, 180, 195), font=subtitle_font)
    draw.line([(padding, 95), (total_w - padding, 95)], fill=(40, 48, 64), width=1)

    for idx, (preset_name, desc) in enumerate(presets_list):
        col = idx % cols
        row = idx // cols

        x = padding + col * (card_w + padding)
        y = header_h + padding + row * (card_h + padding)

        # カード外枠
        draw.rounded_rectangle([(x, y), (x + card_w, y + card_h)], radius=12, fill=(20, 24, 32), outline=(48, 56, 72))

        # カードヘッダー情報
        draw.text((x + 18, y + 14), preset_name, fill=(245, 248, 255), font=card_title_font)
        draw.text((x + 18, y + 42), desc, fill=(155, 165, 180), font=card_desc_font)

        # プレビュー画像枠
        pv_w = card_w - 36
        pv_h = 160
        pv_x = x + 18
        pv_y = y + 66

        pv_img = get_preset_background(preset_name, pv_w, pv_h)

        cfg = DateStampConfig(style_preset=preset_name)
        cfg.apply_style_preset_if_set()
        cfg.font_scale = cfg.font_scale * 1.05

        stamped_pv = render_film_date_stamp(pv_img, config=cfg)
        canvas.paste(stamped_pv, (pv_x, pv_y))
        draw.rounded_rectangle([(pv_x, pv_y), (pv_x + pv_w, pv_y + pv_h)], radius=4, outline=(70, 80, 100))

    return canvas


def generate_all_showcases():
    print("Generating English presets showcase...")
    canvas_en = render_gallery(PRESETS_EN, is_english=True)
    out_en = os.path.join(ASSETS_DIR, "presets_showcase_en.png")
    out_default = os.path.join(ASSETS_DIR, "presets_showcase.png")
    canvas_en.save(out_en, quality=95)
    canvas_en.save(out_default, quality=95)
    print(f"Saved: {out_en}")
    print(f"Saved (default): {out_default}")

    print("Generating Japanese presets showcase...")
    canvas_ja = render_gallery(PRESETS_JA, is_english=False)
    out_ja = os.path.join(ASSETS_DIR, "presets_showcase_ja.png")
    canvas_ja.save(out_ja, quality=95)
    print(f"Saved: {out_ja}")


if __name__ == "__main__":
    generate_all_showcases()
