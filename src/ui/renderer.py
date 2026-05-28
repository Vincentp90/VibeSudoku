"""Pygame renderer for Sudoku.

Handles all drawing: grid, numbers, highlights, notes, HUD, and
game-over / win overlays.
"""

from __future__ import annotations

import math
import time

import pygame

from src.game_state import GameState
from src.ui.screens import Screen
from src.ui.theme import (
    BACKGROUND,
    CELL_SIZE,
    FONT_NAME,
    GRID_LINE,
    THICK_GRID_LINE,
    GRID_OFFSET_X,
    GRID_OFFSET_Y,
    GRID_SIZE,
    HUD_HEIGHT,
    HUD_FONT_SIZE,
    HINT,
    HIGHLIGHT,
    INVALID,
    LOCKED_TEXT,
    NOTE_COLOR,
    NOTE_FONT_SIZE,
    NUMBER_FONT_SIZE,
    OVERLAY_FONT_SIZE,
    OVERLAY_TEXT_COLOR,
    PEER_HIGHLIGHT,
    PLAYER_TEXT,
    SELECTED,
    WIDTH,
    HEIGHT,
    HUD_TEXT_COLOR,
    OVERLAY_TITLE_COLOR,
    WIN_TITLE_COLOR,
    GAME_OVER_TITLE_COLOR,
    FOOTER_FONT_SIZE,
    SHORTCUT_KEY_COLOR,
    SHORTCUT_DESC_COLOR,
    SHORTCUT_CLOSE_COLOR,
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
        self._sub_font = pygame.font.Font(FONT_NAME, FOOTER_FONT_SIZE)

        # Animation state
        self._flash_timer: float = 0.0  # Time since last number placement (seconds)
        self._flash_duration: float = 0.3  # Flash lasts 300ms
        self._selected_cell_timestamp: float = 0.0  # When cell was selected (for pulse)

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

    # ------------------------------------------------------------------
    # Grid & cells
    # ------------------------------------------------------------------

    def _draw_grid(self, state: GameState) -> None:
        """Draw the 9×9 grid with lines and numbers."""
        self._draw_cell_backgrounds(state)
        self._draw_numbers(state)
        self._draw_notes(state)
        self._draw_animations(state)
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
                    # Hint highlight (overrides peer highlights)
                    if (r, c) == state.hinted_cell:
                        color = HINT
                    # Same number highlight
                    elif state.player_grid[r][c] == sel_num and sel_num != 0:
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
                    # Selected cell — use PLAYER_TEXT so number is visible against SELECTED background
                    color = PLAYER_TEXT
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

                    text = self._note_font.render(str(num), True, NOTE_COLOR)
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
    # Animations
    # ------------------------------------------------------------------

    def _draw_animations(self, state: GameState) -> None:
        """Draw subtle animation effects (selection pulse, number flash)."""
        self._draw_selection_pulse(state)
        self._draw_number_flash(state)

    def _draw_selection_pulse(self, state: GameState) -> None:
        """Draw a subtle pulsing border on the selected cell.

        The border oscillates between SELECTED and a brighter highlight
        using a sine wave for smooth easing.
        """
        r, c = state.selected_row, state.selected_col
        if r < 0 or c < 0:
            return

        # Skip if this cell is already highlighted (e.g. same number, hint)
        if state.hinted_cell == (r, c):
            return

        # Use a sine wave for smooth pulsing (period ~2 seconds)
        import math
        pulse = math.sin(state.elapsed_seconds * math.pi) * 0.5 + 0.5  # 0→1→0

        # Interpolate border width: 1 (thin) → 3 (thick)
        border_width = int(1 + pulse * 2)

        x = c * CELL_SIZE
        y = r * CELL_SIZE

        # Draw a border around the cell
        pygame.draw.rect(
            self.screen,
            SELECTED,
            (x, y, CELL_SIZE, CELL_SIZE),
            border_width,
        )

    def _draw_number_flash(self, state: GameState) -> None:
        """Draw a brief flash effect on a cell that just received a number.

        The flash fades out over ``_flash_duration`` seconds.
        """
        fr, fc = state.flash_cell
        if fr < 0 or fc < 0:
            return

        # Calculate how long ago the flash started
        elapsed = time.time() - state._flash_time
        if elapsed > self._flash_duration:
            return

        # Fade from 0.5 alpha to 0 over flash_duration
        flash_intensity = 1.0 - (elapsed / self._flash_duration)

        x = fc * CELL_SIZE
        y = fr * CELL_SIZE

        # Create a semi-transparent white overlay
        flash_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        alpha = int(60 * flash_intensity)
        flash_surf.fill((255, 255, 255, alpha))
        self.screen.blit(flash_surf, (x, y))

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------

    def _draw_hud(self, state: GameState) -> None:
        """Draw the heads-up display (timer, mistakes, and hints)."""
        hud_y = GRID_SIZE + 10

        # Timer
        timer_text = self._hud_font.render(
            f"Time: {state.minutes:02d}:{state.seconds:02d}",
            True, HUD_TEXT_COLOR,
        )
        self.screen.blit(timer_text, (10, hud_y))

        # Mistakes
        mistake_text = self._hud_font.render(
            f"Mistakes: {state.mistake_count}/{state.max_mistakes}",
            True, INVALID if state.mistake_count >= state.max_mistakes - 1 else HUD_TEXT_COLOR,
        )
        self.screen.blit(mistake_text, (10, hud_y + HUD_FONT_SIZE + 5))

        # Hints
        hints_text = self._hud_font.render(
            f"Hints: {state.hints_used}/{state.max_hints}",
            True, HUD_TEXT_COLOR,
        )
        self.screen.blit(hints_text, (10, hud_y + 2 * (HUD_FONT_SIZE + 5)))

    def _draw_hint_message(self, state: GameState) -> None:
        """Draw a brief "Hint used!" message when a hint is applied."""
        if state.hinted_cell[0] < 0:
            return

        r, c = state.hinted_cell
        x = c * CELL_SIZE + CELL_SIZE // 2
        y = r * CELL_SIZE + CELL_SIZE // 2

        # Draw a subtle glow outline around the hinted cell
        hint_rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, HINT, hint_rect, 3)

    # ------------------------------------------------------------------
    # Overlays
    # ------------------------------------------------------------------

    def _draw_pause_overlay(self) -> None:
        """Draw the pause screen overlay."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        title = self._overlay_font.render("Paused", True, OVERLAY_TITLE_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        self.screen.blit(title, title_rect)

        hint = self._hud_font.render("Press P to resume", True, OVERLAY_TEXT_COLOR)
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

        title = self._overlay_font.render("Game Over", True, GAME_OVER_TITLE_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(title, title_rect)

        # Elapsed time
        total_seconds = int(state.elapsed_seconds)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_text = self._hud_font.render(
            f"Time: {minutes:02d}:{seconds:02d}",
            True, OVERLAY_TEXT_COLOR,
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
            True, OVERLAY_TEXT_COLOR,
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

        title = self._overlay_font.render("You Win!", True, WIN_TITLE_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(title, title_rect)

        # Elapsed time
        total_seconds = int(state.elapsed_seconds)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_text = self._hud_font.render(
            f"Time: {minutes:02d}:{seconds:02d}",
            True, OVERLAY_TEXT_COLOR,
        )
        time_rect = time_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(time_text, time_rect)

        restart = self._sub_font.render(
            "Press Space to play again",
            True, OVERLAY_TEXT_COLOR,
        )
        restart_rect = restart.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 50),
        )
        self.screen.blit(restart, restart_rect)

    def _draw_shortcuts_overlay(self) -> None:
        """Draw a keyboard shortcut reference overlay."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self._overlay_font.render("Keyboard Shortcuts", True, OVERLAY_TITLE_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 180))
        self.screen.blit(title, title_rect)

        # Build shortcut lines
        shortcuts = [
            ("← → ↑ ↓ / WASD", "Move selection"),
            ("1 – 9", "Enter number"),
            ("Backspace / Delete", "Erase cell"),
            ("N", "Toggle note/pencil mode"),
            ("Ctrl + Z", "Undo last action"),
            ("H", "Give hint"),
            ("P", "Pause game"),
            ("K", "Close this screen"),
        ]

        y_start = HEIGHT // 2 - 120
        for key_text, desc_text in shortcuts:
            # Key label
            key_surf = self._hud_font.render(key_text, True, SHORTCUT_KEY_COLOR)
            # Description
            desc_surf = self._hud_font.render(desc_text, True, SHORTCUT_DESC_COLOR)

            # Center the pair
            total_width = key_surf.get_width() + 20 + desc_surf.get_width()
            x = WIDTH // 2 - total_width // 2

            self.screen.blit(key_surf, (x, y_start))
            self.screen.blit(desc_surf, (x + key_surf.get_width() + 20, y_start))
            y_start += 40

        close_hint = self._hud_font.render("Press K to close", True, SHORTCUT_CLOSE_COLOR)
        close_rect = close_hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 160))
        self.screen.blit(close_hint, close_rect)
