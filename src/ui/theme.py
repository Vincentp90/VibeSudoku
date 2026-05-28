"""Central visual constants for the Sudoku game.

All colours, font sizes, grid constants, and layout values live here.
Window dimensions (WIDTH, HEIGHT) are imported from display.py.
"""

from __future__ import annotations

# Import window dimensions from display.py (display-specific)
from src.ui.display import WIDTH, HEIGHT

# Colours
BACKGROUND: tuple[int, int, int] = (255, 255, 255)
GRID_LINE: tuple[int, int, int] = (0, 0, 0)
THICK_GRID_LINE: tuple[int, int, int] = (0, 0, 0)
LOCKED_TEXT: tuple[int, int, int] = (30, 30, 30)
PLAYER_TEXT: tuple[int, int, int] = (41, 128, 185)
HIGHLIGHT: tuple[int, int, int] = (206, 215, 222)
SELECTED: tuple[int, int, int] = (120, 177, 232)
INVALID: tuple[int, int, int] = (192, 57, 43)
PEER_HIGHLIGHT: tuple[int, int, int] = (230, 240, 245)
HINT: tuple[int, int, int] = (241, 196, 15)

# Additional colours (used by renderer)
NOTE_COLOR: tuple[int, int, int] = (100, 100, 100)
HUD_TEXT_COLOR: tuple[int, int, int] = (50, 50, 50)
OVERLAY_TEXT_COLOR: tuple[int, int, int] = (200, 200, 200)
OVERLAY_TITLE_COLOR: tuple[int, int, int] = (255, 255, 255)
SUBTITLE_COLOR: tuple[int, int, int] = (120, 120, 120)
FOOTER_HINT_COLOR: tuple[int, int, int] = (160, 160, 160)
MENU_ITEM_COLOR: tuple[int, int, int] = (50, 50, 50)
DIFFICULTY_LABEL_COLOR: tuple[int, int, int] = (80, 80, 80)
DIFFICULTY_DESC_COLOR: tuple[int, int, int] = (150, 150, 150)
SHORTCUT_KEY_COLOR: tuple[int, int, int] = (241, 196, 15)
SHORTCUT_DESC_COLOR: tuple[int, int, int] = (200, 200, 200)
SHORTCUT_CLOSE_COLOR: tuple[int, int, int] = (150, 150, 150)
WIN_TITLE_COLOR: tuple[int, int, int] = (46, 204, 113)
GAME_OVER_TITLE_COLOR: tuple[int, int, int] = (192, 57, 43)

# Fonts
FONT_NAME: str = "assets/fonts/default.ttf"

# Font sizes
NUMBER_FONT_SIZE: int = 36
NOTE_FONT_SIZE: int = 14
HUD_FONT_SIZE: int = 24
OVERLAY_FONT_SIZE: int = 48
TITLE_FONT_SIZE: int = 64
MENU_ITEM_FONT_SIZE: int = 36
SUBTITLE_FONT_SIZE: int = 24
FOOTER_FONT_SIZE: int = 24

# Grid & layout
GRID_OFFSET_X: int = 0
GRID_OFFSET_Y: int = 0
GRID_SIZE: int = 540
CELL_SIZE: int = 60
HUD_HEIGHT: int = 100

__all__ = [
    # Colours
    "BACKGROUND",
    "GRID_LINE",
    "THICK_GRID_LINE",
    "LOCKED_TEXT",
    "PLAYER_TEXT",
    "HIGHLIGHT",
    "SELECTED",
    "INVALID",
    "PEER_HIGHLIGHT",
    "HINT",
    "NOTE_COLOR",
    "HUD_TEXT_COLOR",
    "OVERLAY_TEXT_COLOR",
    "OVERLAY_TITLE_COLOR",
    "SUBTITLE_COLOR",
    "FOOTER_HINT_COLOR",
    "MENU_ITEM_COLOR",
    "DIFFICULTY_LABEL_COLOR",
    "DIFFICULTY_DESC_COLOR",
    "SHORTCUT_KEY_COLOR",
    "SHORTCUT_DESC_COLOR",
    "SHORTCUT_CLOSE_COLOR",
    "WIN_TITLE_COLOR",
    "GAME_OVER_TITLE_COLOR",
    # Fonts
    "FONT_NAME",
    # Font sizes
    "NUMBER_FONT_SIZE",
    "NOTE_FONT_SIZE",
    "HUD_FONT_SIZE",
    "OVERLAY_FONT_SIZE",
    "TITLE_FONT_SIZE",
    "MENU_ITEM_FONT_SIZE",
    "SUBTITLE_FONT_SIZE",
    "FOOTER_FONT_SIZE",
    # Grid & layout
    "GRID_OFFSET_X",
    "GRID_OFFSET_Y",
    "GRID_SIZE",
    "CELL_SIZE",
    "HUD_HEIGHT",
    # Re-exported from display.py
    "WIDTH",
    "HEIGHT",
]
