"""Menu rendering for Sudoku.

Handles drawing of the main menu and difficulty selection screens.
"""

from __future__ import annotations

import math
import pygame

from src.ui.display import (
    BACKGROUND,
    FONT_NAME,
    HEIGHT,
    PLAYER_TEXT,
    SELECTED,
    WIDTH,
)

# Font sizes
TITLE_FONT_SIZE: int = 64
MENU_ITEM_FONT_SIZE: int = 36
SUBTITLE_FONT_SIZE: int = 24


class Menu:
    """Render menu screens (main menu, difficulty selection).

    Parameters
    ----------
    screen : pygame.Surface
        The display surface to draw on.
    """

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self._title_font = pygame.font.Font(FONT_NAME, TITLE_FONT_SIZE)
        self._item_font = pygame.font.Font(FONT_NAME, MENU_ITEM_FONT_SIZE)
        self._sub_font = pygame.font.Font(FONT_NAME, SUBTITLE_FONT_SIZE)

    # ------------------------------------------------------------------
    # Main Menu
    # ------------------------------------------------------------------

    def draw_main_menu(self, hovered_index: int = -1) -> None:
        """Draw the main menu screen.

        Parameters
        ----------
        hovered_index : int
            Index of the currently hovered menu item (for highlighting).
            Defaults to ``-1`` (no highlight).
        """
        self.screen.fill(BACKGROUND)

        # Title
        title = self._title_font.render("Sudoku", True, (30, 30, 30))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self._sub_font.render("A relaxing puzzle game", True, (120, 120, 120))
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 50))
        self.screen.blit(subtitle, subtitle_rect)

        # Menu items
        items = ["New Game", "Quit"]
        menu_y = HEIGHT // 2

        for idx, label in enumerate(items):
            color = SELECTED if idx == hovered_index else (50, 50, 50)
            text = self._item_font.render(label, True, color)
            text_rect = text.get_rect(center=(WIDTH // 2, menu_y + idx * 70))
            self.screen.blit(text, text_rect)

        # Footer hint
        hint = self._sub_font.render("Press Enter to select", True, (160, 160, 160))
        hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.screen.blit(hint, hint_rect)

    # ------------------------------------------------------------------
    # Difficulty Selection
    # ------------------------------------------------------------------

    def draw_difficulty_menu(self, hovered_index: int = -1) -> None:
        """Draw the difficulty selection screen.

        Parameters
        ----------
        hovered_index : int
            Index of the currently hovered difficulty option.
        """
        self.screen.fill(BACKGROUND)

        # Title
        title = self._title_font.render("Select Difficulty", True, (30, 30, 30))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3 - 20))
        self.screen.blit(title, title_rect)

        # Difficulty options
        difficulties = [
            ("Easy", "Few cells removed — great for beginners"),
            ("Medium", "Balanced challenge"),
            ("Hard", "Many cells removed — for experts"),
        ]
        menu_y = HEIGHT // 2

        for idx, (label, description) in enumerate(difficulties):
            # Background highlight for hovered item
            item_rect = pygame.Rect(
                WIDTH // 2 - 160,
                menu_y + idx * 80 - 20,
                320,
                60,
            )
            if idx == hovered_index:
                pygame.draw.rect(self.screen, SELECTED, item_rect, border_radius=8)

            # Label
            color = (30, 30, 30) if idx == hovered_index else (80, 80, 80)
            text = self._item_font.render(label, True, color)
            text_rect = text.get_rect(center=(WIDTH // 2, menu_y + idx * 80 - 5))
            self.screen.blit(text, text_rect)

            # Description
            desc = self._sub_font.render(description, True, (150, 150, 150))
            desc_rect = desc.get_rect(center=(WIDTH // 2, menu_y + idx * 80 + 22))
            self.screen.blit(desc, desc_rect)

        # Back hint
        hint = self._sub_font.render("Press Esc to go back", True, (160, 160, 160))
        hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.screen.blit(hint, hint_rect)
