"""Screen state management for Sudoku.

Defines all game screens (menu, difficulty, game, pause, game over,
win) and provides a ``ScreenManager`` that tracks the current screen
and transitions between them.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Optional


class Screen(enum.Enum):
    """Application-level screens."""

    MAIN_MENU = "main_menu"
    DIFFICULTY = "difficulty"
    GAME = "game"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    WIN = "win"


@dataclass
class ScreenManager:
    """Track the current screen and transition between them.

    Parameters
    ----------
    initial : Screen, optional
        The starting screen. Defaults to ``Screen.MAIN_MENU``.
    """

    current: Screen = Screen.MAIN_MENU
    previous: Optional[Screen] = None

    def go_to(self, screen: Screen) -> None:
        """Transition to *screen*, remembering the previous screen.

        Parameters
        ----------
        screen : Screen
            The target screen to display.
        """
        self.previous = self.current
        self.current = screen

    def go_back(self) -> bool:
        """Return to the previous screen.

        Returns ``True`` if a previous screen exists and was
        restored, ``False`` if there is nowhere to go back to.
        """
        if self.previous is None:
            return False
        self.current = self.previous
        self.previous = None
        return True

    @property
    def is_game_active(self) -> bool:
        """Return ``True`` if the game screen is currently active."""
        return self.current in (Screen.GAME, Screen.PAUSED)

    @property
    def is_game_over(self) -> bool:
        """Return ``True`` if the game-over or win screen is active."""
        return self.current in (Screen.GAME_OVER, Screen.WIN)
