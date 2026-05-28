"""Game state management for Sudoku.

Holds the puzzle, solution, player grid, notes, selection state,
timer, mistake tracking, and action history for undo support.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

Board = List[List[int]]


@dataclass
class Action:
    """Represents a single player action for undo support."""

    row: int
    col: int
    previous_value: int
    new_value: int
    was_note: bool = False
    previous_notes: Set[int] = field(default_factory=set)


@dataclass
class GameState:
    """Encapsulate all mutable state for one game session.

    Parameters
    ----------
    puzzle : Board
        The original puzzle with given (locked) cells and 0 for empty.
    solution : Board
        The complete solved board.
    max_mistakes : int, optional
        Maximum allowed mistakes before game over (default 3).
    """

    puzzle: Board
    solution: Board
    max_mistakes: int = 3

    # Player's current grid (starts as a copy of the puzzle)
    player_grid: Board = field(default_factory=lambda: [[0] * 9 for _ in range(9)])

    # Notes (pencil marks) per cell: (row, col) -> set of candidate numbers
    notes: List[List[Set[int]]] = field(default_factory=lambda: [[set() for _ in range(9)] for _ in range(9)])

    # Selected cell position
    selected_row: int = -1
    selected_col: int = -1

    # Timer
    _start_time: float = field(default=0.0, repr=False)
    elapsed_seconds: float = 0.0

    # Mistakes
    mistake_count: int = 0

    # History for undo
    action_history: List[Action] = field(default_factory=list)

    # Game status flags
    is_note_mode: bool = False
    is_game_over: bool = False
    is_won: bool = False

    # Hint system
    max_hints: int = 3
    hints_used: int = 0
    hinted_cell: Tuple[int, int] = (-1, -1)

    # Animation state
    flash_cell: Tuple[int, int] = (-1, -1)  # Cell that just had a number placed
    _flash_time: float = 0.0  # Timestamp when the flash started

    def __post_init__(self) -> None:
        """Initialize player_grid from puzzle and start the timer."""
        self.player_grid = [row[:] for row in self.puzzle]
        self._start_time = time.time()

    # ------------------------------------------------------------------
    # Timer
    # ------------------------------------------------------------------

    def tick(self) -> None:
        """Update elapsed time. Call once per frame from the game loop."""
        self.elapsed_seconds = time.time() - self._start_time

    @property
    def minutes(self) -> int:
        """Elapsed minutes (integer)."""
        return int(self.elapsed_seconds) // 60

    @property
    def seconds(self) -> int:
        """Elapsed seconds within the current minute (0-59)."""
        return int(self.elapsed_seconds) % 60

    # ------------------------------------------------------------------
    # Cell selection
    # ------------------------------------------------------------------

    def select_cell(self, row: int, col: int) -> None:
        """Select the cell at *(row, col)*.

        Parameters
        ----------
        row : int
            Row index (0-8).
        col : int
            Column index (0-8).
        """
        if 0 <= row < 9 and 0 <= col < 9:
            self.selected_row = row
            self.selected_col = col

    def select_next(self, direction: str) -> None:
        """Move the selection in the given direction.

        Parameters
        ----------
        direction : str
            One of ``"up"``, ``"down"``, ``"left"``, ``"right"``.
        """
        r, c = self.selected_row, self.selected_col
        if direction == "up":
            r = max(0, r - 1)
        elif direction == "down":
            r = min(8, r + 1)
        elif direction == "left":
            c = max(0, c - 1)
        elif direction == "right":
            c = min(8, c + 1)
        self.select_cell(r, c)

    # ------------------------------------------------------------------
    # Number input
    # ------------------------------------------------------------------

    def enter_number(self, number: int) -> None:
        """Enter a number (1-9) into the selected cell.

        If note mode is active, adds the number as a candidate.
        Otherwise, places the number as the cell value.

        Parameters
        ----------
        number : int
            The number to enter (1-9).
        """
        if self.selected_row < 0 or self.selected_col < 0:
            return

        r, c = self.selected_row, self.selected_col

        # Cannot modify given (locked) cells
        if self.puzzle[r][c] != 0:
            return

        if self.is_note_mode:
            self._enter_note(r, c, number)
        else:
            self._enter_value(r, c, number)

    def _enter_value(self, row: int, col: int, number: int) -> None:
        """Place a confirmed number in a cell."""
        if number == 0:
            return  # 0 is not a valid number to enter; use erase() instead
        previous_value = self.player_grid[row][col]
        previous_notes = set(self.notes[row][col])

        # Save action for undo
        self.action_history.append(Action(
            row=row,
            col=col,
            previous_value=previous_value,
            new_value=number,
            previous_notes=previous_notes,
        ))

        self.player_grid[row][col] = number
        self.flash_cell = (row, col)
        self._flash_time = time.time()

        # Check if this is a mistake
        if number != self.solution[row][col]:
            self.mistake_count += 1
            if self.mistake_count >= self.max_mistakes:
                self.is_game_over = True
        else:
            # Correct entry — clean up notes in related cells
            self._clean_related_notes(row, col, number)

        # Check for win
        self._check_win()

    def _enter_note(self, row: int, col: int, number: int) -> None:
        """Add a note/candidate to the selected cell."""
        if not (1 <= number <= 9):
            return

        previous_notes = set(self.notes[row][col])
        self.notes[row][col].add(number)

        self.action_history.append(Action(
            row=row,
            col=col,
            previous_value=0,
            new_value=0,
            was_note=True,
            previous_notes=previous_notes,
        ))

    def erase(self) -> None:
        """Erase the selected cell (backspace/delete).

        Resets the cell value and its notes to empty.
        """
        if self.selected_row < 0 or self.selected_col < 0:
            return

        r, c = self.selected_row, self.selected_col

        # Cannot modify given (locked) cells
        if self.puzzle[r][c] != 0:
            return

        previous_value = self.player_grid[r][c]
        previous_notes = set(self.notes[r][c])

        if previous_value == 0 and not previous_notes:
            return  # Nothing to erase

        self.action_history.append(Action(
            row=r,
            col=c,
            previous_value=previous_value,
            new_value=0,
            previous_notes=previous_notes,
        ))

        self.player_grid[r][c] = 0
        self.notes[r][c].clear()
        self.flash_cell = (-1, -1)
        self._flash_time = 0.0

    def _clean_related_notes(self, row: int, col: int, number: int) -> None:
        """Remove *number* from notes in the same row, column, and box."""
        # Same row
        for c in range(9):
            self.notes[row][c].discard(number)
        # Same column
        for r in range(9):
            self.notes[r][col].discard(number)
        # Same 3x3 box
        box_r, box_c = (row // 3) * 3, (col // 3) * 3
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                self.notes[r][c].discard(number)

    # ------------------------------------------------------------------
    # Undo
    # ------------------------------------------------------------------

    def undo(self) -> bool:
        """Undo the last action.

        Returns ``True`` if an action was undone, ``False`` if nothing
        to undo.
        """
        if not self.action_history:
            return False

        action = self.action_history.pop()

        if action.was_note:
            # Restore notes
            self.notes[action.row][action.col] = set(action.previous_notes)
        else:
            # Restore cell value
            self.player_grid[action.row][action.col] = action.previous_value
            # Restore notes for this cell
            self.notes[action.row][action.col] = set(action.previous_notes)

        return True

    # ------------------------------------------------------------------
    # Win / Game Over
    # ------------------------------------------------------------------

    def _check_win(self) -> None:
        """Check if the player has correctly solved the puzzle."""
        if self.is_game_over:
            return

        for r in range(9):
            for c in range(9):
                if self.player_grid[r][c] != self.solution[r][c]:
                    return

        self.is_won = True
        self.is_game_over = True

    @property
    def is_over(self) -> bool:
        """Return ``True`` if the game is over (won or lost)."""
        return self.is_game_over

    @property
    def selected_cell_is_locked(self) -> bool:
        """Return ``True`` if the currently selected cell is a given (locked) cell."""
        if self.selected_row < 0 or self.selected_col < 0:
            return False
        return self.puzzle[self.selected_row][self.selected_col] != 0

    @property
    def selected_cell_number(self) -> int:
        """Return the number in the selected cell, or 0 if none."""
        if self.selected_row < 0 or self.selected_col < 0:
            return 0
        return self.player_grid[self.selected_row][self.selected_col]

    def get_cell_notes(self, row: int, col: int) -> Set[int]:
        """Return the set of candidate notes for a cell."""
        return set(self.notes[row][col])

    def toggle_note_mode(self) -> None:
        """Toggle note/pencil mode on/off."""
        self.is_note_mode = not self.is_note_mode

    def give_hint(self) -> bool:
        """Reveal one empty cell with the correct answer.

        Uses one hint per call (up to ``max_hints``).  The hinted cell
        is filled with the correct number and the cell position is
        recorded so the renderer can highlight it.

        Returns ``True`` if a hint was given, ``False`` if no hints
        remain or the puzzle is already complete.
        """
        if self.hints_used >= self.max_hints:
            return False
        if self.is_won or self.is_game_over:
            return False

        # Find an empty cell
        empty_cells: List[Tuple[int, int]] = []
        for r in range(9):
            for c in range(9):
                if self.player_grid[r][c] == 0:
                    empty_cells.append((r, c))

        if not empty_cells:
            return False  # puzzle already complete

        # Pick the first empty cell (deterministic)
        r, c = empty_cells[0]

        # Record the hinted cell for rendering
        self.hinted_cell = (r, c)

        # Place the correct number
        self.player_grid[r][c] = self.solution[r][c]

        # Clean up related notes (same as a correct entry)
        self._clean_related_notes(r, c, self.solution[r][c])

        # Clear the hint highlight after one use
        self.hints_used += 1

        # Check for win
        self._check_win()

        return True

    def reset_hint(self) -> None:
        """Clear the current hint highlight."""
        self.hinted_cell = (-1, -1)

    def reset(self) -> None:
        """Reset the game state to a fresh start (same puzzle/solution)."""
        self.player_grid = [row[:] for row in self.puzzle]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.selected_row = -1
        self.selected_col = -1
        self.elapsed_seconds = 0.0
        self._start_time = time.time()
        self.mistake_count = 0
        self.action_history.clear()
        self.is_note_mode = False
        self.is_game_over = False
        self.is_won = False
        self.hints_used = 0
        self.hinted_cell = (-1, -1)
        self.flash_cell = (-1, -1)
        self._flash_time = 0.0
