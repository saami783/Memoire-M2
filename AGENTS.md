# Repository Guidelines

This repository is a small Python toolchain that generates a PICO file and a matching arXiv boolean query, then downloads the corresponding PDFs.

## Project Structure & Module Organization
- `main.py`: CLI entrypoint wiring prompts → file generation → PDF download.
- `utils/`: helpers
  - `create_pico_file.py`, `create_boolean_queries_file.py`: spawn `codex` and watch files.
  - `codex_prompts.py`: prompt builders.
- `arxiv_api.py`: search/download via `arxiv`; tune `OUTPUT_DIR`, `PAGE_SIZE`, `DELAY_SECONDS`.
- `doc_boolean_queries.txt`: arXiv query syntax reference.
- Outputs: `PICO_*.txt`, `boolean_queries.txt`, PDFs under `pdf_arxiv_vertex_cover/` (default).

## Build, Test, and Development Commands
- Python 3.11+ (3.12 used locally). Setup and deps:
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install arxiv tqdm`
- Run locally:
  - `python main.py "Votre question de recherche"`
- `codex` CLI must be on your `PATH` (used by utils to generate files).

## Coding Style & Naming Conventions
- PEP 8, 4-space indentation, type hints where reasonable.
- snake_case for modules/functions; UPPER_SNAKE_CASE for constants (e.g., `OUTPUT_DIR`).
- Prefer pure functions and small modules in `utils/`.
- Formatting/linting (recommended):
  - `pip install black isort flake8`
  - `black . && isort . && flake8`

## Testing Guidelines
- No formal suite yet. Use `pytest`; place tests in `tests/`, mirroring module paths, named `test_*.py`.
- Mock network (`arxiv.Client`) and filesystem; avoid real arXiv calls in tests.
- Example: `pytest -q` (run all tests) or `pytest tests/test_arxiv_api.py -q`.

## Commit & Pull Request Guidelines
- Commits: concise, imperative, present tense (e.g., "Ajoute…", "Refactor: …"), subject ≤ 72 chars.
- PRs: include purpose, minimal repro/commands, sample outputs, and any config changes (e.g., `OUTPUT_DIR`). Link issues; add screenshots if user-facing.

## Agent-Specific Notes & Safety
- File watchers rely on the invariant: the last line of generated files equals the file name; keep this in prompts.
- Respect arXiv rate limits; adjust `DELAY_SECONDS`/`PAGE_SIZE` cautiously.
- Do not commit secrets. Generated artifacts (`PICO_*.txt`, PDFs) should be git-ignored if not needed.

