# Refactor: Centralise Difficulty Options in `InputHandler`

## Problem

`_handle_difficulty_mouse` in `src/ui/input_handler.py` hardcodes the difficulty list:

```python
for idx, _ in enumerate(["easy", "medium", "hard"]):
    ...
    difficulty = ["easy", "medium", "hard"][idx]
```

Meanwhile, `_handle_difficulty_key` already uses the `_get_difficulty_option()` helper. This is a **duplication** — the same literal list lives in two places, and a future rename or reordering would require updating both.

## Goal

1. Ensure `_get_difficulty_option()` is the **single source of truth** for resolving the hover index to a difficulty string.
2. Replace the hardcoded `["easy", "medium", "hard"]` in `_handle_difficulty_mouse` with a reference to the shared constant (`DIFFICULTY_OPTIONS` from `main.py`).

## Implementation

### Step 1: Ensure `_get_difficulty_option()` is the canonical resolver

`_get_difficulty_option()` already exists and works correctly:

```python
def _get_difficulty_option(self) -> str | None:
    """Return the difficulty string at the current hover index."""
    options = ["easy", "medium", "hard"]
    idx = self.hover.difficulty_hover
    if 0 <= idx < len(options):
        return options[idx]
    return None
```

**Decision:** Move the `options` list to a module-level constant so it is defined exactly once:

```python
_DIFFICULTY_OPTIONS: tuple[str, ...] = ("easy", "medium", "hard")
```

Then update `_get_difficulty_option()` to reference it:

```python
def _get_difficulty_option(self) -> str | None:
    """Return the difficulty string at the current hover index."""
    idx = self.hover.difficulty_hover
    if 0 <= idx < len(_DIFFICULTY_OPTIONS):
        return _DIFFICULTY_OPTIONS[idx]
    return None
```

### Step 2: Replace hardcoded list in `_handle_difficulty_mouse`

Current code:

```python
def _handle_difficulty_mouse(self, event: pygame.event.Event) -> None:
    mx, my = event.pos
    menu_y = 640 // 2
    for idx, _ in enumerate(["easy", "medium", "hard"]):
        item_rect = pygame.Rect(
            540 // 2 - 160,
            menu_y + idx * 80 - 20,
            320,
            60,
        )
        if item_rect.collidepoint(mx, my):
            difficulty = ["easy", "medium", "hard"][idx]
            if self.generator is not None:
                puzzle, solution = self.generator.generate(difficulty)
                from src.game_state import GameState
                self.game_state = GameState(puzzle=puzzle, solution=solution)
            self.screen_manager.go_to(Screen.GAME)
            break
```

Replace with — use `_get_difficulty_option()` for the difficulty lookup and iterate over `len(_DIFFICULTY_OPTIONS)` instead of a hardcoded list:

```python
def _handle_difficulty_mouse(self, event: pygame.event.Event) -> None:
    mx, my = event.pos
    menu_y = 640 // 2
    for idx in range(len(_DIFFICULTY_OPTIONS)):
        item_rect = pygame.Rect(
            540 // 2 - 160,
            menu_y + idx * 80 - 20,
            320,
            60,
        )
        if item_rect.collidepoint(mx, my):
            difficulty = _DIFFICULTY_OPTIONS[idx]
            if self.generator is not None:
                puzzle, solution = self.generator.generate(difficulty)
                from src.game_state import GameState
                self.game_state = GameState(puzzle=puzzle, solution=solution)
            self.screen_manager.go_to(Screen.GAME)
            break
```

> **Note:** We use `_DIFFICULTY_OPTIONS[idx]` directly (not `_get_difficulty_option()`) here because we need the difficulty for the *clicked* index, not the current hover index. The helper resolves `self.hover.difficulty_hover`, which may differ from the clicked cell.

### Step 3: Run tests

```bash
python3 -m pytest tests/ -v
timeout 5 python3 scripts/smoke_test.py
```

Both must pass.

## Files Changed

| File | Action |
|------|--------|
| `src/ui/input_handler.py` | **MODIFY** — add `_DIFFICULTY_OPTIONS` constant, update `_get_difficulty_option()` and `_handle_difficulty_mouse()` |
