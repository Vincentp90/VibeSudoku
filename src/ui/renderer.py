"""Pygame renderer for Sudoku.

Handles all drawing: grid, numbers, highlights, notes, HUD, and
game-over / win overlays.
"""

from __future__ import annotations

import math
import pygame

from src.game_state import GameState
from src.ui.screens import Screen
from src.ui.theme import (
    BACKGROUND,
    CELL_SIZE,
    FONT_NAME,
    GRID_LINE,
    GRID_OFFSET_X,
    GRID_OFFSET_Y,
    GRID_SIZE,
    HUD_HEIGHT,
    HUD_FONT_SIZE,
    HIGHLIGHT,
    INVALID,
    LOCKED_TEXT,
    NOTE_FONT_SIZE,
    NUMBER_FONT_SIZE,
    OVERLAY_FONT_SIZE,
    PEER_HIGHLIGHT,
    PLAYER_TEXT,
    SELECTED,
    WIDTH,
)


class Renderer:
    """Render the Sudoku game state onto a Pygame surface.

    Parameters
    ----------
    screen : pygame.Surface
        The display surface to draw on.
    font : pygame.font.Font | None
        Custom font.  ``None`` uses the default TTF or Pygame's
        built-in font.
    """

    def __init__(self, screen: pygame.Surface, font=None) -> None:
        self.screen = screen
        self.font = font
        self._number_font = pygame.font.Font(FONT_NAME, NUMBER_FONT_SIZE)
        self._note_font = pygame.font.Font(FONT_NAME, NOTE_FONT_SIZE)
        self._hud_font = pygame.font.Font(FONT_NAME, HUD_FONT_SIZE)
        self._overlay_font = pygame.font.Font(FONT_NAME, OVERLAY_FONT_SIZE)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, state: GameState, screen: Screen = Screen.GAME) -> None:
        """Render the complete game state.

        Parameters
        ----------
        state : GameState
            The current game state.
        screen : Screen
            The current application screen. Defaults to ``Screen.GAME``.
        """
        self.screen.fill(BACKGROUND)

        if screen == Screen.GAME:
            self._draw_grid(state)
            self._draw_hud(state)

            if state.is_won:
                self._draw_win_overlay(state)
            elif state.is_game_over:
                self._draw_game_over_overlay(state)

        elif screen == Screen.PAUSED:
            self._draw_grid(state)
            self._draw_hud(state)
            self._draw_pause_overlay()

        elif screen == Screen.GAME_OVER:
            self._draw_game_over_overlay(state)

        elif screen == Screen.WIN:
            self._draw_win_overlay(state)

        pygame.display.flip()

    # ------------------------------------------------------------------
    # Grid & cells
    # ------------------------------------------------------------------

    def _draw_grid(self, state: GameState) -> None:
        """Draw the 9×9 grid with lines and numbers."""
        self._draw_cell_backgrounds(state)
        self._draw_numbers(state)
        self._draw_notes(state)
        self._draw_lines()

    def _draw_cell_backgrounds(self, state: GameState) -> None:
        """Fill cell backgrounds with highlight colours."""
        sel_r, sel_c = state.selected_row, state.selected_col

        for r in range(9):
            for c in range(9):
                x, y = c * CELL_SIZE, r * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                color = None

                if state.is_game_over or state.is_won:
                    color = None  # no highlights during overlay
                elif r == sel_r and c == sel_c:
                    color = SELECTED
                elif state.selected_row >= 0:
                    sel_num = state.player_grid[sel_r][sel_c]
                    # Same number highlight
                    if state.player_grid[r][c] == sel_num and sel_num != 0:
                        color = HIGHLIGHT
                    # Peer highlight (same row / col / box)
                    elif (
                        r == sel_r
                        or c == sel_c
                        or (
                            r // 3 == sel_r // 3
                            and c // 3 == sel_c // 3
                        )
                    ):
                        color = PEER_HIGHLIGHT

                if color:
                    pygame.draw.rect(self.screen, color, rect)

    def _draw_numbers(self, state: GameState) -> None:
        """Render all numbers (locked and player-entered)."""
        sel_r, sel_c = state.selected_row, state.selected_col
        selected_num = state.player_grid[sel_r][sel_c] if sel_r >= 0 else 0

        for r in range(9):
            for c in range(9):
                value = state.player_grid[r][c]
                if value == 0:
                    continue

                x = c * CELL_SIZE + CELL_SIZE // 2
                y = r * CELL_SIZE + CELL_SIZE // 2

                # Determine colour
                if state.puzzle[r][c] != 0:
                    # Locked (given) number
                    color = LOCKED_TEXT
                elif value != state.solution[r][c]:
                    # Player-entered but WRONG (invalid)
                    color = INVALID
                elif r == sel_r and c == sel_c:
                    # Selected cell
                    color = SELECTED
                else:
                    # Player-entered, correct
                    color = PLAYER_TEXT

                text = self._number_font.render(str(value), True, color)
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)

    def _draw_notes(self, state: GameState) -> None:
        """Render small pencil-mark notes in each cell."""
        sel_r, sel_c = state.selected_row, state.selected_col

        for r in range(9):
            for c in range(9):
                notes = state.get_cell_notes(r, c)
                if not notes:
                    continue

                # Skip notes in locked cells
                if state.puzzle[r][c] != 0:
                    continue

                # Skip notes in cells with a confirmed value
                if state.player_grid[r][c] != 0:
                    continue

                x0 = c * CELL_SIZE
                y0 = r * CELL_SIZE
                note_size = CELL_SIZE // 3  # 3x3 grid per cell

                for idx, num in enumerate(sorted(notes)):
                    col_offset = idx % 3
                    row_offset = idx // 3
                    nx = x0 + col_offset * note_size + note_size // 2
                    ny = y0 + row_offset * note_size + note_size // 2

                    text = self._note_font.render(str(num), True, (100, 100, 100))
                    text_rect = text.get_rect(center=(nx, ny))
                    self.screen.blit(text, text_rect)

    def _draw_lines(self) -> None:
        """Draw the Sudoku grid lines (thin inside boxes, thick between)."""
        for i in range(10):
            x = i * CELL_SIZE
            # Thick line every 3 cells
            line_width = 3 if i % 3 == 0 else 1
            pygame.draw.line(
                self.screen,
                THICK_GRID_LINE if line_width == 3 else GRID_LINE,
                (x, GRID_OFFSET_Y),
                (x, GRID_OFFSET_Y + GRID_SIZE),
                line_width,
            )

        for j in range(10):
            y = j * CELL_SIZE
            line_width = 3 if j % 3 == 0 else 1
            pygame.draw.line(
                self.screen,
                THICK_GRID_LINE if line_width == 3 else GRID_LINE,
                (GRID_OFFSET_X, y),
                (GRID_OFFSET_X + GRID_SIZE, y),
                line_width,
            )

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------

    def _draw_hud(self, state: GameState) -> None:
        """Draw the heads-up display (timer and mistakes)."""
        hud_y = GRID_SIZE + 10

        # Timer
        timer_text = self._hud_font.render(
            f"Time: {state.minutes:02d}:{state.seconds:02d}",
            True, (50, 50, 50),
        )
        self.screen.blit(timer_text, (10, hud_y))

        # Mistakes
        mistake_text = self._hud_font.render(
            f"Mistakes: {state.mistake_count}/{state.max_mistakes}",
            True, INVALID if state.mistake_count >= state.max_mistakes - 1 else (50, 50, 50),
        )
        self.screen.blit(mistake_text, (10, hud_y + HUD_FONT_SIZE + 5))

    # ------------------------------------------------------------------
    # Overlays
    # ------------------------------------------------------------------

    def _draw_pause_overlay(self) -> None:
        """Draw the pause screen overlay."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        title = self._overlay_font.render("Paused", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        self.screen.blit(title, title_rect)

        hint = self._hud_font.render("Press P to resume", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        self.screen.blit(hint, hint_rect)

    def _draw_game_over_overlay(self, state: GameState) -> None:
        """Draw the game-over overlay with elapsed time.

        Parameters
        ----------
        state : GameState
            The current game state.
        """
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        title = self._overlay_font.render("Game Over", True, (192, 57, 43))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(title, title_rect)

        # Elapsed time
        total_seconds = int(state.elapsed_seconds)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_text = self._hud_font.render(
            f"Time: {minutes:02d}:{seconds:02d}",
            True, (200, 200, 200),
        )
        time_rect = time_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(time_text, time_rect)

        # Mistakes
        mistake_text = self._hud_font.render(
            f"Mistakes: {state.mistake_count}/{state.max_mistakes}",
            True, INVALID,
        )
        mistake_rect = mistake_text.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 40),
        )
        self.screen.blit(mistake_text, mistake_rect)

        restart = self._sub_font.render(
            "Press Space to play again",
            True, (200, 200, 200),
        )
        restart_rect = restart.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 90),
        )
        self.screen.blit(restart, restart_rect)

    def _draw_win_overlay(self, state: GameState) -> None:
        """Draw the win overlay with elapsed time.

        Parameters
        ----------
        state : GameState
            The current game state.
        """
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        title = self._overlay_font.render("You Win!", True, (46, 204, 113))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(title, title_rect)

        # Elapsed time
        total_seconds = int(state.elapsed_seconds)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_text = self._hud_font.render(
            f"Time: {minutes:02d}:{seconds:02d}",
            True, (200, 200, 200),
        )
        time_rect = time_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(time_text, time_rect)

        restart = self._sub_font.render(
            "Press Space to play again",
            True, (200, 200, 200),
        )
        restart_rect = restart.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 50),
        )
        self.screen.blit(restart, restart_rect)
