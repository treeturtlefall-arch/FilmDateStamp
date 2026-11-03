"""
FilmDateStamp - 設定データクラス・カラープリセット・日付パーサー
"""
from dataclasses import dataclass, field
import datetime
import random
import re
from typing import Dict, Tuple, Optional

# プリセットカラーパレット定義 (Core, Body, Halation)
COLOR_PRESETS: Dict[str, Dict[str, Tuple[int, int, int]]] = {
    "Amber Classic": {
        "core": (255, 255, 210),
        "body": (255, 130, 20),
        "halation": (240, 45, 0),
    },
    "Quartz Red": {
        "core": (255, 230, 220),
        "body": (255, 40, 20),
        "halation": (200, 10, 0),
    },
    "Fuji Orange": {
        "core": (255, 250, 190),
        "body": (255, 110, 10),
        "halation": (250, 60, 10),
    },
    "Golden Yellow": {
        "core": (255, 255, 240),
        "body": (255, 185, 30),
        "halation": (240, 110, 0),
    },
    "Cyber Green": {
        "core": (230, 255, 230),
        "body": (40, 255, 80),
        "halation": (0, 180, 40),
    },
}

SUPPORTED_DATE_FORMATS = [
    "'YY MM DD",
    "MM DD 'YY",
    "DD MM 'YY",
    "DD.MM.YY",
    "YY-MM-DD",
    "YY.MM.DD",
    "YYYY MM DD",
    "YYYY-MM-DD",
]

SUPPORTED_POSITIONS = [
    "bottom_right",
    "bottom_left",
    "top_right",
    "top_left",
]

# 利用可能フォント定義 (フォントファイル名, シアー傾斜角度)
FONT_MAP: Dict[str, Tuple[str, float]] = {
    "DSEG7_Classic (7-Segment)": ("DSEG7Classic-Bold.ttf", 0.0),
    "DSEG7_Italic (7-Segment)": ("DSEG7Classic-BoldItalic.ttf", 0.0),
    "DSEG14_Classic (14-Segment)": ("DSEG14Classic-Bold.ttf", 0.0),
    "DSEG14_Italic (14-Segment)": ("DSEG14Classic-BoldItalic.ttf", 0.0),
    "VT323 (Dot Matrix)": ("VT323-Regular.ttf", 0.0),
    "Silkscreen (Fine Dot)": ("Silkscreen-Regular.ttf", 0.0),
    "ShareTechMono (LCD Digital)": ("ShareTechMono-Regular.ttf", 0.0),
}

SUPPORTED_FONTS = list(FONT_MAP.keys())

# スタイル一括プリセット定義（地域・時代・文化ベース）
STYLE_PRESETS: Dict[str, Optional[Dict[str, object]]] = {
    "Custom": None,
    "Japanese Tokyo 90s": {
        "date_mode": "custom",
        "date_string": "'98 12 24",
        "date_format": "'YY MM DD",
        "show_time": False,
        "font_type": "DSEG7_Italic (7-Segment)",
        "preset_color": "Amber Classic",
        "exposure_intensity": 1.00,
        "core_glow": 1.00,
        "halation": 1.00,
        "optical_burn": True,
        "position": "bottom_right",
        "font_scale": 1.00,
        "margin_x": 1.00,
        "margin_y": 1.00,
    },
    "Japanese Snap (Disposable)": {
        "date_mode": "custom",
        "date_string": "'98 12 24 18:30",
        "date_format": "'YY MM DD",
        "show_time": True,
        "font_type": "VT323 (Dot Matrix)",
        "preset_color": "Fuji Orange",
        "exposure_intensity": 1.00,
        "core_glow": 0.50,
        "halation": 1.00,
        "optical_burn": True,
        "position": "bottom_right",
        "font_scale": 1.20,
        "margin_x": 1.50,
        "margin_y": 1.50,
    },
    "American West Coast": {
        "date_mode": "custom",
        "date_string": "12 24 '98",
        "date_format": "MM DD 'YY",
        "show_time": False,
        "font_type": "DSEG7_Italic (7-Segment)",
        "preset_color": "Golden Yellow",
        "exposure_intensity": 1.00,
        "core_glow": 0.85,
        "halation": 1.00,
        "optical_burn": True,
        "position": "bottom_right",
        "font_scale": 1.00,
        "margin_x": 1.00,
        "margin_y": 1.00,
    },
    "American 80s (Red Quartz)": {
        "date_mode": "custom",
        "date_string": "12 24 '88",
        "date_format": "MM DD 'YY",
        "show_time": False,
        "font_type": "DSEG7_Classic (7-Segment)",
        "preset_color": "Quartz Red",
        "exposure_intensity": 1.10,
        "core_glow": 1.00,
        "halation": 1.30,
        "optical_burn": True,
        "position": "bottom_right",
        "font_scale": 1.00,
        "margin_x": 1.00,
        "margin_y": 1.00,
    },
    "European Classic (Paris/Berlin)": {
        "date_mode": "custom",
        "date_string": "24.12.98",
        "date_format": "DD.MM.YY",
        "show_time": False,
        "font_type": "DSEG7_Classic (7-Segment)",
        "preset_color": "Amber Classic",
        "exposure_intensity": 0.90,
        "core_glow": 0.70,
        "halation": 0.80,
        "optical_burn": True,
        "position": "bottom_right",
        "font_scale": 0.95,
        "margin_x": 1.10,
        "margin_y": 1.10,
    },
    "Hong Kong Neon (90s Cinema)": {
        "date_mode": "custom",
        "date_string": "'94 05 01",
        "date_format": "'YY MM DD",
        "show_time": False,
        "font_type": "DSEG14_Italic (14-Segment)",
        "preset_color": "Cyber Green",
        "exposure_intensity": 1.20,
        "core_glow": 1.10,
        "halation": 1.60,
        "optical_burn": True,
        "position": "bottom_right",
        "font_scale": 1.05,
        "margin_x": 1.00,
        "margin_y": 1.00,
    },
    "Y2K Digicam (Early 2000s)": {
        "date_mode": "custom",
        "date_string": "'03 08 15 14:20",
        "date_format": "'YY MM DD",
        "show_time": True,
        "font_type": "ShareTechMono (LCD Digital)",
        "preset_color": "Golden Yellow",
        "exposure_intensity": 1.05,
        "core_glow": 0.60,
        "halation": 0.90,
        "optical_burn": True,
        "position": "bottom_right",
        "font_scale": 1.15,
        "margin_x": 1.40,
        "margin_y": 1.40,
    },
    "Compact Fine Dot (Minimal)": {
        "date_mode": "custom",
        "date_string": "'99 07 20 16:45",
        "date_format": "'YY MM DD",
        "show_time": True,
        "font_type": "Silkscreen (Fine Dot)",
        "preset_color": "Fuji Orange",
        "exposure_intensity": 1.00,
        "core_glow": 0.40,
        "halation": 0.90,
        "optical_burn": True,
        "position": "bottom_right",
        "font_scale": 1.10,
        "margin_x": 1.50,
        "margin_y": 1.50,
    },
}


@dataclass
class DateStampConfig:
    """フィルム日付スタンプの設定データクラス"""
    style_preset: str = "Custom"
    date_mode: str = "custom"  # "custom", "current_date", "random_vintage"
    date_string: str = "'98 12 24"
    date_format: str = "'YY MM DD"
    show_time: bool = False
    font_type: str = "DSEG7_Classic (7-Segment)"
    preset_color: str = "Amber Classic"
    custom_color_hex: Optional[str] = None  # 将来用 or 任意指定
    exposure_intensity: float = 1.0
    core_glow: float = 1.0
    halation: float = 1.0
    optical_burn: bool = True
    position: str = "bottom_right"
    font_scale: float = 1.0
    margin_x: float = 1.0
    margin_y: float = 1.0
    italic_angle: float = 0.0  # DSEG7_Italic 等で適用する傾斜アフィン角度（約10〜12度）

    def apply_style_preset_if_set(self):
        """style_preset が選択されている場合、対応するパラメータを適用"""
        if self.style_preset and self.style_preset in STYLE_PRESETS:
            preset_values = STYLE_PRESETS[self.style_preset]
            if preset_values:
                for k, v in preset_values.items():
                    if hasattr(self, k):
                        setattr(self, k, v)

    def get_color_palette(self) -> Dict[str, Tuple[int, int, int]]:
        """選択されたカラープリセットの辞書を取得"""
        if self.preset_color in COLOR_PRESETS:
            return COLOR_PRESETS[self.preset_color]
        return COLOR_PRESETS["Amber Classic"]


def format_datetime(dt: datetime.datetime, format_str: str, show_time: bool = False) -> str:
    """指定された日付フォーマットに従って日時候補文字列を生成"""
    yy = f"{dt.year % 100:02d}"
    yyyy = f"{dt.year:04d}"
    mm = f"{dt.month:02d}"
    dd = f"{dt.day:02d}"
    hh = f"{dt.hour:02d}"
    minute = f"{dt.minute:02d}"

    if format_str == "'YY MM DD":
        base = f"'{yy} {mm} {dd}"
    elif format_str == "MM DD 'YY":
        base = f"{mm} {dd} '{yy}"
    elif format_str == "DD MM 'YY":
        base = f"{dd} {mm} '{yy}"
    elif format_str == "DD.MM.YY":
        base = f"{dd}.{mm}.{yy}"
    elif format_str == "YY-MM-DD":
        base = f"{yy}-{mm}-{dd}"
    elif format_str == "YY.MM.DD":
        base = f"{yy}.{mm}.{dd}"
    elif format_str == "YYYY MM DD":
        base = f"{yyyy} {mm} {dd}"
    elif format_str == "YYYY-MM-DD":
        base = f"{yyyy}-{mm}-{dd}"
    elif format_str == "'YY MM DD HH:MM":
        # 過去互換
        return f"'{yy} {mm} {dd} {hh}:{minute}"
    else:
        # デフォルトは 'YY MM DD
        base = f"'{yy} {mm} {dd}"

    if show_time:
        return f"{base} {hh}:{minute}"
    return base


def generate_random_vintage_datetime(start_year: int = 1985, end_year: int = 2005) -> datetime.datetime:
    """1985〜2005年のランダムな日時を生成"""
    start_dt = datetime.datetime(start_year, 1, 1, 0, 0, 0)
    end_dt = datetime.datetime(end_year, 12, 31, 23, 59, 59)
    total_seconds = int((end_dt - start_dt).total_seconds())
    random_sec = random.randint(0, total_seconds)
    return start_dt + datetime.timedelta(seconds=random_sec)


def resolve_date_text(config: DateStampConfig, seed: Optional[int] = None) -> str:
    """
    設定に基づいて実際に描画する文字列を決定・解決する。
    """
    mode = config.date_mode.lower().strip()
    
    if mode == "custom":
        text = config.date_string.strip() if config.date_string else "'98 12 24"
        
        # 末尾の時刻（例: ' 18:30', ' 09:15'）を検出
        time_match = re.search(r'\s+(\d{1,2}:\d{2})$', text)
        
        if config.show_time:
            if not time_match:
                # show_time が True なのに時刻がない場合はデフォルト "18:30" を付加
                text = f"{text} 18:30"
        else:
            if time_match:
                # show_time が False なのに時刻が含まれている場合は除去
                text = text[:time_match.start()]
                
        return text
        
    elif mode == "current_date":
        now = datetime.datetime.now()
        return format_datetime(now, config.date_format, show_time=config.show_time)
        
    elif mode == "random_vintage":
        if seed is not None:
            # 再現性確保用のシード設定
            rng_state = random.getstate()
            random.seed(seed)
            dt = generate_random_vintage_datetime()
            random.setstate(rng_state)
        else:
            dt = generate_random_vintage_datetime()
        return format_datetime(dt, config.date_format, show_time=config.show_time)
        
    # フォールバック
    return config.date_string if config.date_string else "'98 12 24"
