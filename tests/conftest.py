"""Shared pytest fixtures for the Sudoku test suite."""

from __future__ import annotations

import pygame
import pytest


@pytest.fixture(autouse=True, scope="session")
def init_pygame() -> None:
    """Initialise pygame once for the entire test session.

    Pygame requires ``pygame.init()`` before using any subsystem
    (fonts, display, etc.).  Using ``scope='session'`` ensures the
    initialisation happens exactly once, avoiding repeated calls.
    """
    pygame.init()
    # Clean up at the end of the session
    yield
    pygame.quit()
