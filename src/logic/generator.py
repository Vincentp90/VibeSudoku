"""Sudoku puzzle generator.

Creates solvable Sudoku puzzles by starting with a full solved board,
shuffling it with valid transformations, then removing cells to
create the puzzle.
"""

from __future__ import annotations

import copy
import random
from typing import List, Optional

from src.logic.validator import SudokuValidator
from src.logic.solver import SudokuSolver

Board = List[List[int]]


class SudokuGenerator:
    """Generate Sudoku puzzles of varying difficulty."""

    # Number of cells to remove per difficulty
    DIFFICULTY_REMOVALS = {
        "easy": 30,
        "medium": 40,
        "hard": 50,
    }

    def __init__(self, seed: Optional[int] = None) -> None:
        """Initialise the generator.

        Parameters
        ----------
        seed : int | None
            Random seed for reproducibility.  ``None`` uses the
            system time.
        """
        self._rng = random.Random(seed)

    def generate(self, difficulty: str = "medium") -> tuple[Board, Board]:
        """Generate a new puzzle.

        Parameters
        ----------
        difficulty : str
            One of ``"easy"``, ``"medium"``, or ``"hard"``.

        Returns
        -------
        tuple[Board, Board]
            ``(puzzle, solution)`` where *puzzle* is the playable board
            (with empty cells as ``0``) and *solution* is the complete
            solved board.

        Raises
        ------
        ValueError
            If *difficulty* is not recognised.
        """
        if difficulty not in self.DIFFICULTY_REMOVALS:
            raise ValueError(
                f"Unknown difficulty '{difficulty}'. "
                f"Choose from {list(self.DIFFICULTY_REMOVALS.keys())}"
            )

        # 1. Build a full solved board
        solution = self._generate_full_board()

        # 2. Remove cells to create the puzzle
        puzzle = copy.deepcopy(solution)
        num_removals = self.DIFFICULTY_REMOVALS[difficulty]
        self._remove_cells(puzzle, num_removals)

        return puzzle, solution

    def _generate_full_board(self) -> Board:
        """Create a complete, valid 9×9 solved Sudoku board.

        Uses a filled diagonal-box strategy followed by backtracking
        to fill the rest, then shuffles with row/column/number
        permutations for variety.
        """
        board: Board = [[0] * 9 for _ in range(9)]

        # Fill the three diagonal 3×3 boxes independently (they don't
        # interfere with each other)
        for box_idx in range(0, 9, 3):
            self._fill_box(board, box_idx, box_idx)

        # Solve the rest with backtracking
        SudokuSolver._backtrack(board)

        # Shuffle for variety
        board = self._shuffle_board(board)

        return board

    def _fill_box(self, board: Board, row: int, col: int) -> None:
        """Fill a 3×3 box at the given top-left corner with 1-9."""
        nums = list(range(1, 10))
        self._rng.shuffle(nums)
        idx = 0
        for r in range(row, row + 3):
            for c in range(col, col + 3):
                board[r][c] = nums[idx]
                idx += 1

    def _shuffle_board(self, board: Board) -> Board:
        """Apply random valid transformations to a solved board.

        Valid transformations include:
        - Swapping rows within the same band (3 bands total)
        - Swapping columns within the same stack (3 stacks total)
        - Permuting the digit labels (1-9)
        - Transposing the board
        """
        board = copy.deepcopy(board)

        # Swap rows within bands
        for band in range(3):
            rows = [board[band * 3 + r] for r in range(3)]
            self._rng.shuffle(rows)
            for r in range(3):
                board[band * 3 + r] = rows[r]

        # Swap columns within stacks
        for stack in range(3):
            # Extract the three columns in this stack
            col_sets = [
                [board[r][stack * 3 + offset] for r in range(9)]
                for offset in range(3)
            ]
            self._rng.shuffle(col_sets)
            for offset in range(3):
                for r in range(9):
                    board[r][stack * 3 + offset] = col_sets[offset][r]

        # Permute digits
        digit_map = {i: i for i in range(1, 10)}
        digits = list(range(1, 10))
        self._rng.shuffle(digits)
        for i, d in enumerate(range(1, 10)):
            digit_map[d] = digits[i]

        for r in range(9):
            for c in range(9):
                board[r][c] = digit_map[board[r][c]]

        # Optionally transpose (50% chance)
        if self._rng.random() > 0.5:
            board = list(zip(*board))
            board = [list(row) for row in board]

        return board

    def _remove_cells(self, board: Board, num_removals: int) -> None:
        """Randomly remove *num_removals* cells from the board.

        After each removal the board is checked to ensure it still has
        a valid solution.  If removing a cell would make the puzzle
        unsolvable, the cell is restored and another position is tried.
        """
        positions = list((r, c) for r in range(9) for c in range(9))
        self._rng.shuffle(positions)

        removed = 0
        for r, c in positions:
            if removed >= num_removals:
                break

            original = board[r][c]
            board[r][c] = 0

            # Quick sanity: the remaining board must still be valid
            if not SudokuValidator.is_valid(board):
                board[r][c] = original
                continue

            # Verify the puzzle still has at least one solution
            if SudokuSolver.solve(board) is None:
                board[r][c] = original
                continue

            removed += 1
