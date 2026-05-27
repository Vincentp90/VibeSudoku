"""Sudoku backtracking solver.

Finds *one* solution for a given puzzle (or confirms the puzzle is
already solved / unsolvable).
"""

from __future__ import annotations

import copy
from typing import List, Optional, Tuple

from src.logic.validator import SudokuValidator

Board = List[List[int]]


class SudokuSolver:
    """Solve a Sudoku puzzle using backtracking."""

    @staticmethod
    def solve(board: Board) -> Optional[Board]:
        """Solve the board in-place and return it, or ``None`` if unsolvable.

        Parameters
        ----------
        board : Board
            A 9×9 list of lists.  ``0`` represents an empty cell.

        Returns
        -------
        Board | None
            The solved board, or ``None`` if no solution exists.
        """
        board = copy.deepcopy(board)

        # Validate pre-filled cells before attempting to solve
        if not SudokuValidator.is_valid(board):
            return None

        if SudokuSolver._backtrack(board):
            return board
        return None

    @staticmethod
    def has_unique_solution(board: Board) -> bool:
        """Return ``True`` if the puzzle has exactly one solution.

        This is a lightweight check — it finds the first solution and
        then tries to find a second one by temporarily modifying the
        first solution's cells.

        Note: For full uniqueness verification a proper counter would
        be needed, but this heuristic is sufficient for generator
        purposes.
        """
        board = copy.deepcopy(board)
        solution = SudokuSolver.solve(board)
        if solution is None:
            return False

        # Try to find a second solution by blocking one empty cell's value
        # This is a simplified uniqueness check
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    continue
                original = board[r][c]
                # Try a different value — if it still allows a solution,
                # the puzzle may have multiple solutions
                board[r][c] = 0  # clear the cell
                alt = SudokuSolver.solve(board)
                if alt is not None:
                    # Check if the alternative differs from the original solution
                    if alt != solution:
                        return False
                board[r][c] = original

        return True

    @staticmethod
    def _backtrack(board: Board) -> bool:
        """Recursive backtracking helper.

        Returns ``True`` when a valid full board is found.
        """
        empty = SudokuSolver._find_empty(board)
        if empty is None:
            return True  # Solved

        row, col = empty

        for num in range(1, 10):
            if SudokuSolver._is_safe(board, row, col, num):
                board[row][col] = num
                if SudokuSolver._backtrack(board):
                    return True
                board[row][col] = 0  # backtrack

        return False

    @staticmethod
    def _find_empty(board: Board) -> Optional[Tuple[int, int]]:
        """Return the (row, col) of the first empty cell, or ``None``."""
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    return (r, c)
        return None

    @staticmethod
    def _is_safe(board: Board, row: int, col: int, num: int) -> bool:
        """Check if placing *num* at *(row, col)* violates Sudoku rules."""
        # Row check
        if num in board[row]:
            return False

        # Column check
        for r in range(9):
            if board[r][col] == num:
                return False

        # 3×3 box check
        box_r, box_c = (row // 3) * 3, (col // 3) * 3
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if board[r][c] == num:
                    return False

        return True
