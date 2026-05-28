# Main instruction
You are an expert Python developer building a Pygame Sudoku desktop game.
This file (agent-todo.md) is your source of truth and working log.
Rules you must follow:

Before starting any work, read this file to orient yourself.
Work top-to-bottom through tasks. Do not skip ahead unless a task is ❌ Blocked.
When you begin a task, immediately update it to 🔄 In Progress in the file.
When a task is complete, update it to ✅ Done before moving on.
If you discover required sub-tasks, add them inline under the relevant section.
Never delete tasks — only update their status.
After every code change, confirm the game still runs before marking a task done.
Keep code modular: logic in src/logic/, rendering in src/ui/, constants in src/theme.py.



# Sudoku Pygame — Agent Todo List

> **Instructions for the agent**: Work through tasks top-to-bottom. When you start a task, mark it `🔄 In Progress`. When done, mark it `✅ Done`. If you discover sub-tasks or blockers, add them inline. Never remove tasks — only update their status. Keep this file committed and accurate at all times.

---

## Status Key
- `⬜ Todo` — not started
- `🔄 In Progress` — actively being worked on
- `✅ Done` — completed
- `❌ Blocked` — cannot proceed (add reason inline)

---

## 1. Project Setup
- `✅ Done` Create project directory structure (`src/`, `assets/`, `tests/`)
- `✅ Done` Create `requirements.txt` with `pygame` dependency
- `✅ Done` Create `README.md` with basic project description and run instructions
- `✅ Done` Verify Pygame installs and a blank window opens (`src/main.py` smoke test)

---

## 2. Core Sudoku Logic (no UI)
- `✅` Implement Sudoku validator — checks rows, columns, and 3×3 boxes
- `✅` Implement backtracking solver
- `✅` Implement puzzle generator — creates a full solved board, then removes cells to create a puzzle
- `✅` Add difficulty levels (easy / medium / hard) by controlling how many cells are removed
- `✅` Write unit tests for validator, solver, and generator (`tests/test_logic.py`)

---

## 3. Game State
- `✅` Define `GameState` class holding: puzzle grid, solution grid, player grid, selected cell, timer, mistake count
- `✅` Implement cell selection logic (mouse + keyboard arrow keys)
- `✅` Implement number input (1–9) and erase (Delete/Backspace)
- `✅` Implement note/pencil mode toggle — allow multiple candidate numbers per cell
- `✅` Implement win detection (player grid matches solution)
- `✅` Implement mistake detection and limit (e.g. 3 mistakes = game over)

---

## 4. Rendering (Pygame UI)
- `✅` Draw 9×9 grid with correct thick/thin line weights (box borders vs cell borders)
- `✅` Render given (locked) numbers vs player-entered numbers in distinct styles
- `✅` Highlight selected cell and its row/column/box peers
- `✅` Highlight cells containing the same number as the selected cell
- `✅` Render pencil/note numbers (small, multi-per-cell)
- `✅` Render mistake indicator (e.g. "Mistakes: 2/3")
- `✅` Render timer (counting up)
- `✅` Render invalid entries in red

---

## 5. Menus & Screens
- `✅` Main menu screen — New Game, Continue, Quit
- `✅` Difficulty selection screen
- `✅` Pause screen (P key)
- `✅` Game Over screen (too many mistakes)
- `✅` Win / congratulations screen with time taken

---

## 6. Quality of Life Features
- `✅` Undo (Ctrl+Z) — revert last player action
- `✅` Hint system — reveals one correct cell (limited uses)
  - `✅` Add `max_hints` / `hints_used` to GameState
  - `✅` Add `give_hint()` method to GameState
  - `✅` Wire up hint key (H) in main.py
  - `✅` Render hint count in HUD
  - `✅` Visually highlight the hinted cell (yellow border)
  - `✅` Write tests for hint system
- `✅` Auto-remove pencil marks when a number is confirmed in a related cell
- `✅` Keyboard shortcut reference shown on screen or via K key
  - `✅` Add `_draw_shortcuts_overlay()` to Renderer
  - `✅` Wire up overlay key (K) in main.py

---

## 7. Polish & Assets
- `✅` Choose and load a clean font (e.g. a TTF bundled in `assets/fonts/`)
- `✅` Consistent colour scheme via a central `theme.py` constants file
- `✅` Add subtle animations: cell selection highlight, number placement flash
- `✅` Window icon and title (`Sudoku`)

---

## 8. Final
- `⬜` Full playthrough test — generate puzzle, play to completion, verify win screen
- `⬜` Code cleanup, remove debug prints, add docstrings to public functions
- `⬜` Update `README.md` with final controls reference and screenshot