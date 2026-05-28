"""Full playthrough integration test.

Simulates a complete game: generate a puzzle, fill every cell
correctly, and verify that the win state is reached.
"""

import pytest

from src.logic.generator import SudokuGenerator
from src.logic.validator import SudokuValidator
from src.game_state import GameState


@pytest.fixture
def generator():
    """Return a seeded generator for reproducibility."""
    return SudokuGenerator(seed=42)


def _solve_puzzle_manually(state: GameState) -> None:
    """Fill every empty cell with the correct solution value.

    This simulates a player entering every number correctly by
    selecting each cell and entering the correct number.
    """
    for r in range(9):
        for c in range(9):
            if state.puzzle[r][c] == 0 and state.player_grid[r][c] == 0:
                state.select_cell(r, c)
                state.enter_number(state.solution[r][c])


def _enter_wrong(state: GameState, r: int, c: int, wrong_num: int) -> None:
    """Enter a wrong number into the given cell."""
    state.select_cell(r, c)
    state.enter_number(wrong_num)


def test_full_playthrough_easy(generator: SudokuGenerator) -> None:
    """Generate an easy puzzle and simulate a perfect playthrough."""
    puzzle, solution = generator.generate("easy")

    # Validate the generated boards
    assert SudokuValidator.is_valid(solution)
    assert SudokuValidator.is_valid(puzzle)

    state = GameState(puzzle=puzzle, solution=solution)
    assert not state.is_won
    assert not state.is_game_over
    assert state.mistake_count == 0

    # Simulate perfect play — fill every cell correctly
    _solve_puzzle_manually(state)

    # After filling all cells, the game should be won
    assert state.is_won
    assert state.is_game_over
    assert state.mistake_count == 0

    # Verify player_grid matches solution
    for r in range(9):
        for c in range(9):
            assert state.player_grid[r][c] == solution[r][c]


def test_full_playthrough_medium(generator: SudokuGenerator) -> None:
    """Generate a medium puzzle and simulate a perfect playthrough."""
    puzzle, solution = generator.generate("medium")

    assert SudokuValidator.is_valid(solution)

    state = GameState(puzzle=puzzle, solution=solution)
    assert not state.is_won

    _solve_puzzle_manually(state)

    assert state.is_won
    assert state.is_game_over
    assert state.mistake_count == 0


def test_full_playthrough_hard(generator: SudokuGenerator) -> None:
    """Generate a hard puzzle and simulate a perfect playthrough."""
    puzzle, solution = generator.generate("hard")

    assert SudokuValidator.is_valid(solution)

    state = GameState(puzzle=puzzle, solution=solution)
    assert not state.is_won

    _solve_puzzle_manually(state)

    assert state.is_won
    assert state.is_game_over
    assert state.mistake_count == 0


def test_game_over_via_mistakes(generator: SudokuGenerator) -> None:
    """Simulate a player making enough mistakes to trigger game over."""
    puzzle, solution = generator.generate("easy")
    state = GameState(puzzle=puzzle, solution=solution, max_mistakes=3)

    # Find three empty cells and enter wrong numbers
    wrong_count = 0
    for r in range(9):
        if wrong_count >= 3:
            break
        for c in range(9):
            if wrong_count >= 3:
                break
            if puzzle[r][c] == 0:
                wrong_num = solution[r][c] % 9 + 1  # guaranteed wrong since solution[r][c] is 1-9
                _enter_wrong(state, r, c, wrong_num)
                wrong_count += 1

    assert state.is_game_over
    assert not state.is_won
    assert state.mistake_count >= 3


def test_undo_restores_cell_value(generator: GameState) -> None:
    """After undoing a wrong entry, the cell value is restored."""
    puzzle, solution = SudokuGenerator(seed=42).generate("easy")
    state = GameState(puzzle=puzzle, solution=solution)

    # Make a wrong entry
    state.select_cell(0, 0)
    state.enter_number(solution[0][0] % 9 + 1)
    assert state.mistake_count == 1
    assert state.player_grid[0][0] == solution[0][0] % 9 + 1

    # Undo the wrong entry
    state.undo()
    assert state.player_grid[0][0] == 0  # cell restored to empty

    # Now fill correctly — should still be able to win
    _solve_puzzle_manually(state)
    assert state.is_won


def test_hint_does_not_break_win_condition(generator: SudokuGenerator) -> None:
    """Using a hint (filling a cell correctly) should not prevent winning."""
    puzzle, solution = generator.generate("medium")
    state = GameState(puzzle=puzzle, solution=solution)

    # Use a hint
    state.give_hint()
    assert state.hints_used == 1

    # Fill the rest correctly
    _solve_puzzle_manually(state)

    assert state.is_won
    assert state.hints_used == 1  # only one hint was used
