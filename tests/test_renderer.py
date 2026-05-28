"""Unit tests for :class:`~src.ui.renderer.Renderer`.

These tests exercise the renderer's public and private methods to ensure
that all font attributes are initialized and every draw method can execute
without raising ``AttributeError`` or ``pygame.error``.
"""

from __future__ import annotations

import unittest

import pygame

from src.game_state import GameState
from src.ui.renderer import Renderer
from src.ui.screens import Screen
from src.ui.theme import CELL_SIZE, SELECTED


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _make_game_state(**kwargs) -> GameState:
    """Create a minimal GameState with sensible defaults.

    Parameters
    ----------
    **kwargs : dict
        Optional overrides for GameState fields (e.g. ``is_game_over=True``).

    Returns
    -------
    GameState
    """
    puzzle = [
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
    solution = [
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
    gs = GameState(puzzle=puzzle, solution=solution, **kwargs)
    return gs


def _make_renderer() -> Renderer:
    """Create a Renderer backed by an off-screen surface.

    Returns
    -------
    Renderer
    """
    surface = pygame.Surface((540, 640))
    return Renderer(surface)


# ------------------------------------------------------------------
# Renderer initialisation
# ------------------------------------------------------------------

class TestRendererInit(unittest.TestCase):
    """Ensure the Renderer creates all required font objects."""

    def test_font_attributes_exist(self):
        """All internal font attributes must be initialized."""
        r = _make_renderer()
        self.assertIsNotNone(r._number_font)
        self.assertIsNotNone(r._note_font)
        self.assertIsNotNone(r._hud_font)
        self.assertIsNotNone(r._overlay_font)
        self.assertIsNotNone(r._sub_font)


# ------------------------------------------------------------------
# Grid drawing
# ------------------------------------------------------------------

class TestGridDrawing(unittest.TestCase):
    """Test grid-related rendering methods."""

    def setUp(self) -> None:
        self.renderer = _make_renderer()
        self.state = _make_game_state()

    def test_draw_grid(self):
        """_draw_grid should complete without error."""
        self.renderer._draw_grid(self.state)

    def test_draw_grid_selection_highlight(self):
        """Selected cell should be drawn with the SELECTED colour."""
        self.state.selected_row = 0
        self.state.selected_col = 0
        self.renderer._draw_grid(self.state)
        cx, cy = CELL_SIZE // 2, CELL_SIZE // 2
        pixel = self.renderer.screen.get_at((cx, cy))
        self.assertEqual(
            (pixel.r, pixel.g, pixel.b),
            SELECTED,
            "Selection highlight colour mismatch",
        )

    def test_draw_cell_backgrounds(self):
        """_draw_cell_backgrounds should complete without error."""
        self.renderer._draw_cell_backgrounds(self.state)

    def test_draw_numbers(self):
        """_draw_numbers should complete without error."""
        self.renderer._draw_numbers(self.state)

    def test_draw_numbers_invalid_color(self):
        """Wrong numbers should be drawn in INVALID colour."""
        from src.ui.theme import INVALID
        # Place a wrong number in the player grid
        self.state.player_grid[0][2] = 9  # wrong — should be 4
        self.renderer._draw_numbers(self.state)
        cx, cy = 2 * CELL_SIZE + CELL_SIZE // 2, 0 * CELL_SIZE + CELL_SIZE // 2
        pixel = self.renderer.screen.get_at((cx, cy))
        # The INVALID colour should not be white (background)
        self.assertNotEqual(
            (pixel.r, pixel.g, pixel.b),
            (255, 255, 255),
            "Wrong number was not rendered",
        )

    def test_draw_notes(self):
        """_draw_notes should complete without error."""
        self.state.notes[0][0].add(1)
        self.state.notes[0][0].add(2)
        self.renderer._draw_notes(self.state)

    def test_draw_lines(self):
        """_draw_lines should complete without error."""
        self.renderer._draw_lines()


# ------------------------------------------------------------------
# HUD
# ------------------------------------------------------------------

class TestHUDDrawing(unittest.TestCase):
    """Test HUD rendering methods."""

    def setUp(self) -> None:
        self.renderer = _make_renderer()
        self.state = _make_game_state()

    def test_draw_hud(self):
        """_draw_hud should complete without error."""
        self.renderer._draw_hud(self.state)


# ------------------------------------------------------------------
# Animations
# ------------------------------------------------------------------

class TestAnimationDrawing(unittest.TestCase):
    """Test animation rendering methods."""

    def setUp(self) -> None:
        self.renderer = _make_renderer()
        self.state = _make_game_state()

    def test_draw_animations(self):
        """_draw_animations should complete without error."""
        self.renderer._draw_animations(self.state)

    def test_draw_selection_pulse(self):
        """_draw_selection_pulse should complete without error."""
        self.state.selected_row = 0
        self.state.selected_col = 0
        self.renderer._draw_selection_pulse(self.state)

    def test_draw_selection_pulse_no_selection(self):
        """_draw_selection_pulse should be a no-op when no cell is selected."""
        self.state.selected_row = -1
        self.state.selected_col = -1
        self.renderer._draw_selection_pulse(self.state)

    def test_draw_number_flash(self):
        """_draw_number_flash should complete without error."""
        self.state.flash_cell = (0, 0)
        self.state._flash_time = 0.0
        self.renderer._draw_number_flash(self.state)

    def test_draw_number_flash_expired(self):
        """_draw_number_flash should be a no-op when flash is expired."""
        self.state.flash_cell = (0, 0)
        self.state._flash_time = 0.0  # old time
        # Advance time past the flash duration
        import time
        self.state._flash_time = time.time() - 1.0  # 1 second ago
        self.renderer._draw_number_flash(self.state)


# ------------------------------------------------------------------
# Overlays — these are where the _sub_font bug lived
# ------------------------------------------------------------------

class TestOverlayDrawing(unittest.TestCase):
    """Test overlay rendering methods.

    These tests specifically ensure that all overlay methods can execute
    without raising ``AttributeError`` — the regression test for the
    missing ``_sub_font`` initialisation.
    """

    def setUp(self) -> None:
        self.renderer = _make_renderer()
        self.state = _make_game_state()

    def test_draw_pause_overlay(self):
        """_draw_pause_overlay should complete without error."""
        self.renderer._draw_pause_overlay()

    def test_draw_game_over_overlay(self):
        """_draw_game_over_overlay must use all font attributes.

        This test is the regression for the missing ``_sub_font`` bug:
        before the fix, calling this method raised
        ``AttributeError: 'Renderer' object has no attribute '_sub_font'``.
        """
        self.state.elapsed_seconds = 123.0
        self.state.mistake_count = 2
        self.renderer._draw_game_over_overlay(self.state)

    def test_draw_win_overlay(self):
        """_draw_win_overlay must use all font attributes.

        Same regression test as ``test_draw_game_over_overlay`` — the
        win overlay also uses ``_sub_font`` for the "Press Space" text.
        """
        self.state.elapsed_seconds = 45.0
        self.renderer._draw_win_overlay(self.state)

    def test_draw_shortcuts_overlay(self):
        """_draw_shortcuts_overlay should complete without error."""
        self.renderer._draw_shortcuts_overlay()


# ------------------------------------------------------------------
# Full render cycle
# ------------------------------------------------------------------

class TestFullRender(unittest.TestCase):
    """Test the public ``render`` method across all screen states."""

    def setUp(self) -> None:
        self.renderer = _make_renderer()
        self.state = _make_game_state()

    def test_render_game(self):
        """Rendering the GAME screen should complete without error."""
        self.state.selected_row = 0
        self.state.selected_col = 0
        self.renderer.render(self.state, Screen.GAME)

    def test_render_paused(self):
        """Rendering the PAUSED screen should complete without error."""
        self.renderer.render(self.state, Screen.PAUSED)

    def test_render_game_over(self):
        """Rendering the GAME_OVER screen should complete without error."""
        self.state.elapsed_seconds = 200.0
        self.state.mistake_count = 3
        self.renderer.render(self.state, Screen.GAME_OVER)

    def test_render_win(self):
        """Rendering the WIN screen should complete without error."""
        self.state.elapsed_seconds = 60.0
        self.renderer.render(self.state, Screen.WIN)

    def test_render_game_with_won_state(self):
        """Rendering GAME with is_won should show the win overlay."""
        self.state.is_won = True
        self.state.elapsed_seconds = 90.0
        self.renderer.render(self.state, Screen.GAME)

    def test_render_game_with_game_over_state(self):
        """Rendering GAME with is_game_over should show the game-over overlay."""
        self.state.is_game_over = True
        self.state.elapsed_seconds = 300.0
        self.state.mistake_count = 3
        self.renderer.render(self.state, Screen.GAME)

    def test_render_draws_to_surface(self):
        """render() should actually draw pixels to the surface."""
        self.state.selected_row = 0
        self.state.selected_col = 0
        self.renderer.render(self.state, Screen.GAME)
        # Check a few known cell positions have non-background pixels.
        # Cell (0, 0) has the number 5 which should be drawn in a non-white colour.
        cx, cy = 30, 30  # center of cell (0, 0)
        pixel = self.renderer.screen.get_at((cx, cy))
        self.assertNotEqual(
            (pixel.r, pixel.g, pixel.b),
            (255, 255, 255),
            "Cell (0, 0) is still white — the number 5 was not rendered.",
        )


if __name__ == "__main__":
    unittest.main()
