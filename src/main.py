"""
VibeSudoku — Main entry point.

Launches the Pygame window, generates a puzzle, and runs the
complete game loop with keyboard and mouse input.
"""

import sys
import os

import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.logic.generator import SudokuGenerator
from src.game_state import GameState
from src.ui.renderer import Renderer


def main() -> None:
    """Initialise Pygame and start the game loop."""
    pygame.init()
    screen = pygame.display.set_mode((540, 640))
    pygame.display.set_caption("Sudoku")
    clock = pygame.time.Clock()

    # Generate a new puzzle
    generator = SudokuGenerator()
    puzzle, solution = generator.generate("medium")
    state = GameState(puzzle=puzzle, solution=solution)
    renderer = Renderer(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if state.is_over:
                    if event.key == pygame.K_SPACE:
                        # Restart with new puzzle
                        puzzle, solution = generator.generate("medium")
                        state = GameState(puzzle=puzzle, solution=solution)
                        continue

                # Navigation
                if event.key in (pygame.K_UP, pygame.K_w):
                    state.select_next("up")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    state.select_next("down")
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    state.select_next("left")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    state.select_next("right")

                # Number input (1-9)
                elif event.unicode.isdigit() and 1 <= int(event.unicode) <= 9:
                    state.enter_number(int(event.unicode))

                # Erase
                elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                    state.erase()

                # Note mode toggle
                elif event.key == pygame.K_n:
                    state.toggle_note_mode()

                # Undo
                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    state.undo()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mx, my = event.pos
                    col = mx // 60
                    row = my // 60
                    if 0 <= row < 9 and 0 <= col < 9:
                        state.select_cell(row, col)

        # Update timer
        state.tick()

        # Render
        renderer.render(state)
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
