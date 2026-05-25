"""
VibeSudoku — Main entry point.

Launches the Pygame window and runs the game loop.
"""

import sys
import os
import pygame

# Ensure the repo root is on sys.path so ``from src.ui`` works
# when running ``python src/main.py`` from the project root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ui import display


def main() -> None:
    """Initialise Pygame and start the game loop."""
    pygame.init()
    screen = pygame.display.set_mode((display.WIDTH, display.HEIGHT))
    pygame.display.set_caption("Sudoku")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(display.BACKGROUND)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
