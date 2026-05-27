# Refactor: Extract Input Handling from `main.py`

## Problem

`src/main.py` contains a ~200-line monolithic event loop with deeply nested `if/elif` chains for every screen. Every new feature (undo, hint, shortcuts overlay) requires surgical insertion into this dense block. This makes:

- **Adding features hard** — you must understand the entire nested structure to insert new branches.
- **Reviewing changes hard** — diffs are noisy because lines shift within the if-chain.
- **Testing hard** — input logic is tangled with the game loop, so you can't unit-test a handler in isolation.
- **Bug-prone** — subtle state bugs creep in when hover variables (`main_menu_hover`, `difficulty_hover`, `show_shortcuts`) are mutated inside the loop without clear ownership.

## Target Architecture

Extract input handling into a dedicated `InputHandler` class (and supporting per-screen handler methods). The main loop becomes thin — a dispatcher that calls `handler.handle_event(event)` and then updates state + renders.

```
src/main.py            — thin game loop (init, dispatch, update, render, loop)
src/ui/input_handler.py — InputHandler class with per-screen methods
```

### File: `src/ui/input_handler.py`

```
InputHandler
├── __init__(screen_manager, game_state, menu, hover_state)
├── handle_event(event) -> bool        # returns False to signal quit
│   ├── dispatch KEYDOWN → per-screen key handler
│   └── dispatch MOUSEBUTTONDOWN → per-screen mouse handler
├── _handle_main_menu_key(event)
├── _handle_main_menu_mouse(event)
├── _handle_difficulty_key(event)
├── _handle_difficulty_mouse(event)
├── _handle_game_key(event)
├── _handle_game_mouse(event)
├── _handle_paused_key(event)
├── _handle_game_over_key(event)
└── _handle_win_key(event)
```

### File: `src/main.py` (after refactor)

```python
def main():
    pygame.init()
    screen = pygame.display.set_mode((540, 640))
    pygame.display.set_caption("Sudoku")
    clock = pygame.time.Clock()

    generator = SudokuGenerator()
    renderer = Renderer(screen)
    menu = Menu(screen)
    screen_manager = ScreenManager()
    game_state: GameState | None = None

    hover_state = HoverState()  # owns main_menu_hover, difficulty_hover, show_shortcuts

    input_handler = InputHandler(screen_manager, game_state, menu, hover_state)

    running = True
    while running:
        for event in pygame.event.get():
            running = input_handler.handle_event(event)
            if not running:
                break

        # Game state updates
        _update_game_state(screen_manager, game_state)

        # Rendering
        _render(screen_manager, game_state, renderer, menu, hover_state)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
```

## Implementation Steps

### Step 1: Create `src/ui/input_handler.py`

Create `src/ui/input_handler.py` with:

1. **`HoverState` dataclass** — owns the three mutable hover/overlay booleans:
   ```python
   @dataclass
   class HoverState:
       main_menu_hover: int = -1
       difficulty_hover: int = 1
       show_shortcuts: bool = False
   ```

2. **`InputHandler` class** — receives `screen_manager`, `game_state`, `menu`, and `hover_state` in `__init__`.

3. **`handle_event(event) -> bool`** — single entry point:
   - If `QUIT`: return `False`
   - If `KEYDOWN`: dispatch to `_handle_keydown(event)`
   - If `MOUSEBUTTONDOWN`: dispatch to `_handle_mouse(event)`
   - Otherwise: return `True`

4. **`_handle_keydown(event)`** — dict-based dispatch:
   ```python
   _KEY_HANDLERS = {
       Screen.MAIN_MENU: "_handle_main_menu_key",
       Screen.DIFFICULTY: "_handle_difficulty_key",
       Screen.GAME: "_handle_game_key",
       Screen.PAUSED: "_handle_paused_key",
       Screen.GAME_OVER: "_handle_game_over_key",
       Screen.WIN: "_handle_win_key",
   }
   ```
   Use `getattr(self, handler_name)(event)` to call the right method.

5. **`_handle_mouse(event)`** — same pattern with `_MOUSE_HANDLERS`.

6. **Per-screen key handlers** — each takes `self, event` and mutates `hover_state` / `screen_manager` / `game_state` as needed.

7. **Per-screen mouse handlers** — each takes `self, event` and mutates state.

### Step 2: Update `src/main.py`

1. Replace the entire event loop body with:
   ```python
   input_handler = InputHandler(screen_manager, game_state, menu, hover_state)
   running = True
   while running:
       for event in pygame.event.get():
           running = input_handler.handle_event(event)
           if not running:
               break
       _update_game_state(screen_manager, game_state)
       _render(screen_manager, game_state, renderer, menu, hover_state)
       pygame.display.flip()
       clock.tick(60)
   ```

2. Extract `_update_game_state()` and `_render()` as module-level helpers (or methods on a `GameController` if you prefer OOP).

3. Remove all per-screen `if/elif` chains from the event loop.

### Step 3: Update `src/ui/__init__.py` (if needed)

Export `HoverState` and `InputHandler` from `src/ui/__init__.py` if other modules need them.

### Step 4: Run tests

```bash
python3 -m pytest tests/ -v
timeout 5 python3 scripts/smoke_test.py
```

Both must pass.

## Detailed Per-Screen Handler Logic

### Main Menu Key Handler
```python
def _handle_main_menu_key(self, event):
    if event.key == pygame.K_UP:
        self.hover.main_menu_hover = (self.hover.main_menu_hover - 1) % 2
    elif event.key == pygame.K_DOWN:
        self.hover.main_menu_hover = (self.hover.main_menu_hover + 1) % 2
    elif event.key == pygame.K_RETURN:
        if self.hover.main_menu_hover == 0:
            self.screen_manager.go_to(Screen.DIFFICULTY)
            self.hover.difficulty_hover = 1
        elif self.hover.main_menu_hover == 1:
            self.running = False  # or return a quit signal
```

### Main Menu Mouse Handler
```python
def _handle_main_menu_mouse(self, event):
    mx, my = event.pos
    menu_y = 640 // 2
    for idx, _ in enumerate(["New Game", "Quit"]):
        item_rect = pygame.Rect(540 // 2 - 100, menu_y + idx * 70 - 20, 200, 50)
        if item_rect.collidepoint(mx, my):
            if idx == 0:
                self.screen_manager.go_to(Screen.DIFFICULTY)
                self.hover.difficulty_hover = 1
            else:
                self.running = False
            break
```

### Difficulty Key Handler
```python
def _handle_difficulty_key(self, event):
    if event.key == pygame.K_UP:
        self.hover.difficulty_hover = max(0, self.hover.difficulty_hover - 1)
    elif event.key == pygame.K_DOWN:
        self.hover.difficulty_hover = min(2, self.hover.difficulty_hover + 1)
    elif event.key == pygame.K_RETURN:
        difficulty = DIFFICULTY_OPTIONS[self.hover.difficulty_hover]
        self.game_state = _generate_game(self.generator, difficulty)
        self.screen_manager.go_to(Screen.GAME)
    elif event.key == pygame.K_ESCAPE:
        self.screen_manager.go_back()
        self.hover.main_menu_hover = -1
```

### Difficulty Mouse Handler
```python
def _handle_difficulty_mouse(self, event):
    mx, my = event.pos
    menu_y = 640 // 2
    for idx, _ in enumerate(DIFFICULTY_OPTIONS):
        item_rect = pygame.Rect(540 // 2 - 160, menu_y + idx * 80 - 20, 320, 60)
        if item_rect.collidepoint(mx, my):
            difficulty = DIFFICULTY_OPTIONS[idx]
            self.game_state = _generate_game(self.generator, difficulty)
            self.screen_manager.go_to(Screen.GAME)
            break
```

### Game Key Handler
```python
def _handle_game_key(self, event):
    if self.game_state is None:
        return

    # Pause
    if event.key == pygame.K_p:
        self.screen_manager.go_to(Screen.PAUSED)
        return

    # Game over restart
    if self.game_state.is_game_over and event.key == pygame.K_SPACE:
        self.game_state.reset()
        return

    # Navigation
    if event.key in (pygame.K_UP, pygame.K_w):
        self.game_state.select_next("up")
    elif event.key in (pygame.K_DOWN, pygame.K_s):
        self.game_state.select_next("down")
    elif event.key in (pygame.K_LEFT, pygame.K_a):
        self.game_state.select_next("left")
    elif event.key in (pygame.K_RIGHT, pygame.K_d):
        self.game_state.select_next("right")

    # Number input
    elif event.unicode.isdigit() and 1 <= int(event.unicode) <= 9:
        self.game_state.enter_number(int(event.unicode))

    # Erase
    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
        self.game_state.erase()

    # Note mode
    elif event.key == pygame.K_n:
        self.game_state.toggle_note_mode()

    # Undo
    elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
        self.game_state.undo()

    # Hint
    elif event.key == pygame.K_h:
        self.game_state.give_hint()
        self.hover.show_shortcuts = False

    # Shortcuts overlay
    elif event.key == pygame.K_k:
        self.hover.show_shortcuts = not self.hover.show_shortcuts
```

### Game Mouse Handler
```python
def _handle_game_mouse(self, event):
    if self.game_state is None:
        return
    mx, my = event.pos
    col = mx // 60
    row = my // 60
    if 0 <= row < 9 and 0 <= col < 9:
        self.game_state.select_cell(row, col)
```

### Paused Key Handler
```python
def _handle_paused_key(self, event):
    if event.key == pygame.K_p:
        self.screen_manager.go_back()
```

### Game Over Key Handler
```python
def _handle_game_over_key(self, event):
    if event.key == pygame.K_SPACE:
        self.game_state.reset()
        self.screen_manager.go_to(Screen.GAME)
    elif event.key == pygame.K_ESCAPE:
        self.game_state = None
        self.screen_manager.go_to(Screen.MAIN_MENU)
        self.hover.main_menu_hover = -1
```

### Win Key Handler
```python
def _handle_win_key(self, event):
    if event.key == pygame.K_SPACE:
        self.game_state.reset()
        self.screen_manager.go_to(Screen.GAME)
    elif event.key == pygame.K_ESCAPE:
        self.game_state = None
        self.screen_manager.go_to(Screen.MAIN_MENU)
        self.hover.main_menu_hover = -1
```

## Notes & Decisions

- **`_generate_game()` stays in `main.py`** — it's a tiny helper and doesn't belong in the UI layer.
- **`DIFFICULTY_OPTIONS` stays in `main.py`** — same reasoning.
- **The `running` flag** — the quit signal from mouse handlers can set `self.running = False` on the handler or return a sentinel. The simplest approach: add a `self._should_quit: bool = False` attribute that `handle_event` checks and returns `not self._should_quit`.
- **Generator reference** — `InputHandler` needs a reference to the `SudokuGenerator` instance for difficulty selection. Pass it in `__init__`.
- **No new dependencies** — this is pure restructuring, no new packages.
- **Preserve exact behaviour** — every key/mouse interaction must behave identically to the original.

## Testing Strategy

1. Run `python3 -m pytest tests/ -v` — all existing tests must pass (no logic changed).
2. Run `timeout 5 python3 scripts/smoke_test.py` — smoke test must pass.
3. Manual verification:
   - Navigate main menu with arrows and Enter
   - Select difficulty
   - Play a game: move, enter numbers, erase, toggle notes, undo (Ctrl+Z), hint (H), shortcuts overlay (K), pause (P)
   - Game over / win screens: restart and escape back to menu

## Files Changed

| File | Action |
|------|--------|
| `src/ui/input_handler.py` | **NEW** — `HoverState` dataclass + `InputHandler` class |
| `src/main.py` | **MODIFY** — thin loop, delegate to `InputHandler` |
| `src/ui/__init__.py` | **OPTIONAL** — export new classes |
