Environment: Linux (vs code dev container Node 22) + Bash.

Ask the user for input if a bash command is blocked but you need it do to your work.

## Development Workflow Rules

- **One module at a time.** Write and test a single logical module before moving to the next. Do not batch-write multiple files.
- **Test after every file.** Run the relevant tests immediately after writing or modifying a file. Fix failures before proceeding.
- **Stop and wait for input** after each module is complete (tests passing, smoke test green). Do not continue to the next module without explicit user approval.
- **If a test fails, investigate and fix before writing more code.** Never accumulate broken state.