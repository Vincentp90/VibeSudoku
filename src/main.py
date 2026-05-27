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
from src.ui.theme import HINT


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

    # Menu hover state
    main_menu_hover = -1
    difficulty_hover = -1

    # Keyboard shortcut overlay toggle
    show_shortcuts = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # --- Main Menu ---
                if screen_manager.current == Screen.MAIN_MENU:
                    if event.key == pygame.K_UP:
                        main_menu_hover = (main_menu_hover - 1) % 2
                    elif event.key == pygame.K_DOWN:
                        main_menu_hover = (main_menu_hover + 1) % 2
                    elif event.key == pygame.K_RETURN:
                        if main_menu_hover == 0:
                            # New Game -> go to difficulty selection
                            screen_manager.go_to(Screen.DIFFICULTY)
                            difficulty_hover = 1  # default to medium
                        elif main_menu_hover == 1:
                            # Quit
                            running = False

                # --- Difficulty Selection ---
                elif screen_manager.current == Screen.DIFFICULTY:
                    if event.key == pygame.K_UP:
                        difficulty_hover = max(0, difficulty_hover - 1)
                    elif event.key == pygame.K_DOWN:
                        difficulty_hover = min(2, difficulty_hover + 1)
                    elif event.key == pygame.K_RETURN:
                        difficulty = DIFFICULTY_OPTIONS[difficulty_hover]
                        game_state = _generate_game(generator, difficulty)
                        screen_manager.go_to(Screen.GAME)
                    elif event.key == pygame.K_ESCAPE:
                        screen_manager.go_back()
                        main_menu_hover = -1

                # --- Gameplay ---
                elif screen_manager.current == Screen.GAME:
                    if game_state is None:
                        continue

                    # Pause toggle
                    if event.key == pygame.K_p:
                        screen_manager.go_to(Screen.PAUSED)
                        continue

                    if game_state.is_game_over:
                        if event.key == pygame.K_SPACE:
                            # Restart with same difficulty
                            game_state.reset()
                            continue

                    # Navigation
                    if event.key in (pygame.K_UP, pygame.K_w):
                        game_state.select_next("up")
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        game_state.select_next("down")
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        game_state.select_next("left")
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        game_state.select_next("right")

                    # Number input (1-9)
                    elif event.unicode.isdigit() and 1 <= int(event.unicode) <= 9:
                        game_state.enter_number(int(event.unicode))

                    # Erase
                    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        game_state.erase()

                    # Note mode toggle
                    elif event.key == pygame.K_n:
                        game_state.toggle_note_mode()

                    # Undo
                    elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        game_state.undo()

                    # Hint
                    elif event.key == pygame.K_h:
                        if game_state.give_hint():
                            show_shortcuts = False  # close overlay if open

                    # Keyboard shortcut overlay
                    elif event.key == pygame.K_k:
                        show_shortcuts = not show_shortcuts

                # --- Paused ---
                elif screen_manager.current == Screen.PAUSED:
                    if event.key == pygame.K_p:
                        screen_manager.go_back()

                # --- Game Over ---
                elif screen_manager.current == Screen.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        # New game with same difficulty
                        game_state.reset()
                        screen_manager.go_to(Screen.GAME)
                    elif event.key == pygame.K_ESCAPE:
                        game_state = None
                        screen_manager.go_to(Screen.MAIN_MENU)
                        main_menu_hover = -1

                # --- Win ---
                elif screen_manager.current == Screen.WIN:
                    if event.key == pygame.K_SPACE:
                        # New game with same difficulty
                        game_state.reset()
                        screen_manager.go_to(Screen.GAME)
                    elif event.key == pygame.K_ESCAPE:
                        game_state = None
                        screen_manager.go_to(Screen.MAIN_MENU)
                        main_menu_hover = -1

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # --- Main Menu mouse clicks ---
                if screen_manager.current == Screen.MAIN_MENU:
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
                                screen_manager.go_to(Screen.DIFFICULTY)
                                difficulty_hover = 1
                            elif idx == 1:
                                running = False
                            break

                # --- Difficulty Selection mouse clicks ---
                elif screen_manager.current == Screen.DIFFICULTY:
                    menu_y = 640 // 2
                    for idx, _ in enumerate(DIFFICULTY_OPTIONS):
                        item_rect = pygame.Rect(
                            540 // 2 - 160,
                            menu_y + idx * 80 - 20,
                            320,
                            60,
                        )
                        if item_rect.collidepoint(mx, my):
                            difficulty = DIFFICULTY_OPTIONS[idx]
                            game_state = _generate_game(generator, difficulty)
                            screen_manager.go_to(Screen.GAME)
                            break

                # --- Gameplay mouse clicks ---
                elif screen_manager.current == Screen.GAME and game_state is not None:
                    col = mx // 60
                    row = my // 60
                    if 0 <= row < 9 and 0 <= col < 9:
                        game_state.select_cell(row, col)

        # --- Game state updates ---
        if screen_manager.current in (Screen.GAME, Screen.PAUSED) and game_state is not None:
            game_state.tick()

            # Check for game over / win transitions
            if game_state.is_won and screen_manager.current == Screen.GAME:
                screen_manager.go_to(Screen.WIN)
            elif game_state.is_game_over and screen_manager.current == Screen.GAME:
                screen_manager.go_to(Screen.GAME_OVER)

        # --- Rendering ---
        if screen_manager.current == Screen.MAIN_MENU:
            menu.draw_main_menu(main_menu_hover)
        elif screen_manager.current == Screen.DIFFICULTY:
            menu.draw_difficulty_menu(difficulty_hover)
        elif screen_manager.current in (Screen.GAME, Screen.PAUSED, Screen.GAME_OVER, Screen.WIN):
            if game_state is not None:
                renderer.render(game_state, screen_manager.current)
                if screen_manager.current == Screen.GAME and show_shortcuts:
                    renderer._draw_shortcuts_overlay()
            else:
                renderer.render(game_state, Screen.GAME)  # fallback

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
