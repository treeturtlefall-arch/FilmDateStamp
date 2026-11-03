"""
DSEG7 / DSEG14 フォントのアポストロフィ (U+0027) グリフおよび字幅を最適化し、
SIL Open Font License 1.1 Section 3 (Reserved Font Name) に準拠するため
派生フォント名 (FDS7Classic / FDS14Classic) へ名称を変更して生成するパッチスクリプト。
"""
import copy
import os
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates


def rename_font_records(font: TTFont, old_prefix: str, new_prefix: str, family_name: str):
    """
    OFL 1.1 Section 3 に準拠するため、フォント内の name テーブルを書き換えて
    Reserved Font Name の使用を回避する。
    """
    for record in font["name"].names:
        text = record.toUnicode()
        if old_prefix in text:
            new_text = text.replace(old_prefix, new_prefix)
            # nameID 1 (Family name) は明確に新ファミリー名にする
            if record.nameID == 1:
                new_text = family_name
            font["name"].setName(
                new_text,
                record.nameID,
                record.platformID,
                record.platEncID,
                record.langID,
            )


def patch_and_derive_segment_font(
    source_target_path: str,
    source_glyph_path: str,
    output_path: str,
    old_prefix: str,
    new_prefix: str,
    family_name: str,
):
    font_target = TTFont(source_target_path)
    font_glyph_src = TTFont(source_glyph_path)

    src_glyph = font_glyph_src["glyf"]["quotesingle"]
    coords = list(src_glyph.coordinates)
    flags = list(src_glyph.flags)

    # クォーツデート表記 ('98) で数字の直前に気持ちよく収まるよう、
    # 送り幅を 460 に設定し、グリフを右寄り (x=220〜) に配置
    min_x = min(pt[0] for pt in coords)
    target_x = 220
    shift_x = target_x - min_x

    new_coords = [(pt[0] + shift_x, pt[1]) for pt in coords]

    new_glyph = Glyph()
    new_glyph.numberOfContours = src_glyph.numberOfContours
    new_glyph.endPtsOfContours = list(src_glyph.endPtsOfContours)
    new_glyph.coordinates = GlyphCoordinates(new_coords)
    new_glyph.flags = bytearray(flags)
    new_glyph.program = copy.deepcopy(src_glyph.program) if hasattr(src_glyph, "program") else None
    new_glyph.xMin = min(pt[0] for pt in new_coords)
    new_glyph.xMax = max(pt[0] for pt in new_coords)
    new_glyph.yMin = min(pt[1] for pt in new_coords)
    new_glyph.yMax = max(pt[1] for pt in new_coords)

    glyph_name = "quotesingle" if "quotesingle" in font_target.getGlyphOrder() else "apostrophe"
    font_target["glyf"][glyph_name] = new_glyph
    font_target["hmtx"][glyph_name] = (460, new_glyph.xMin)

    if glyph_name not in font_target.getGlyphOrder():
        font_target.setGlyphOrder(font_target.getGlyphOrder() + [glyph_name])

    for table in font_target["cmap"].tables:
        if table.format == 0:
            table.cmap[0x27] = glyph_name
            table.cmap[0x60] = glyph_name
            table.cmap[0x2C] = glyph_name
        else:
            table.cmap[0x27] = glyph_name
            table.cmap[0x60] = glyph_name
            table.cmap[0x2C] = glyph_name
            table.cmap[0x2018] = glyph_name
            table.cmap[0x2019] = glyph_name
            table.cmap[0x201B] = glyph_name

    # リネーム（Reserved Font Name 対策）
    rename_font_records(font_target, old_prefix, new_prefix, family_name)

    font_target.save(output_path)
    print(f"Generated compliant derivative font: {output_path}")


if __name__ == "__main__":
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
    
    # 7-Segment Bold
    patch_and_derive_segment_font(
        source_target_path=os.path.join(fonts_dir, "DSEG7Classic-Bold.ttf"),
        source_glyph_path=os.path.join(fonts_dir, "DSEG14Classic-Bold.ttf"),
        output_path=os.path.join(fonts_dir, "FDS7Classic-Bold.ttf"),
        old_prefix="DSEG7",
        new_prefix="FDS7",
        family_name="FDS7 Classic",
    )
    # 7-Segment BoldItalic
    patch_and_derive_segment_font(
        source_target_path=os.path.join(fonts_dir, "DSEG7Classic-BoldItalic.ttf"),
        source_glyph_path=os.path.join(fonts_dir, "DSEG14Classic-BoldItalic.ttf"),
        output_path=os.path.join(fonts_dir, "FDS7Classic-BoldItalic.ttf"),
        old_prefix="DSEG7",
        new_prefix="FDS7",
        family_name="FDS7 Classic",
    )
    # 14-Segment Bold
    patch_and_derive_segment_font(
        source_target_path=os.path.join(fonts_dir, "DSEG14Classic-Bold.ttf"),
        source_glyph_path=os.path.join(fonts_dir, "DSEG14Classic-Bold.ttf"),
        output_path=os.path.join(fonts_dir, "FDS14Classic-Bold.ttf"),
        old_prefix="DSEG14",
        new_prefix="FDS14",
        family_name="FDS14 Classic",
    )
    # 14-Segment BoldItalic
    patch_and_derive_segment_font(
        source_target_path=os.path.join(fonts_dir, "DSEG14Classic-BoldItalic.ttf"),
        source_glyph_path=os.path.join(fonts_dir, "DSEG14Classic-BoldItalic.ttf"),
        output_path=os.path.join(fonts_dir, "FDS14Classic-BoldItalic.ttf"),
        old_prefix="DSEG14",
        new_prefix="FDS14",
        family_name="FDS14 Classic",
    )
