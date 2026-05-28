# Public API — One-Pager

Reference for the two core classes. All methods listed here are the intended public surface; everything else is internal.

---

## `GameState` (`src/game_state.py`)

### Constructor

```python
GameState(puzzle: Board, solution: Board, max_mistakes: int = 3)
```

| Parameter    | Type       | Default | Description                        |
|-------------|-----------|---------|------------------------------------|
| `puzzle`    | `Board`   | —       | Original puzzle (0 = empty)        |
| `solution`  | `Board`   | —       | Complete solved board              |
| `max_mistakes` | `int`  | `3`     | Mistakes allowed before game over  |

### Public Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `tick` | `tick() -> None` | Update elapsed time. Call once per frame. |
| `select_cell` | `select_cell(row: int, col: int) -> None` | Select the cell at *(row, col)* (0–8). |
| `select_next` | `select_next(direction: str) -> None` | Move selection: `"up"`, `"down"`, `"left"`, `"right"`. |
| `enter_number` | `enter_number(number: int) -> None` | Enter 1–9 into the selected cell (respects note mode). |
| `erase` | `erase() -> None` | Erase the selected cell (backspace). |
| `undo` | `undo() -> bool` | Undo the last action. Returns `True` if something was undone. |
| `give_hint` | `give_hint() -> bool` | Reveal one empty cell. Uses one hint. Returns `True` if used. |
| `reset_hint` | `reset_hint() -> None` | Clear the hint highlight. |
| `toggle_note_mode` | `toggle_note_mode() -> None` | Toggle pencil/note mode on/off. |
| `get_cell_notes` | `get_cell_notes(row: int, col: int) -> Set[int]` | Return candidate notes for a cell. |
| `reset` | `reset() -> None` | Reset to a fresh start (same puzzle/solution, timer restarts). |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `minutes` | `int` | Elapsed minutes (integer). |
| `seconds` | `int` | Elapsed seconds within the current minute (0–59). |
| `is_over` | `bool` | `True` if game is won or lost. |
| `selected_cell_is_locked` | `bool` | `True` if the selected cell is a given (locked) cell. |
| `selected_cell_number` | `int` | Number in the selected cell, or `0` if none. |

### Key Fields (read-only access)

| Field | Type | Description |
|-------|------|-------------|
| `player_grid` | `Board` | Player's current grid. |
| `mistake_count` | `int` | Number of mistakes made. |
| `is_note_mode` | `bool` | Whether pencil mode is active. |
| `is_won` | `bool` | `True` if the player has won. |
| `is_game_over` | `bool` | `True` if the game is over. |
| `hints_used` | `int` | Number of hints used so far. |
| `max_hints` | `int` | Maximum allowed hints. |
| `hinted_cell` | `Tuple[int, int]` | Position of the last hinted cell (or `(-1, -1)`). |

---

## `Renderer` (`src/ui/renderer.py`)

### Constructor

```python
Renderer(screen: pygame.Surface, font: pygame.font.Font | None = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `screen` | `pygame.Surface` | — | The display surface to draw on. |
| `font` | `pygame.font.Font \| None` | `None` | Optional custom font. |

### Public Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `render` | `render(state: GameState, screen: Screen = Screen.GAME) -> None` | Render the complete game state. Handles grid, HUD, and overlays (win, game-over, paused). |

> **Note:** `Renderer` has no other public methods. All drawing is done through `render()`, which dispatches to private helpers (`_draw_grid`, `_draw_hud`, `_draw_win_overlay`, etc.).
