"""Tests for screen management (menus & screens)."""

import pytest

from src.ui.screens import Screen, ScreenManager


class TestScreenEnum:
    """Test the Screen enum values."""

    def test_main_menu_exists(self):
        assert Screen.MAIN_MENU.value == "main_menu"

    def test_difficulty_exists(self):
        assert Screen.DIFFICULTY.value == "difficulty"

    def test_game_exists(self):
        assert Screen.GAME.value == "game"

    def test_paused_exists(self):
        assert Screen.PAUSED.value == "paused"

    def test_game_over_exists(self):
        assert Screen.GAME_OVER.value == "game_over"

    def test_win_exists(self):
        assert Screen.WIN.value == "win"


class TestScreenManager:
    """Test the ScreenManager state machine."""

    def test_initial_state(self):
        sm = ScreenManager()
        assert sm.current == Screen.MAIN_MENU
        assert sm.previous is None

    def test_go_to_changes_screen(self):
        sm = ScreenManager()
        sm.go_to(Screen.GAME)
        assert sm.current == Screen.GAME

    def test_go_to_remembers_previous(self):
        sm = ScreenManager()
        sm.go_to(Screen.DIFFICULTY)
        assert sm.previous == Screen.MAIN_MENU

    def test_go_back_restores_previous(self):
        sm = ScreenManager()
        sm.go_to(Screen.PAUSED)
        sm.go_back()
        assert sm.current == Screen.MAIN_MENU
        assert sm.previous is None

    def test_go_back_no_previous(self):
        sm = ScreenManager()
        result = sm.go_back()
        assert result is False
        assert sm.current == Screen.MAIN_MENU

    def test_multiple_transitions(self):
        sm = ScreenManager()
        sm.go_to(Screen.DIFFICULTY)
        sm.go_to(Screen.GAME)
        sm.go_back()
        assert sm.current == Screen.DIFFICULTY
        # previous was cleared by go_back, so another go_back does nothing
        sm.go_back()
        assert sm.current == Screen.DIFFICULTY

    def test_is_game_active(self):
        sm = ScreenManager()
        assert not sm.is_game_active
        sm.go_to(Screen.GAME)
        assert sm.is_game_active
        sm.go_to(Screen.PAUSED)
        assert sm.is_game_active

    def test_is_game_active_false_for_menu(self):
        sm = ScreenManager()
        assert not sm.is_game_active
        sm.go_to(Screen.MAIN_MENU)
        assert not sm.is_game_active

    def test_is_game_over(self):
        sm = ScreenManager()
        assert not sm.is_game_over
        sm.go_to(Screen.GAME_OVER)
        assert sm.is_game_over
        sm.go_to(Screen.WIN)
        assert sm.is_game_over
        sm.go_to(Screen.GAME)
        assert not sm.is_game_over

    def test_restart_from_game_over(self):
        """Simulate: game -> game_over -> back to game."""
        sm = ScreenManager()
        sm.go_to(Screen.GAME)
        sm.go_to(Screen.GAME_OVER)
        sm.go_to(Screen.GAME)
        assert sm.current == Screen.GAME
        assert sm.previous == Screen.GAME_OVER

    def test_quit_from_menu(self):
        """Simulate: main_menu -> quit (no go_back needed)."""
        sm = ScreenManager()
        sm.go_to(Screen.MAIN_MENU)
        assert sm.current == Screen.MAIN_MENU


class TestScreenTransitions:
    """Test realistic screen transition flows."""

    def test_full_game_flow(self):
        """main_menu -> difficulty -> game -> paused -> game -> win -> game."""
        sm = ScreenManager()
        assert sm.current == Screen.MAIN_MENU

        # Start new game
        sm.go_to(Screen.DIFFICULTY)
        sm.go_to(Screen.GAME)
        assert sm.current == Screen.GAME

        # Pause
        sm.go_to(Screen.PAUSED)
        assert sm.current == Screen.PAUSED

        # Resume
        sm.go_back()
        assert sm.current == Screen.GAME

        # Win
        sm.go_to(Screen.WIN)
        assert sm.current == Screen.WIN

        # Play again
        sm.go_to(Screen.GAME)
        assert sm.current == Screen.GAME

    def test_game_over_flow(self):
        """main_menu -> difficulty -> game -> game_over -> game."""
        sm = ScreenManager()
        sm.go_to(Screen.DIFFICULTY)
        sm.go_to(Screen.GAME)
        sm.go_to(Screen.GAME_OVER)
        assert sm.current == Screen.GAME_OVER

        # Restart
        sm.go_to(Screen.GAME)
        assert sm.current == Screen.GAME

    def test_escape_from_game_over_to_menu(self):
        """Escape from game over returns to main menu."""
        sm = ScreenManager()
        sm.go_to(Screen.DIFFICULTY)
        sm.go_to(Screen.GAME)
        sm.go_to(Screen.GAME_OVER)
        sm.go_to(Screen.MAIN_MENU)
        assert sm.current == Screen.MAIN_MENU

    def test_escape_from_win_to_menu(self):
        """Escape from win returns to main menu."""
        sm = ScreenManager()
        sm.go_to(Screen.DIFFICULTY)
        sm.go_to(Screen.GAME)
        sm.go_to(Screen.WIN)
        sm.go_to(Screen.MAIN_MENU)
        assert sm.current == Screen.MAIN_MENU
