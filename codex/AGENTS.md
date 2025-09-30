# Repository Guidelines
## Project Structure & Module Organization
- `print_question.py` is the primary entry point; it parses CLI arguments and orchestrates the Codex CLI invocation. Keep this responsibility in the module and push new helpers into dedicated functions.
- Create a `src/` package when adding reusable modules; mirror the hierarchy under `tests/` (for example `src/prompting/utils.py` <-> `tests/prompting/test_utils.py`).
- Store one-off maintenance scripts under `tools/` with a short README describing usage and dependencies.

## Build, Test, and Development Commands
- Target Python 3.11+; create a virtual environment with `python -m venv .venv` followed by `.\.venv\Scripts\activate`.
- Dependencies: the project currently uses only the standard library; log any new third-party requirement in `requirements.txt` and regenerate `package-lock.json` if you add Node tooling.
- Quick run: `python print_question.py "Your research question"` prints the question and triggers PICO generation via Codex.
- Tests: run `pytest` inside the activated environment; aim for <30 s wall clock time on a recent laptop.

## Coding Style & Naming Conventions
- Follow PEP 8 (4-space indentation, lines <=88 chars) and add Google-style docstrings to all public functions.
- Naming: functions use `snake_case`, classes `CapWords`, modules descriptive (`prompt_formatter.py`).
- Run `ruff check .` before every pull request and `ruff format` for automatic formatting.

## Testing Guidelines
- Place tests under `tests/` and name files `test_<feature>.py`.
- Cover critical paths (argument parsing, prompt formatting, subprocess handling) with unit tests.
- Tag heavy tests with `@pytest.mark.slow` and isolate external effects with `unittest.mock`.

## Commit & Pull Request Guidelines
- Commit messages: short imperative summary with a conventional prefix (`feat:`, `fix:`, `docs:`) and body describing the rationale when needed.
- Pull requests: include a functional summary, the test and lint commands you ran, and link issues (`Closes #12`). Share CLI output snippets when behavior changes.
- Ask for at least one cross-review and ensure `ruff` and `pytest` both pass before requesting merge.

## Agent-Specific Notes
- Keep scripts runnable without elevated privileges; avoid `os.system` calls to unaudited commands.
- Log major steps with the standard `logging` module at `INFO` level for traceability in automated runs.
- Document any flow requiring tokens or secrets in `docs/configuration.md` using placeholders rather than live credentials.
