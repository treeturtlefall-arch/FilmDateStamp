"""
FilmDateStamp - ComfyUI Custom Node
フィルム感光乳剤へのLED露光（Optical Burn-in）を再現する特化型日付スタンプノード。
"""
from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__version__ = "1.0.0"
WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY", "__version__"]
