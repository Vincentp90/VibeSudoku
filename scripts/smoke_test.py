#!/usr/bin/env python3
"""Smoke test for VibeSudoku.

Initialises Pygame, opens a blank window for ~2 seconds, then quits.
Exits with code 0 on success, 1 on failure.
"""

from __future__ import annotations

import sys
import time
import pygame


def main() -> int:
    """Run the smoke test."""
    try:
        pygame.init()
    except pygame.error as exc:
        print(f"[FAIL] pygame.init() failed: {exc}", file=sys.stderr)
        return 1

    screen = None
    try:
        screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("VibeSudoku Smoke Test")
    except pygame.error as exc:
        print(f"[FAIL] pygame.display.set_mode() failed: {exc}", file=sys.stderr)
        pygame.quit()
        return 1

    clock = pygame.time.Clock()
    deadline = time.monotonic() + 2.0  # 2 seconds

    while time.monotonic() < deadline:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # User closed the window early — that's fine.
                pass

        screen.fill((240, 240, 240))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("[OK] Smoke test passed — window opened and rendered for 2 seconds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
