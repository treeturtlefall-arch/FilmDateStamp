"""
DSEG7 / DSEG14 フォントのアポストロフィ (U+0027) グリフおよび字幅を最適化するパッチスクリプト
SIL Open Font License 1.1 の改変・再配布条項に準拠。
"""
import copy
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates


def patch_dseg_apostrophe(target_path: str, source_dseg14_path: str):
    font_target = TTFont(target_path)
    font14 = TTFont(source_dseg14_path)

    src_glyph = font14["glyf"]["quotesingle"]
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

    font_target.save(target_path)
    print(f"Patched {target_path} successfully!")


if __name__ == "__main__":
    patch_dseg_apostrophe("fonts/DSEG7Classic-Bold.ttf", "fonts/DSEG14Classic-Bold.ttf")
    patch_dseg_apostrophe("fonts/DSEG7Classic-BoldItalic.ttf", "fonts/DSEG14Classic-BoldItalic.ttf")
    patch_dseg_apostrophe("fonts/DSEG14Classic-Bold.ttf", "fonts/DSEG14Classic-Bold.ttf")
    patch_dseg_apostrophe("fonts/DSEG14Classic-BoldItalic.ttf", "fonts/DSEG14Classic-BoldItalic.ttf")
