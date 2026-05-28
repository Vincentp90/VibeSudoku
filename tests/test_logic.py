"""Unit tests for core Sudoku logic: validator, solver, and generator."""

import unittest

from src.logic.validator import SudokuValidator
from src.logic.solver import SudokuSolver
from src.logic.generator import SudokuGenerator


class TestSudokuValidator(unittest.TestCase):
    """Tests for :class:`~src.logic.validator.SudokuValidator`."""

    def _make_board(self, rows: list[str]) -> list[list[int]]:
        """Helper to turn a list of digit-strings into a 9×9 int board."""
        return [[int(c) for c in row] for row in rows]

    # -- is_valid --

    def test_empty_board_is_valid(self):
        board = [[0] * 9 for _ in range(9)]
        self.assertTrue(SudokuValidator.is_valid(board))

    def test_solved_board_is_valid(self):
        solved = self._make_board([
            "534678912",
            "672195348",
            "198342567",
            "859761423",
            "426853791",
            "713924856",
            "961537284",
            "287419635",
            "345826179",
        ])
        self.assertTrue(SudokuValidator.is_valid(solved))

    def test_conflict_in_row(self):
        board = self._make_board([
            "534678912",
            "672195348",
            "198342567",
            "859761423",
            "426853791",
            "713924856",
            "961537284",
            "287419635",
            "345826179",
        ])
        # Introduce a conflict: duplicate '5' in row 0
        board[0][1] = 5
        self.assertFalse(SudokuValidator.is_valid(board))

    def test_conflict_in_column(self):
        board = self._make_board([
            "534678912",
            "672195348",
            "198342567",
            "859761423",
            "426853791",
            "713924856",
            "961537284",
            "287419635",
            "345826179",
        ])
        # Duplicate '6' in column 0
        board[1][0] = 5
        self.assertFalse(SudokuValidator.is_valid(board))

    def test_conflict_in_box(self):
        board = self._make_board([
            "534678912",
            "672195348",
            "198342567",
            "859761423",
            "426853791",
            "713924856",
            "961537284",
            "287419635",
            "345826179",
        ])
        # Duplicate '3' in top-left 3×3 box: (0,1)=3, change (2,1) to 3
        board[2][1] = 3
        self.assertFalse(SudokuValidator.is_valid(board))

    def test_invalid_number(self):
        board = self._make_board([
            "534678912",
            "672195348",
            "198342567",
            "859761423",
            "426853791",
            "713924856",
            "961537284",
            "287419635",
            "345826179",
        ])
        board[0][0] = 10  # out of range
        self.assertFalse(SudokuValidator.is_valid(board))

    def test_is_solution_empty_board(self):
        board = [[0] * 9 for _ in range(9)]
        self.assertFalse(SudokuValidator.is_solution(board))

    def test_is_solution_partial(self):
        board = [[0] * 9 for _ in range(9)]
        board[0][0] = 5
        self.assertFalse(SudokuValidator.is_solution(board))

    def test_is_solution_valid_full(self):
        solved = self._make_board([
            "534678912",
            "672195348",
            "198342567",
            "859761423",
            "426853791",
            "713924856",
            "961537284",
            "287419635",
            "345826179",
        ])
        self.assertTrue(SudokuValidator.is_solution(solved))

    # -- malformed board --

    def test_wrong_number_of_rows(self):
        board = [[0] * 9 for _ in range(8)]
        self.assertFalse(SudokuValidator.is_valid(board))

    def test_wrong_number_of_cols(self):
        board = [[0] * 8 for _ in range(9)]
        self.assertFalse(SudokuValidator.is_valid(board))


class TestSudokuSolver(unittest.TestCase):
    """Tests for :class:`~src.logic.solver.SudokuSolver`."""

    def test_solve_empty_board(self):
        board = [[0] * 9 for _ in range(9)]
        result = SudokuSolver.solve(board)
        self.assertIsNotNone(result)
        self.assertTrue(SudokuValidator.is_solution(result))

    def test_solve_easy_puzzle(self):
        # A well-known easy Sudoku puzzle
        board = self._make_board([
            "530070000",
            "600195000",
            "098000060",
            "800060003",
            "400803001",
            "700020006",
            "060000280",
            "000419005",
            "000080079",
        ])
        result = SudokuSolver.solve(board)
        self.assertIsNotNone(result)
        self.assertTrue(SudokuValidator.is_solution(result))

    def test_solve_already_solved(self):
        solved = self._make_board([
            "534678912",
            "672195348",
            "198342567",
            "859761423",
            "426853791",
            "713924856",
            "961537284",
            "287419635",
            "345826179",
        ])
        result = SudokuSolver.solve(solved)
        self.assertIsNotNone(result)
        self.assertEqual(result, solved)

    def test_solve_unsolvable(self):
        # Two 5s in the same row — impossible to solve
        board = self._make_board([
            "534678912",
            "672195348",
            "198342567",
            "859761423",
            "426853791",
            "713924856",
            "961537284",
            "287419635",
            "345826179",
        ])
        board[0][1] = 5  # conflict with board[0][0]
        result = SudokuSolver.solve(board)
        self.assertIsNone(result)

    def test_solve_preserves_original(self):
        board = self._make_board([
            "530070000",
            "600195000",
            "098000060",
            "800060003",
            "400803001",
            "700020006",
            "060000280",
            "000419005",
            "000080079",
        ])
        original = [row[:] for row in board]
        SudokuSolver.solve(board)
        self.assertEqual(board, original)  # deep copy, original unchanged

    def _make_board(self, rows: list[str]) -> list[list[int]]:
        return [[int(c) for c in row] for row in rows]


class TestSudokuGenerator(unittest.TestCase):
    """Tests for :class:`~src.logic.generator.SudokuGenerator`."""

    def setUp(self) -> None:
        self.generator = SudokuGenerator(seed=42)

    def test_generate_returns_two_boards(self):
        puzzle, solution = self.generator.generate("medium")
        self.assertIsInstance(puzzle, list)
        self.assertIsInstance(solution, list)
        self.assertEqual(len(puzzle), 9)
        self.assertEqual(len(solution), 9)
        # Puzzle and solution must be independent copies
        puzzle[0][0] = 99
        self.assertNotEqual(puzzle[0][0], solution[0][0])

    def test_puzzle_cells_are_subset_of_solution(self):
        puzzle, solution = self.generator.generate("easy")
        for r in range(9):
            for c in range(9):
                if puzzle[r][c] != 0:
                    self.assertEqual(puzzle[r][c], solution[r][c])

    def test_puzzle_is_valid(self):
        puzzle, solution = self.generator.generate("hard")
        self.assertTrue(SudokuValidator.is_valid(puzzle))
        # Puzzle must have empty cells to be playable
        empty_count = sum(
            1 for r in range(9) for c in range(9) if puzzle[r][c] == 0
        )
        self.assertGreater(empty_count, 0)

    def test_solution_is_valid(self):
        _, solution = self.generator.generate("easy")
        self.assertTrue(SudokuValidator.is_solution(solution))

    def test_solution_is_solved(self):
        _, solution = self.generator.generate("medium")
        self.assertTrue(SudokuValidator.is_solution(solution))

    def test_difficulty_levels(self):
        """Each difficulty should remove a different number of cells.

        Easy should have more filled cells than medium, which should have
        more than hard.
        """
        results = {}
        for diff in ["easy", "medium", "hard"]:
            puzzle, _ = self.generator.generate(diff)
            filled = sum(
                1 for r in range(9) for c in range(9) if puzzle[r][c] != 0
            )
            results[diff] = filled
            self.assertGreater(filled, 0)
        # Verify difficulty ordering: easy > medium > hard
        self.assertGreater(results["easy"], results["medium"])
        self.assertGreater(results["medium"], results["hard"])

    def test_invalid_difficulty(self):
        with self.assertRaises(ValueError):
            self.generator.generate("extreme")

    def test_reproducible_with_seed(self):
        gen1 = SudokuGenerator(seed=123)
        gen2 = SudokuGenerator(seed=123)
        p1, s1 = gen1.generate("easy")
        p2, s2 = gen2.generate("easy")
        self.assertEqual(p1, p2)
        self.assertEqual(s1, s2)

    def test_all_difficulties_work(self):
        for diff in ["easy", "medium", "hard"]:
            puzzle, solution = self.generator.generate(diff)
            self.assertTrue(SudokuValidator.is_valid(puzzle))
            self.assertTrue(SudokuValidator.is_solution(solution))


if __name__ == "__main__":
    unittest.main()
