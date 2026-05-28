# Improvements

Actionable instructions for the next agent working on VibeSudoku.

---

## 2. Add a reusable `active_game_state` pytest fixture

**Why:** Every test that manipulates the player grid has to repeat the boilerplate:
```python
puzzle, solution = generator.generate("easy")
state = GameState(puzzle=puzzle, solution=solution)
state.select_cell(0, 0)
```

This is verbose, error-prone (forgetting `select_cell`), and makes tests harder to read.

**What to do:**

1. Open `tests/conftest.py`.
2. Add a fixture called `active_game_state` that returns a `GameState` with a seed and a cell already selected:

```python
@pytest.fixture
def active_game_state():
    """Return a GameState with a puzzle, solution, and cell (0, 0) selected.

    Useful for tests that immediately call enter_number, erase, or similar
    methods on the selected cell.
    """
    puzzle, solution = SudokuGenerator(seed=42).generate("easy")
    state = GameState(puzzle=puzzle, solution=solution)
    state.select_cell(0, 0)
    return state
```

3. Update existing tests in `tests/test_game_state.py` that currently create their own `GameState` inline to use the fixture instead. For tests that need a different difficulty or seed, add parameters:

```python
@pytest.fixture
def game_state_difficulty():
    """Return a fixture factory for generating states at different difficulties."""
    def _make(difficulty="easy", seed=42):
        puzzle, solution = SudokuGenerator(seed=seed).generate(difficulty)
        state = GameState(puzzle=puzzle, solution=solution)
        return state
    return _make
```

4. Run `python3 -m pytest tests/test_game_state.py -v` to verify nothing broke.

---

## 3. Add a "quick smoke" integration test

**Why:** The current smoke test (`scripts/smoke_test.py`) only verifies that Pygame can open a window. It does not exercise the game logic. If a developer accidentally breaks `GameState.enter_number()` or `GameState.select_cell()`, the smoke test won't catch it.

**What to do:**

1. Create a new file: `tests/test_smoke_integration.py`.
2. Add a single test that exercises the core game flow:

```python
"""Quick smoke integration test.

Verifies that the basic game loop (generate → select → enter →
undo) still works end-to-end. Catches regressions in GameState
before they reach the renderer.
"""

import pytest

from src.logic.generator import SudokuGenerator
from src.game_state import GameState


def test_quick_smoke():
    """Generate a puzzle and perform a few player actions."""
    puzzle, solution = SudokuGenerator(seed=42).generate("easy")
    state = GameState(puzzle=puzzle, solution=solution)

    # Select a cell and enter a correct number
    state.select_cell(0, 0)
    state.enter_number(solution[0][0])
    assert state.player_grid[0][0] == solution[0][0]
    assert state.mistake_count == 0

    # Enter a wrong number
    state.select_cell(0, 1)
    wrong = solution[0][1] % 9 + 1  # a guaranteed wrong number
    state.enter_number(wrong)
    assert state.player_grid[0][1] == wrong
    assert state.mistake_count == 1

    # Undo the wrong entry
    state.undo()
    assert state.player_grid[0][1] == 0

    # Navigate with keyboard-style methods
    state.select_next("right")
    assert state.selected_col == 2
    state.select_next("down")
    assert state.selected_row == 1

    # Toggle note mode and add a note
    state.toggle_note_mode()
    assert state.is_note_mode
    state.enter_number(5)
    assert 5 in state.notes[1][2]
```

3. Run `python3 -m pytest tests/test_smoke_integration.py -v` to verify.
4. Optionally: add this test to a pre-commit hook or CI config so it runs on every PR.

---

## 4. Improve test assertion quality

**Why:** When a test fails, Pygame dumps the entire `GameState` dataclass (hundreds of lines of repr), making it hard to spot the actual problem. For example:

```
E       assert False
E        +  where False = GameState(puzzle=[[0, 0, 3, ...  # 200 more lines
```

**What to do:**

1. **Use more specific assertions.** Instead of:
   ```python
   assert state.is_won
   ```
   Add context:
   ```python
   assert state.is_won, (
       f"Expected win but player_grid[0][0]={state.player_grid[0][0]}, "
       f"solution[0][0]={state.solution[0][0]}, "
       f"mistake_count={state.mistake_count}"
   )
   ```

2. **Use `pytest.approx` or helper functions** for comparing grids:

   ```python
   def assert_grid_equal(actual, expected, label="player_grid"):
       """Assert two 9x9 grids are equal with a helpful message."""
       for r in range(9):
           for c in range(9):
               assert actual[r][c] == expected[r][c], (
                   f"Mismatch at ({r},{c}): {label}[{r}][{c}] = "
                   f"{actual[r][c]}, expected {expected[r][c]}"
               )
   ```

3. **Use `pytest.raises`** instead of checking state after a method call:

   ```python
   # Before:
   state.enter_number(0)
   assert state.player_grid[0][0] == 0  # silent no-op

   # After (if you add validation):
   with pytest.raises(ValueError):
       state.enter_number(0)
   ```

4. **For the playthrough tests**, instead of asserting `state.is_won` at the end, verify the grid matches:

   ```python
   assert_grid_equal(state.player_grid, solution, "player_grid")
   ```

   This gives a precise cell-level failure message instead of a vague "is_won is False".

5. Run `python3 -m pytest tests/ -v` after making changes to ensure nothing regresses.
