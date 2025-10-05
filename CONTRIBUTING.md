# Contributing Guide

Thank you for considering contributing!

## Quick Start
1. Fork the repository and clone locally.
2. Create a virtual environment (Python 3.8+).
3. Install in editable mode with dev deps:
   ```bash
   pip install -e .[dev]
   ```
4. Run tests:
   ```bash
   pytest -q
   ```
5. Create a feature branch:
   ```bash
   git checkout -b feat/short-description
   ```

## Development Commands
| Task | Command |
|------|---------|
| Lint (flake8) | `flake8 src` |
| Format (black) | `black src tests` |
| Type check | `mypy src` |
| Tests | `pytest -q` |
| Coverage | `pytest --cov=psychopy_ai_coder_assistant --cov-report=term-missing` |

## Commit Convention (Recommended)
Use Conventional Commits style:
`feat: add builder component suggestion for loops`

Types: feat, fix, chore, docs, refactor, test, perf, build.

## Pull Request Checklist
- [ ] Tests added / updated
- [ ] Lint passes
- [ ] No mypy errors (or justified)
- [ ] Docs / README updated if behavior changed

## Branch Naming
`feat/<slug>` `fix/<slug>` `chore/<slug>`

## Versioning
Semantic Versioning. Bump version in `pyproject.toml` and `__init__.py` together.

## Reporting Issues
Include:
- Steps to reproduce
- Expected vs actual behavior
- PsychoPy version / OS / Python version

## Security
Do not post API keys in issues. Use placeholder like `sk-****`.

## Code Style Notes
- Keep UI logic in `ui.py`
- Keep network / LLM provider logic in `llm_client.py`
- Add new pattern detections in `patterns.py` with clear docstring

## Thank You
Your contributions help empower the PsychoPy community.
