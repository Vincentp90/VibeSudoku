"""Unit tests for :class:`~src.game_state.GameState`."""

import unittest

from src.game_state import GameState


class TestGameStateInit(unittest.TestCase):
    """Tests for GameState initialisation."""

    def setUp(self) -> None:
        """Create a simple puzzle and its solution."""
        self.puzzle = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        self.solution = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]

    def test_player_grid_starts_as_puzzle_copy(self):
        gs = GameState(self.puzzle, self.solution)
        for r in range(9):
            for c in range(9):
                self.assertEqual(gs.player_grid[r][c], self.puzzle[r][c])

    def test_selected_cell_is_none(self):
        gs = GameState(self.puzzle, self.solution)
        self.assertEqual(gs.selected_row, -1)
        self.assertEqual(gs.selected_col, -1)

    def test_mistake_count_starts_at_zero(self):
        gs = GameState(self.puzzle, self.solution)
        self.assertEqual(gs.mistake_count, 0)

    def test_game_not_over(self):
        gs = GameState(self.puzzle, self.solution)
        self.assertFalse(gs.is_game_over)
        self.assertFalse(gs.is_won)

    def test_max_mistakes_default(self):
        gs = GameState(self.puzzle, self.solution)
        self.assertEqual(gs.max_mistakes, 3)

    def test_custom_max_mistakes(self):
        gs = GameState(self.puzzle, self.solution, max_mistakes=5)
        self.assertEqual(gs.max_mistakes, 5)


class TestCellSelection(unittest.TestCase):
    """Tests for cell selection logic."""

    def setUp(self) -> None:
        self.puzzle = [[0] * 9 for _ in range(9)]
        self.solution = [[0] * 9 for _ in range(9)]
        self.gs = GameState(self.puzzle, self.solution)

    def test_select_cell(self):
        self.gs.select_cell(3, 4)
        self.assertEqual(self.gs.selected_row, 3)
        self.assertEqual(self.gs.selected_col, 4)

    def test_select_out_of_bounds_row(self):
        self.gs.select_cell(9, 0)
        self.assertEqual(self.gs.selected_row, -1)

    def test_select_out_of_bounds_col(self):
        self.gs.select_cell(0, 9)
        self.assertEqual(self.gs.selected_col, -1)

    def test_select_next_up(self):
        self.gs.select_cell(5, 5)
        self.gs.select_next("up")
        self.assertEqual(self.gs.selected_row, 4)

    def test_select_next_down(self):
        self.gs.select_cell(3, 3)
        self.gs.select_next("down")
        self.assertEqual(self.gs.selected_row, 4)

    def test_select_next_left(self):
        self.gs.select_cell(5, 5)
        self.gs.select_next("left")
        self.assertEqual(self.gs.selected_col, 4)

    def test_select_next_right(self):
        self.gs.select_cell(3, 3)
        self.gs.select_next("right")
        self.assertEqual(self.gs.selected_col, 4)

    def test_select_next_clamps_top(self):
        self.gs.select_cell(0, 0)
        self.gs.select_next("up")
        self.assertEqual(self.gs.selected_row, 0)

    def test_select_next_clamps_bottom(self):
        self.gs.select_cell(8, 8)
        self.gs.select_next("down")
        self.assertEqual(self.gs.selected_row, 8)

    def test_select_next_clamps_left(self):
        self.gs.select_cell(0, 0)
        self.gs.select_next("left")
        self.assertEqual(self.gs.selected_col, 0)

    def test_select_next_clamps_right(self):
        self.gs.select_cell(0, 8)
        self.gs.select_next("right")
        self.assertEqual(self.gs.selected_col, 8)


class TestNumberInput(unittest.TestCase):
    """Tests for number input and erase."""

    def setUp(self) -> None:
        self.puzzle = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        self.solution = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]
        self.gs = GameState(self.puzzle, self.solution)

    def test_enter_correct_number(self):
        self.gs.select_cell(0, 2)
        self.gs.enter_number(4)
        self.assertEqual(self.gs.player_grid[0][2], 4)
        self.assertEqual(self.gs.mistake_count, 0)

    def test_enter_incorrect_number(self):
        self.gs.select_cell(0, 2)
        self.gs.enter_number(9)  # wrong — should be 4
        self.assertEqual(self.gs.player_grid[0][2], 9)
        self.assertEqual(self.gs.mistake_count, 1)

    def test_enter_on_locked_cell(self):
        self.gs.select_cell(0, 0)  # locked cell with value 5
        self.gs.enter_number(3)
        self.assertEqual(self.gs.player_grid[0][0], 5)  # unchanged
        self.assertEqual(self.gs.mistake_count, 0)

    def test_enter_zero_ignored(self):
        self.gs.select_cell(0, 2)
        self.gs.enter_number(0)
        self.assertEqual(self.gs.player_grid[0][2], 0)  # still 0

    def test_enter_on_no_selection(self):
        self.gs.enter_number(4)
        self.assertEqual(self.gs.player_grid[0][2], 0)  # no selection, no change

    def test_erase_cell(self):
        self.gs.select_cell(0, 2)
        self.gs.enter_number(4)
        self.assertEqual(self.gs.player_grid[0][2], 4)
        self.gs.erase()
        self.assertEqual(self.gs.player_grid[0][2], 0)

    def test_erase_locked_cell(self):
        self.gs.select_cell(0, 0)
        self.gs.erase()
        self.assertEqual(self.gs.player_grid[0][0], 5)  # unchanged

    def test_erase_empty_cell(self):
        self.gs.select_cell(0, 2)
        self.gs.erase()
        self.assertEqual(self.gs.player_grid[0][2], 0)  # nothing to erase

    def test_erase_no_selection(self):
        self.gs.erase()
        self.assertEqual(self.gs.player_grid[0][2], 0)


class TestNoteMode(unittest.TestCase):
    """Tests for note/pencil mode."""

    def setUp(self) -> None:
        self.puzzle = [[0] * 9 for _ in range(9)]
        self.solution = [[0] * 9 for _ in range(9)]
        self.gs = GameState(self.puzzle, self.solution)

    def test_note_mode_toggle(self):
        self.assertFalse(self.gs.is_note_mode)
        self.gs.toggle_note_mode()
        self.assertTrue(self.gs.is_note_mode)
        self.gs.toggle_note_mode()
        self.assertFalse(self.gs.is_note_mode)

    def test_enter_note(self):
        self.gs.is_note_mode = True
        self.gs.select_cell(0, 0)
        self.gs.enter_number(3)
        self.gs.enter_number(5)
        notes = self.gs.get_cell_notes(0, 0)
        self.assertEqual(notes, {3, 5})

    def test_enter_note_on_locked_cell(self):
        self.puzzle = [[5] + [0] * 8] + [[0] * 9 for _ in range(8)]
        self.solution = [[5] + [0] * 8] + [[0] * 9 for _ in range(8)]
        gs = GameState(self.puzzle, self.solution)
        gs.is_note_mode = True
        gs.select_cell(0, 0)
        gs.enter_number(3)
        notes = gs.get_cell_notes(0, 0)
        self.assertEqual(notes, set())  # locked cell, no notes

    def test_clean_related_notes(self):
        """When a correct number is placed, related notes should be cleaned."""
        self.puzzle = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        self.solution = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]
        gs = GameState(self.puzzle, self.solution)
        # Add note '4' to related cells
        gs.notes[0][3].add(4)  # same row
        gs.notes[1][2].add(4)  # same column
        gs.notes[0][1].add(4)  # same box
        # Place correct number 4 at (0, 2)
        gs.select_cell(0, 2)
        gs.enter_number(4)
        # Related notes should be cleaned
        self.assertNotIn(4, gs.notes[0][3])
        self.assertNotIn(4, gs.notes[1][2])
        self.assertNotIn(4, gs.notes[0][1])


class TestWinDetection(unittest.TestCase):
    """Tests for win detection."""

    def setUp(self) -> None:
        self.puzzle = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        self.solution = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]
        self.gs = GameState(self.puzzle, self.solution)

    def test_not_won_initially(self):
        self.assertFalse(self.gs.is_won)

    def test_win_when_full_correct(self):
        for r in range(9):
            for c in range(9):
                if self.puzzle[r][c] != 0:
                    continue
                self.gs.select_cell(r, c)
                self.gs.enter_number(self.solution[r][c])
        self.assertTrue(self.gs.is_won)
        self.assertTrue(self.gs.is_game_over)

    def test_not_won_with_wrong_number(self):
        # Fill all cells but one is wrong
        self.gs.player_grid = [row[:] for row in self.solution]
        self.gs.player_grid[0][2] = 9  # wrong
        self.assertFalse(self.gs.is_won)


class TestMistakeLimit(unittest.TestCase):
    """Tests for mistake detection and game over."""

    def setUp(self) -> None:
        self.puzzle = [[0] * 9 for _ in range(9)]
        self.solution = [[0] * 9 for _ in range(9)]
        self.gs = GameState(self.puzzle, self.solution, max_mistakes=3)

    def test_mistake_count_increments(self):
        self.gs.select_cell(0, 0)
        for _ in range(3):
            self.gs.enter_number(9)  # wrong
        self.assertEqual(self.gs.mistake_count, 3)

    def test_game_over_at_max_mistakes(self):
        self.gs.select_cell(0, 0)
        for _ in range(3):
            self.gs.enter_number(9)  # wrong
        self.assertTrue(self.gs.is_game_over)

    def test_game_not_over_below_limit(self):
        self.gs.select_cell(0, 0)
        self.gs.enter_number(9)  # wrong
        self.assertFalse(self.gs.is_game_over)

    def test_correct_entries_do_not_increment_mistakes(self):
        self.gs.select_cell(0, 0)
        self.gs.enter_number(1)  # arbitrary number, not checked against solution since solution is all 0
        # With a solution of all zeros, any non-zero is a mistake
        # Let's use a proper solution
        self.solution = [[1] * 9 for _ in range(9)]
        gs2 = GameState(self.puzzle, self.solution, max_mistakes=3)
        gs2.select_cell(0, 0)
        gs2.enter_number(1)  # correct
        self.assertEqual(gs2.mistake_count, 0)


class TestUndo(unittest.TestCase):
    """Tests for undo functionality."""

    def setUp(self) -> None:
        self.puzzle = [[0] * 9 for _ in range(9)]
        self.solution = [[1] * 9 for _ in range(9)]
        self.gs = GameState(self.puzzle, self.solution)

    def test_undo_no_history(self):
        self.assertFalse(self.gs.undo())
        self.assertEqual(len(self.gs.action_history), 0)

    def test_undo_value(self):
        self.gs.select_cell(0, 0)
        self.gs.enter_number(5)
        self.assertEqual(self.gs.player_grid[0][0], 5)
        self.gs.undo()
        self.assertEqual(self.gs.player_grid[0][0], 0)

    def test_undo_multiple(self):
        self.gs.select_cell(0, 0)
        self.gs.enter_number(5)
        self.gs.select_cell(0, 1)
        self.gs.enter_number(6)
        self.gs.undo()
        self.assertEqual(self.gs.player_grid[0][1], 0)
        self.gs.undo()
        self.assertEqual(self.gs.player_grid[0][0], 0)

    def test_undo_note(self):
        self.gs.is_note_mode = True
        self.gs.select_cell(0, 0)
        self.gs.enter_number(3)
        self.gs.enter_number(5)
        self.gs.undo()
        notes = self.gs.get_cell_notes(0, 0)
        self.assertEqual(notes, {3})

    def test_undo_restores_notes(self):
        self.gs.is_note_mode = True
        self.gs.select_cell(0, 0)
        self.gs.enter_number(3)
        self.gs.enter_number(5)
        self.gs.undo()
        notes = self.gs.get_cell_notes(0, 0)
        self.assertEqual(notes, {3})

    def test_undo_value_clears_notes(self):
        """Undo of a value entry restores the cell and its previous notes."""
        self.gs.select_cell(0, 0)
        self.gs.enter_number(5)
        self.gs.notes[0][0].add(3)  # add note after value (not via game state)
        self.gs.undo()
        self.assertEqual(self.gs.player_grid[0][0], 0)
        # previous_notes was empty when value was entered
        self.assertEqual(self.gs.get_cell_notes(0, 0), set())


class TestTimer(unittest.TestCase):
    """Tests for the timer."""

    def setUp(self) -> None:
        self.puzzle = [[0] * 9 for _ in range(9)]
        self.solution = [[0] * 9 for _ in range(9)]
        self.gs = GameState(self.puzzle, self.solution)

    def test_tick_updates_elapsed(self):
        self.gs.tick()
        self.assertGreater(self.gs.elapsed_seconds, 0)

    def test_seconds_property(self):
        self.gs.elapsed_seconds = 65.0
        self.assertEqual(self.gs.minutes, 1)
        self.assertEqual(self.gs.seconds, 5)

    def test_selected_cell_number(self):
        self.gs.select_cell(0, 0)
        self.gs.player_grid[0][0] = 5
        self.assertEqual(self.gs.selected_cell_number, 5)

    def test_selected_cell_number_no_selection(self):
        self.assertEqual(self.gs.selected_cell_number, 0)

    def test_selected_cell_is_locked(self):
        puzzle = [[5] + [0] * 8] + [[0] * 9 for _ in range(8)]
        gs = GameState(puzzle, [[0] * 9 for _ in range(9)])
        gs.select_cell(0, 0)
        self.assertTrue(gs.selected_cell_is_locked)
        gs.select_cell(0, 1)
        self.assertFalse(gs.selected_cell_is_locked)


class TestReset(unittest.TestCase):
    """Tests for the reset method."""

    def setUp(self) -> None:
        self.puzzle = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        self.solution = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]
        self.gs = GameState(self.puzzle, self.solution)

    def test_reset_clears_player_grid(self):
        self.gs.player_grid[0][2] = 4
        self.gs.mistake_count = 2
        self.gs.reset()
        self.assertEqual(self.gs.player_grid[0][2], 0)
        self.assertEqual(self.gs.mistake_count, 0)

    def test_reset_clears_selection(self):
        self.gs.select_cell(3, 3)
        self.gs.reset()
        self.assertEqual(self.gs.selected_row, -1)
        self.assertEqual(self.gs.selected_col, -1)

    def test_reset_clears_history(self):
        self.gs.select_cell(0, 0)
        self.gs.enter_number(5)
        self.gs.reset()
        self.assertEqual(len(self.gs.action_history), 0)

    def test_reset_clears_game_over(self):
        self.gs.is_game_over = True
        self.gs.reset()
        self.assertFalse(self.gs.is_game_over)
        self.assertFalse(self.gs.is_won)


if __name__ == "__main__":
    unittest.main()
