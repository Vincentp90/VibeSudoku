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

## Requirements

- Python 3.10+
- Pygame 2.0+

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python src/main.py
```

## Controls

| Key / Action          | Effect                       |
|-----------------------|------------------------------|
| Mouse click           | Select cell                  |
| Arrow keys            | Move selection               |
| 1–9                   | Enter number                 |
| Delete / Backspace    | Erase cell                   |
| N                     | Toggle pencil mode           |
| P                     | Pause game                   |
| Ctrl+Z                | Undo                         |
| H                     | Show keyboard shortcuts      |

## Project Structure

```
src/
  main.py          # Entry point
  ui/              # Rendering and display
  logic/           # Sudoku solver, validator, generator
  theme.py         # Colour and font constants
assets/
  fonts/           # Bundled fonts
  images/          # Icons and background art
tests/
  test_logic.py    # Unit tests for core logic
```

## License

MIT
