Ridge Base — Agent Guide

Build/test
- Create venv and install deps: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- Start services (Postgres 5433, Redis 6379): `docker compose up -d`
- Apply DB schema/migration: `psql -h localhost -p 5433 -U ridge_user -d ridge_base < sql/init_schema.sql` then `psql ... < sql/migrate_context_management.sql`
- Set API key: `export ANTHROPIC_API_KEY=...`
- Run all tests: `pytest -q`
- Run a single test: `pytest -q test_context_management.py::test_context_system` or by keyword `pytest -q -k context_system`

Architecture
- CLI entry: [cli.py](file:///home/ridgetop/ridge_base/src/cli.py) (Click groups: `memory`, `context`; analysis command `ridge [target] analyze` flows through AgentManager → RidgeAPI → MemoryManager)
- AI API: [api.py](file:///home/ridgetop/ridge_base/src/api.py) wraps Anthropic; model selection via flags (`quick/deep/ultra`). Requires `ANTHROPIC_API_KEY`.
- Memory/context: [memory.py](file:///home/ridgetop/ridge_base/src/memory.py), [context.py](file:///home/ridgetop/ridge_base/src/context.py) with auto-checkpoints and Rich UI.
- Persistence: [database.py](file:///home/ridgetop/ridge_base/src/database.py) (SQLAlchemy Session), models in [models.py](file:///home/ridgetop/ridge_base/src/models.py). Postgres/Redis via [docker-compose.yml](file:///home/ridgetop/ridge_base/docker-compose.yml); schema SQL in [sql/](file:///home/ridgetop/ridge_base/sql).
- File tracking: [file_tracker.py](file:///home/ridgetop/ridge_base/src/file_tracker.py) tracks code files and hashes.
- Agents: markdown configs in [agents/](file:///home/ridgetop/ridge_base/agents) parsed by [agents.py](file:///home/ridgetop/ridge_base/src/agents.py).
- Editing: side-by-side diff viewer and approval flow in [cli.py](file:///home/ridgetop/ridge_base/src/cli.py); backups via [backup_manager.py](file:///home/ridgetop/ridge_base/src/backup_manager.py).

Code style
- Python 3.10+ assumed; follow PEP 8, snake_case functions, PascalCase classes; type hints used in managers.
- Imports are local (e.g., `from models import Project`) with `src` added to `sys.path`; keep module-local imports consistent.
- Formatting/lint: no configured tools (no ruff/black/mypy). Prefer readable 100-col lines, f-strings, and explicit try/except with session commit/rollback.
- Errors: print via Rich console where available; database ops wrap in try/except with `session.rollback()` then re-raise or return False.
- Env/secrets: load with `python-dotenv`; never commit keys; require `ANTHROPIC_API_KEY`.

Notes
- Goal is build and learn. User hand-types code; unless the user asks for direct updates, provide code/diffs each session. Build in modular steps.
- No Cursor/Claude/Windsurf/Cline/Goose/Copilot rules found.
- Some schema naming differs between SQL and ORM; use provided SQL migrations to align before running features.
