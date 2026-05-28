"""
VibeSudoku — Main entry point.

Launches the Pygame window and runs the complete game loop with
keyboard and mouse input, managing multiple screens:
main menu, difficulty selection, gameplay, pause, game over, and win.
"""

import sys
import os

import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.logic.generator import SudokuGenerator
from src.game_state import GameState
from src.ui.renderer import Renderer
from src.ui.screens import Screen, ScreenManager
from src.ui.menu import Menu
from src.ui.input_handler import HoverState, InputHandler


# Difficulty selection constants
DIFFICULTY_OPTIONS = ["easy", "medium", "hard"]


def _generate_game(generator: SudokuGenerator, difficulty: str) -> GameState:
    """Generate a new game with the given difficulty.

    Parameters
    ----------
    generator : SudokuGenerator
        The puzzle generator instance.
    difficulty : str
        One of ``"easy"``, ``"medium"``, or ``"hard"``.

    Returns
    -------
    GameState
        A fresh game state for the generated puzzle.
    """
    puzzle, solution = generator.generate(difficulty)
    return GameState(puzzle=puzzle, solution=solution)


def _update_game_state(
    screen_manager: ScreenManager,
    game_state: GameState | None,
) -> None:
    """Update game state (timer, win/over transitions).

    Parameters
    ----------
    screen_manager : ScreenManager
        The current screen manager.
    game_state : GameState | None
        The active game state, or ``None``.
    """
    if screen_manager.current in (Screen.GAME, Screen.PAUSED) and game_state is not None:
        game_state.tick()

        # Check for game over / win transitions
        if game_state.is_won and screen_manager.current == Screen.GAME:
            screen_manager.go_to(Screen.WIN)
        elif game_state.is_game_over and screen_manager.current == Screen.GAME:
            screen_manager.go_to(Screen.GAME_OVER)


def _render(
    screen_manager: ScreenManager,
    game_state: GameState | None,
    renderer: Renderer,
    menu: Menu,
    hover: HoverState,
) -> None:
    """Render the current screen.

    Parameters
    ----------
    screen_manager : ScreenManager
        The current screen manager.
    game_state : GameState | None
        The active game state, or ``None``.
    renderer : Renderer
        The game renderer.
    menu : Menu
        The menu renderer.
    hover : HoverState
        The shared hover state.
    """
    if screen_manager.current == Screen.MAIN_MENU:
        menu.draw_main_menu(hover.main_menu_hover)
    elif screen_manager.current == Screen.DIFFICULTY:
        menu.draw_difficulty_menu(hover.difficulty_hover)
    elif screen_manager.current in (Screen.GAME, Screen.PAUSED, Screen.GAME_OVER, Screen.WIN):
        if game_state is not None:
            renderer.render(game_state, screen_manager.current)
            if screen_manager.current == Screen.GAME and hover.show_shortcuts:
                renderer._draw_shortcuts_overlay()
        else:
            renderer.render(game_state, Screen.GAME)  # fallback


def main() -> None:
    """Initialise Pygame and start the game loop."""
    pygame.init()
    screen = pygame.display.set_mode((540, 640))
    pygame.display.set_caption("Sudoku")
    clock = pygame.time.Clock()

    # Shared game objects
    generator = SudokuGenerator()
    renderer = Renderer(screen)
    menu = Menu(screen)

    # Screen management
    screen_manager = ScreenManager()

    # Current game state (None until a game is started)
    game_state: GameState | None = None

    # Hover and overlay state
    hover = HoverState()

    # Input handling
    input_handler = InputHandler(screen_manager, game_state, menu, hover, generator)

    running = True
    while running:
        for event in pygame.event.get():
            running = input_handler.handle_event(event)
            if not running:
                break

        # Game state updates
        _update_game_state(screen_manager, game_state)

        # Rendering
        _render(screen_manager, game_state, renderer, menu, hover)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
