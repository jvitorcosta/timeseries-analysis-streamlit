# Forecast error analysis

Evaluate daily forecasts: where they miss, by series, period and holiday, and against a benchmark.

[![CI](https://github.com/jvitorcosta/timeseries-analysis-streamlit/actions/workflows/ci.yml/badge.svg)](https://github.com/jvitorcosta/timeseries-analysis-streamlit/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Requirements

[uv](https://docs.astral.sh/uv/) (it installs Python 3.12 for you), Git ≥ 2.31 and `make`:

| Tool | macOS | Linux (Debian/Ubuntu) | Windows (PowerShell) |
| ---- | ----- | --------------------- | -------------------- |
| uv   | `brew install uv` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `winget install astral-sh.uv` |
| Git  | `brew install git` | `sudo apt install git` | `winget install Git.Git` |
| make | `xcode-select --install` | `sudo apt install make` | `winget install ezwinports.make` |

All `make` targets work in bash, zsh, PowerShell and cmd. Without `make`, run the
`uv run ...` line from the [Makefile](Makefile). On Windows, also run
`git config --global core.longpaths true` once.

## Quickstart

```bash
git clone https://github.com/jvitorcosta/timeseries-analysis-streamlit.git
cd timeseries-analysis-streamlit
make install   # uv sync + pre-commit hooks
make check     # lint + typecheck + tests
```

## Development

| Command          | What it does                              |
| ---------------- | ----------------------------------------- |
| `make help`      | List every target                         |
| `make format`    | Ruff format + safe autofixes              |
| `make lint`      | Ruff lint + format check                  |
| `make typecheck` | mypy (strict)                             |
| `make test`      | pytest                                    |
| `make cov`       | pytest with coverage (fails under 80%)    |
| `make check`     | Everything CI runs                        |
| `make upgrade`   | Bump all deps in `uv.lock`                |

Add dependencies with `uv add <pkg>` (runtime) or `uv add --dev <pkg>` (tooling).

## Project layout

```
.
├── CLAUDE.md              # Context Claude Code loads every session
├── .mcp.json              # Shared MCP servers
├── .claude/
│   ├── settings.json      # Permissions + hooks (team-shared)
│   ├── rules/             # Topic-scoped guidance (style, testing, API)
│   ├── commands/          # /review, /fix-issue
│   ├── skills/            # Auto-loaded workflows (release)
│   ├── agents/            # code-reviewer, security-auditor
│   └── hooks/             # Bash guard + auto-format
├── src/forecast_eval/
├── tests/
├── Makefile
└── pyproject.toml
```

## Working with Claude Code

This repo ships a full `.claude/` setup. See [CLAUDE.md](CLAUDE.md) for the
project context and [CONTRIBUTING.md](CONTRIBUTING.md#working-with-claude-code)
for how to extend it. Personal overrides go in `CLAUDE.local.md` and
`.claude/settings.local.json`; both are gitignored.

## Keeping up with the template

This project was generated from a [Copier](https://copier.readthedocs.io) template.
To pull in template improvements:

```bash
uvx copier update
```

`README.md`, `CHANGELOG.md` and `src/forecast_eval/__init__.py` belong to this project:
`copier update` leaves them alone (`protect_project_files` in `.copier-answers.yml`).

## License

[MIT](LICENSE) © Vitor Pinheiro
