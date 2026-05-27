"""Sudoku board validator.

Checks whether a partially-filled 9×9 board is valid (no conflicts
among the filled cells) and whether a fully-filled board is a
correct solution.
"""

from __future__ import annotations

from typing import List


# Type alias for clarity
Board = List[List[int]]


class SudokuValidator:
    """Stateless validator for Sudoku boards."""

    @staticmethod
    def is_valid(board: Board) -> bool:
        """Return ``True`` if the board has *no* conflicts among filled cells.

        A conflict occurs when the same number appears more than once
        in any row, column, or 3×3 box.  Empty cells (value ``0``) are
        ignored.
        """
        if len(board) != 9:
            return False
        for row in board:
            if len(row) != 9:
                return False

        for i in range(9):
            if not SudokuValidator._check_group(board, i):
                return False

        return True

    @staticmethod
    def is_solution(board: Board) -> bool:
        """Return ``True`` if *every* cell is filled and the board is valid.

        Unlike :meth:`is_valid`, this rejects any board with empty
        cells (``0``).
        """
        for row in board:
            for cell in row:
                if cell == 0:
                    return False
        return SudokuValidator.is_valid(board)

    @staticmethod
    def _check_group(board: Board, index: int) -> bool:
        """Validate one row, column, or box by index.

        Parameters
        ----------
        index : int
            ``0-8`` for rows, ``9-17`` for columns, ``18-26`` for boxes.
        """
        seen: set[int] = set()

        if 0 <= index <= 8:
            # Row
            group = board[index]
        elif 9 <= index <= 17:
            # Column
            group = [board[r][index - 9] for r in range(9)]
        else:
            # 3×3 box
            box_idx = index - 18
            start_row, start_col = (box_idx // 3) * 3, (box_idx % 3) * 3
            group = [
                board[start_row + r][start_col + c]
                for r in range(3)
                for c in range(3)
            ]

        for value in group:
            if value == 0:
                continue
            if value < 1 or value > 9:
                return False
            if value in seen:
                return False
            seen.add(value)

        return True
