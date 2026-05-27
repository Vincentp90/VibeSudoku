Environment: Linux (vs code dev container Node 22) + Bash.

Ask user for input if you are not sure how to proceed.

## Scripts

- `scripts/smoke_test.py` — Opens blank pygame window for ~2s; catches import/runtime errors. Run before debugging window/render issues to verify pygame works.

## Development Workflow Rules

- **One module at a time** — write and test a single logical module before moving on; do not batch-write multiple files.
- **Test every file** — run tests after writing or modifying; fix failures before proceeding.
- **Pause for approval** — stop after each module completes; wait for user input before continuing.
- **Fix before writing** — if a test fails, resolve it first; never accumulate broken state.