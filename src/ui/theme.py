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
