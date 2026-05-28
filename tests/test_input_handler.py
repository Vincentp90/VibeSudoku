"""Tests for InputHandler state management.

Verifies that the InputHandler properly creates and updates
its game_state attribute when the player selects a difficulty
or resets a game — ensuring the main loop can always read
the current game state from the handler.
"""

import pygame
import pytest

from src.logic.generator import SudokuGenerator
from src.game_state import GameState
from src.ui.screens import Screen, ScreenManager
from src.ui.input_handler import InputHandler, HoverState


@pytest.fixture
def generator():
    """Return a seeded generator for reproducibility."""
    return SudokuGenerator(seed=42)


@pytest.fixture
def handler(generator):
    """Return an InputHandler with a fresh screen manager and hover state."""
    screen_manager = ScreenManager()
    game_state = None  # No game yet — main loop starts with None
    hover = HoverState()
    menu = None  # Not needed for these tests
    return InputHandler(screen_manager, game_state, menu, hover, generator)


def _make_key_event(key):
    """Create a mock KEYDOWN event with the given key code."""
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def _make_mouse_event(pos):
    """Create a mock MOUSEBUTTONDOWN event with the given position."""
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)


class TestDifficultySelectionCreatesGameState:
    """Verify that selecting a difficulty creates a GameState."""

    def test_key_selection_easy(self, handler):
        """Pressing Enter on 'easy' should create a GameState."""
        handler.hover.difficulty_hover = 0  # easy
        handler._handle_difficulty_key(_make_key_event(pygame.K_RETURN))
        assert handler.game_state is not None
        assert isinstance(handler.game_state, GameState)
        assert handler.screen_manager.current == Screen.GAME

    def test_key_selection_medium(self, handler):
        """Pressing Enter on 'medium' should create a GameState."""
        handler.hover.difficulty_hover = 1  # medium
        handler._handle_difficulty_key(_make_key_event(pygame.K_RETURN))
        assert handler.game_state is not None
        assert isinstance(handler.game_state, GameState)
        assert handler.screen_manager.current == Screen.GAME

    def test_key_selection_hard(self, handler):
        """Pressing Enter on 'hard' should create a GameState."""
        handler.hover.difficulty_hover = 2  # hard
        handler._handle_difficulty_key(_make_key_event(pygame.K_RETURN))
        assert handler.game_state is not None
        assert isinstance(handler.game_state, GameState)
        assert handler.screen_manager.current == Screen.GAME

    def test_mouse_selection_creates_game_state(self, handler):
        """Clicking a difficulty button should create a GameState."""
        event = _make_mouse_event((270, 340))
        handler._handle_difficulty_mouse(event)
        assert handler.game_state is not None
        assert isinstance(handler.game_state, GameState)
        assert handler.screen_manager.current == Screen.GAME


class TestGameStateSyncAfterReset:
    """Verify that game-state resets are reflected in the handler."""

    def test_game_over_restart_sets_game_state(self, handler):
        """After game over + space, the handler should have a reset game state."""
        # First, create a game
        handler.hover.difficulty_hover = 0
        handler._handle_difficulty_key(_make_key_event(pygame.K_RETURN))
        assert handler.game_state is not None
        initial = handler.game_state

        # Simulate game over
        handler.game_state.mistake_count = handler.game_state.max_mistakes
        handler.game_state.tick()  # triggers is_game_over

        # Press space to restart
        handler._handle_game_over_key(_make_key_event(pygame.K_SPACE))

        # The game state should have been reset (not None, cleared grid)
        assert handler.game_state is not None
        assert handler.game_state is initial  # same instance, reset in place
        assert handler.game_state.mistake_count == 0
        assert handler.screen_manager.current == Screen.GAME

    def test_win_restart_sets_game_state(self, handler):
        """After win + space, the handler should have a reset game state."""
        # Create a game and win it
        handler.hover.difficulty_hover = 0
        handler._handle_difficulty_key(_make_key_event(pygame.K_RETURN))
        assert handler.game_state is not None

        # Simulate win
        handler.game_state.player_grid = [row[:] for row in handler.game_state.solution]
        handler.game_state.tick()  # triggers is_won

        # Press space to restart
        handler._handle_win_key(_make_key_event(pygame.K_SPACE))

        # The game state should have been reset
        assert handler.game_state is not None
        assert handler.game_state.mistake_count == 0
        assert handler.screen_manager.current == Screen.GAME


class TestGameStateSyncFromMainLoop:
    """Simulate the main loop's sync pattern.

    These tests verify that the main loop's `game_state =
    input_handler.game_state` pattern correctly picks up state
    changes made by the handler — this is the exact fix that
    resolved the AttributeError when selecting a difficulty.
    """

    def test_main_loop_picks_up_difficulty_selection(self, handler):
        """The main loop should see the GameState after difficulty selection."""
        # Simulate: main loop starts with game_state = None
        game_state = None

        # Player selects difficulty
        handler.hover.difficulty_hover = 1  # medium
        handler._handle_difficulty_key(_make_key_event(pygame.K_RETURN))

        # Main loop sync (the fix)
        game_state = handler.game_state

        # Now game_state should be a valid GameState
        assert game_state is not None
        assert isinstance(game_state, GameState)
        assert handler.screen_manager.current == Screen.GAME

    def test_main_loop_picks_up_mouse_selection(self, handler):
        """The main loop should see the GameState after mouse click."""
        game_state = None

        # Player clicks a difficulty
        event = _make_mouse_event((270, 340))
        handler._handle_difficulty_mouse(event)

        # Main loop sync
        game_state = handler.game_state

        assert game_state is not None
        assert isinstance(game_state, GameState)

    def test_main_loop_sees_reset_state(self, handler):
        """The main loop should see the reset GameState after game over."""
        game_state = None

        # Start a game
        handler.hover.difficulty_hover = 0
        handler._handle_difficulty_key(_make_key_event(pygame.K_RETURN))
        game_state = handler.game_state
        assert game_state is not None

        # Simulate game over
        game_state.mistake_count = game_state.max_mistakes
        game_state.tick()

        # Player presses space to restart
        handler._handle_game_over_key(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        )

        # Main loop sync picks up the reset state
        game_state = handler.game_state

        assert game_state is not None
        assert game_state.mistake_count == 0
        assert game_state.is_game_over is False
