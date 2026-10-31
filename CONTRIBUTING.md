# Contributing to Forecast error analysis

Thanks for helping out! This guide covers setup, workflow, and conventions.

## Setup

```bash
make install
```

This runs `uv sync --all-groups` and installs the pre-commit hooks. You never
need to activate a virtualenv: prefix commands with `uv run`.

Prerequisites (uv, Git ≥ 2.31, make) for macOS, Linux and Windows are listed in the
[README](README.md#requirements). The project is tested in CI on all three OSes, so
keep scripts portable: use `pathlib`, not hard-coded `/` or `\` separators, and add new
`make` targets as `uv run ...` commands, not shell utilities.

## Workflow

1. Create a branch from `main`: `git switch -c feat/short-description`
2. Make your change **with tests**.
3. Run `make format && make check` until it's green.
4. Commit using [Conventional Commits](https://www.conventionalcommits.org):
   - `feat: add X`, `fix: handle Y`, `docs: ...`, `refactor: ...`, `test: ...`, `chore: ...`
5. Open a PR. Fill in the template and link the issue (`Closes #123`).

### Branch names

`feat/...`, `fix/...`, `docs/...`, `chore/...`, `refactor/...`

## Code standards

- **Formatting & lint:** Ruff (configured in `pyproject.toml`). Don't fight it.
- **Types:** mypy `strict`. Every public function has full type hints.
- **Tests:** pytest, under `tests/`, mirroring `src/` layout. Coverage must stay ≥ 80%.
- **Dependencies:** only via `uv add`. Never edit `uv.lock` by hand and never use `pip install`.

The detailed rules live in [`.claude/rules/`](.claude/rules/). They are written for
humans *and* Claude.

## Working with Claude Code

The `.claude/` folder is part of the codebase. Review changes to it like code.

| Want to...                                  | Put it in                                  |
| ------------------------------------------- | ------------------------------------------ |
| Change what Claude knows about the project  | `CLAUDE.md`                                |
| Add a convention for one area / file type   | `.claude/rules/<topic>.md` (with `paths:`) |
| Add a reusable prompt (`/name`)             | `.claude/commands/<name>.md`               |
| Add a multi-step workflow Claude auto-picks | `.claude/skills/<name>/SKILL.md`           |
| Add a specialist sub-agent                  | `.claude/agents/<name>.md`                 |
| Allow/deny tools or add hooks               | `.claude/settings.json`                    |
| Add an MCP server for the team              | `.mcp.json`                                |
| Personal tweaks (not committed)             | `CLAUDE.local.md`, `.claude/settings.local.json` |

Keep `CLAUDE.md` short: link to rules instead of pasting them in.

## Reporting bugs

Open an issue using the **Bug report** template. Include steps to reproduce,
expected vs. actual behaviour, and `uv --version` / Python version.
