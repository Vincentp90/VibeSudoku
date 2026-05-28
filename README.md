# VibeSudoku

A project to learn agentic coding with pi

Dev stack:
- VS Code dev containers
- pi (pi.dev)
- Local running model
    - llama-server
    - Qwen3.6

Topic:  
Make a sudoku game with python

Generated README.md below here:

----

A clean, modern Sudoku game built with Python and Pygame.

## Features

- Play Sudoku with difficulty levels (easy, medium, hard)
- Pencil / note mode for candidate numbers
- Undo, hints, and mistake tracking
- Keyboard and mouse controls
- Animations: selection pulse, number placement flash
- Full game states: menu, difficulty, gameplay, pause, game over, win

## Requirements

- Python 3.10+
- Pygame 2.0+

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python3 src/main.py
```

## Controls

| Key / Action          | Effect                          |
|-----------------------|---------------------------------|
| Mouse click           | Select cell                     |
| Arrow keys / WASD     | Move selection                  |
| 1–9                   | Enter number                    |
| Backspace / Delete    | Erase cell                      |
| N                     | Toggle note/pencil mode         |
| Ctrl+Z                | Undo last action                |
| H                     | Give hint (fills one cell)      |
| P                     | Pause game                      |
| K                     | Show/hide keyboard shortcuts    |
| Esc                   | Go back / quit                  |
| Space                 | Restart (game over / win screen)|

## Project Structure

```
src/
  main.py          # Entry point
  game_state.py    # Game state management
  ui/
    renderer.py    # Pygame rendering
    input_handler.py # Keyboard/mouse event dispatch
    menu.py        # Menu screen rendering
    screens.py     # Screen state machine
    theme.py       # Visual constants (colours, fonts)
    display.py     # Window dimensions
    __init__.py
  logic/
    generator.py   # Puzzle generation
    solver.py      # Backtracking solver
    validator.py   # Board validation
    __init__.py
  __init__.py
assets/
  fonts/           # Bundled fonts
tests/
  test_logic.py    # Unit tests for core logic
  test_game_state.py
  test_renderer.py
  test_screens.py
  test_playthrough.py  # Full game playthrough tests
```

## License

MIT
