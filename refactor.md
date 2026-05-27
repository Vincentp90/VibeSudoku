# Refactoring Tasks

This file tracks refactoring tasks that improve code quality but are not part of feature development.

---

## 1. Centralize All Styling Constants in `theme.py`

### Problem
Font sizes, grid constants, and spacing values are scattered across multiple files:

| Constant | Current Location |
|---|---|
| `NUMBER_FONT_SIZE` (36) | `src/ui/renderer.py` |
| `NOTE_FONT_SIZE` (14) | `src/ui/renderer.py` |
| `HUD_FONT_SIZE` (24) | `src/ui/renderer.py` |
| `OVERLAY_FONT_SIZE` (48) | `src/ui/renderer.py` |
| `TITLE_FONT_SIZE` (64) | `src/ui/menu.py` |
| `MENU_ITEM_FONT_SIZE` (36) | `src/ui/menu.py` |
| `SUBTITLE_FONT_SIZE` (24) | `src/ui/menu.py` |
| `GRID_OFFSET_X` (0) | `src/ui/renderer.py` |
| `GRID_OFFSET_Y` (0) | `src/ui/renderer.py` |
| `GRID_SIZE` (540) | `src/ui/renderer.py` |
| `CELL_SIZE` (60) | `src/ui/renderer.py` |
| `HUD_HEIGHT` (100) | `src/ui/renderer.py` |

Meanwhile, `src/ui/display.py` already holds the "source of truth" for colours (`BACKGROUND`, `GRID_LINE`, etc.) and window dimensions (`WIDTH`, `HEIGHT`).

### Goal
Create `src/ui/theme.py` (or enhance `display.py`) as the single source of truth for all visual constants. Every module that currently defines its own font sizes or grid constants should import from this central file instead.

### Scope

1. **Create `src/ui/theme.py`** with the following structure:
   ```python
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

   # Export existing display constants
   from src.ui.display import (
       WIDTH, HEIGHT,
       BACKGROUND,
       GRID_LINE, THICK_GRID_LINE,
       LOCKED_TEXT, PLAYER_TEXT,
       HIGHLIGHT, SELECTED, INVALID,
       PEER_HIGHLIGHT,
       FONT_NAME,
   )

   __all__ = [
       # Font sizes
       "NUMBER_FONT_SIZE", "NOTE_FONT_SIZE", "HUD_FONT_SIZE",
       "OVERLAY_FONT_SIZE", "TITLE_FONT_SIZE",
       "MENU_ITEM_FONT_SIZE", "SUBTITLE_FONT_SIZE",
       # Grid & layout
       "GRID_OFFSET_X", "GRID_OFFSET_Y", "GRID_SIZE",
       "CELL_SIZE", "HUD_HEIGHT",
       # Re-exported display constants
       "WIDTH", "HEIGHT", "BACKGROUND",
       "GRID_LINE", "THICK_GRID_LINE",
       "LOCKED_TEXT", "PLAYER_TEXT",
       "HIGHLIGHT", "SELECTED", "INVALID",
       "PEER_HIGHLIGHT", "FONT_NAME",
   ]
   ```

2. **Update `src/ui/renderer.py`**:
   - Remove all local `FONT_SIZE` and grid constant definitions.
   - Import from `src.ui.theme` instead.
   - Verify all font names and sizes still match.

3. **Update `src/ui/menu.py`**:
   - Remove all local `FONT_SIZE` definitions.
   - Import from `src.ui.theme` instead.

4. **Update `src/ui/__init__.py`**:
   - Re-export from `theme.py` so consumers can do `from src.ui import NUMBER_FONT_SIZE`.

5. **Update `src/ui/display.py`** (optional):
   - Consider whether `WIDTH` / `HEIGHT` should live in `display.py` or `theme.py` (they're already in `display.py`, which is fine — just ensure consistency).

### Acceptance Criteria
- Running `python3 scripts/smoke_test.py` still passes (window opens and renders for 2s).
- All existing tests pass (`python3 -m pytest tests/ -v`).
- No file defines any of the 12 constants listed above locally — they all import from `theme.py`.
- `grep -r "FONT_SIZE" src/` only finds results in `theme.py` (imports and `__all__`).

### Notes
- This is a pure refactor — no behaviour changes. One import at a time, test after each file.
- `display.py` can stay as-is for colours; `theme.py` is for sizes/layout. The separation keeps things readable.
- If `display.py` and `theme.py` feel redundant, consider merging them into a single `display.py` with everything in it.
