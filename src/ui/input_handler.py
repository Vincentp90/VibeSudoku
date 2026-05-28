"""Input handling for VibeSudoku.

Extracts keyboard and mouse event processing from the monolithic game
loop into a dedicated ``InputHandler`` class with per-screen methods.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame

from src.ui.screens import Screen

if TYPE_CHECKING:
    from src.game_state import GameState
    from src.logic.generator import SudokuGenerator
    from src.ui.menu import Menu
    from src.ui.screens import ScreenManager


@dataclass
class HoverState:
    """Mutable hover/overlay state shared across screens.

    Parameters
    ----------
    main_menu_hover : int
        Index of the hovered main-menu item (-1 = none).
    difficulty_hover : int
        Index of the hovered difficulty option (0 = easy, 1 = medium, 2 = hard).
    show_shortcuts : bool
        Whether the keyboard-shortcuts overlay is visible.
    """

    main_menu_hover: int = -1
    difficulty_hover: int = 1
    show_shortcuts: bool = False


# Dispatch tables — map screen → method name
_KEY_HANDLERS: dict[Screen, str] = {
    Screen.MAIN_MENU: "_handle_main_menu_key",
    Screen.DIFFICULTY: "_handle_difficulty_key",
    Screen.GAME: "_handle_game_key",
    Screen.PAUSED: "_handle_paused_key",
    Screen.GAME_OVER: "_handle_game_over_key",
    Screen.WIN: "_handle_win_key",
}

_MOUSE_HANDLERS: dict[Screen, str] = {
    Screen.MAIN_MENU: "_handle_main_menu_mouse",
    Screen.DIFFICULTY: "_handle_difficulty_mouse",
    Screen.GAME: "_handle_game_mouse",
}


class InputHandler:
    """Dispatch keyboard and mouse events to per-screen handlers.

    Parameters
    ----------
    screen_manager : ScreenManager
        Tracks the current screen.
    game_state : GameState | None
        The active game state (may be ``None`` when not in a game).
    menu : Menu
        Menu renderer (unused by handlers but kept for future use).
    hover : HoverState
        Mutable hover/overlay booleans.
    generator : SudokuGenerator | None
        Puzzle generator, needed for difficulty selection.
    """

    def __init__(
        self,
        screen_manager: ScreenManager,
        game_state: GameState | None,
        menu: Menu,
        hover: HoverState,
        generator: SudokuGenerator | None = None,
    ) -> None:
        self.screen_manager = screen_manager
        self.game_state = game_state
        self.menu = menu
        self.hover = hover
        self.generator = generator
        self._should_quit: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle a single Pygame event.

        Parameters
        ----------
        event : pygame.event.Event
            The event to process.

        Returns
        -------
        bool
            ``True`` to continue the game loop, ``False`` to quit.
        """
        if event.type == pygame.QUIT:
            self._should_quit = True
            return False

        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
            return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse(event)
            return True

        return True

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """Dispatch KEYDOWN to the current screen's key handler."""
        handler_name = _KEY_HANDLERS.get(self.screen_manager.current)
        if handler_name is None:
            return
        handler = getattr(self, handler_name)
        handler(event)

    def _handle_mouse(self, event: pygame.event.Event) -> None:
        """Dispatch MOUSEBUTTONDOWN to the current screen's mouse handler."""
        handler_name = _MOUSE_HANDLERS.get(self.screen_manager.current)
        if handler_name is None:
            return
        handler = getattr(self, handler_name)
        handler(event)

    # ------------------------------------------------------------------
    # Main Menu
    # ------------------------------------------------------------------

    def _handle_main_menu_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_UP:
            self.hover.main_menu_hover = (self.hover.main_menu_hover - 1) % 2
        elif event.key == pygame.K_DOWN:
            self.hover.main_menu_hover = (self.hover.main_menu_hover + 1) % 2
        elif event.key == pygame.K_RETURN:
            if self.hover.main_menu_hover == 0:
                self.screen_manager.go_to(Screen.DIFFICULTY)
                self.hover.difficulty_hover = 1
            elif self.hover.main_menu_hover == 1:
                self._should_quit = True

    def _handle_main_menu_mouse(self, event: pygame.event.Event) -> None:
        mx, my = event.pos
        menu_y = 640 // 2
        for idx, _ in enumerate(["New Game", "Quit"]):
            item_rect = pygame.Rect(
                540 // 2 - 100,
                menu_y + idx * 70 - 20,
                200,
                50,
            )
            if item_rect.collidepoint(mx, my):
                if idx == 0:
                    self.screen_manager.go_to(Screen.DIFFICULTY)
                    self.hover.difficulty_hover = 1
                else:
                    self._should_quit = True
                break

    # ------------------------------------------------------------------
    # Difficulty Selection
    # ------------------------------------------------------------------

    def _handle_difficulty_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_UP:
            self.hover.difficulty_hover = max(0, self.hover.difficulty_hover - 1)
        elif event.key == pygame.K_DOWN:
            self.hover.difficulty_hover = min(2, self.hover.difficulty_hover + 1)
        elif event.key == pygame.K_RETURN:
            difficulty = self._get_difficulty_option()
            if difficulty is not None and self.generator is not None:
                puzzle, solution = self.generator.generate(difficulty)
                from src.game_state import GameState
                self.game_state = GameState(puzzle=puzzle, solution=solution)
                self.screen_manager.go_to(Screen.GAME)
        elif event.key == pygame.K_ESCAPE:
            self.screen_manager.go_back()
            self.hover.main_menu_hover = -1

    def _handle_difficulty_mouse(self, event: pygame.event.Event) -> None:
        mx, my = event.pos
        menu_y = 640 // 2
        for idx, _ in enumerate(["easy", "medium", "hard"]):
            item_rect = pygame.Rect(
                540 // 2 - 160,
                menu_y + idx * 80 - 20,
                320,
                60,
            )
            if item_rect.collidepoint(mx, my):
                difficulty = ["easy", "medium", "hard"][idx]
                if self.generator is not None:
                    puzzle, solution = self.generator.generate(difficulty)
                    from src.game_state import GameState
                    self.game_state = GameState(puzzle=puzzle, solution=solution)
                self.screen_manager.go_to(Screen.GAME)
                break

    def _get_difficulty_option(self) -> str | None:
        """Return the difficulty string at the current hover index."""
        options = ["easy", "medium", "hard"]
        idx = self.hover.difficulty_hover
        if 0 <= idx < len(options):
            return options[idx]
        return None

    # ------------------------------------------------------------------
    # Gameplay
    # ------------------------------------------------------------------

    def _handle_game_key(self, event: pygame.event.Event) -> None:
        if self.game_state is None:
            return

        # Pause
        if event.key == pygame.K_p:
            self.screen_manager.go_to(Screen.PAUSED)
            return

        # Game over restart
        if self.game_state.is_game_over and event.key == pygame.K_SPACE:
            self.game_state.reset()
            return

        # Navigation
        if event.key in (pygame.K_UP, pygame.K_w):
            self.game_state.select_next("up")
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.game_state.select_next("down")
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self.game_state.select_next("left")
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.game_state.select_next("right")

        # Number input
        elif event.unicode.isdigit() and 1 <= int(event.unicode) <= 9:
            self.game_state.enter_number(int(event.unicode))

        # Erase
        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            self.game_state.erase()

        # Note mode
        elif event.key == pygame.K_n:
            self.game_state.toggle_note_mode()

        # Undo
        elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.game_state.undo()

        # Hint
        elif event.key == pygame.K_h:
            if self.game_state.give_hint():
                self.hover.show_shortcuts = False

        # Shortcuts overlay
        elif event.key == pygame.K_k:
            self.hover.show_shortcuts = not self.hover.show_shortcuts

    def _handle_game_mouse(self, event: pygame.event.Event) -> None:
        if self.game_state is None:
            return
        mx, my = event.pos
        col = mx // 60
        row = my // 60
        if 0 <= row < 9 and 0 <= col < 9:
            self.game_state.select_cell(row, col)

    # ------------------------------------------------------------------
    # Paused
    # ------------------------------------------------------------------

    def _handle_paused_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_p:
            self.screen_manager.go_back()

    # ------------------------------------------------------------------
    # Game Over
    # ------------------------------------------------------------------

    def _handle_game_over_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_SPACE:
            if self.game_state is not None:
                self.game_state.reset()
            self.screen_manager.go_to(Screen.GAME)
        elif event.key == pygame.K_ESCAPE:
            self.game_state = None
            self.screen_manager.go_to(Screen.MAIN_MENU)
            self.hover.main_menu_hover = -1

    # ------------------------------------------------------------------
    # Win
    # ------------------------------------------------------------------

    def _handle_win_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_SPACE:
            if self.game_state is not None:
                self.game_state.reset()
            self.screen_manager.go_to(Screen.GAME)
        elif event.key == pygame.K_ESCAPE:
            self.game_state = None
            self.screen_manager.go_to(Screen.MAIN_MENU)
            self.hover.main_menu_hover = -1
