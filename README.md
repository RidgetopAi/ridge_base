# Ridge Base

Goal
- Build and learn. User is hand-typing code; unless the user asks for direct edits, the assistant provides code/diffs each session. We proceed in modular steps to show how to build from the ground up.

Quick start
- Env: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- Services: `docker compose up -d` (Postgres 5433, Redis 6379)
- DB schema: `psql -h localhost -p 5433 -U ridge_user -d ridge_base < sql/init_schema.sql` then `psql ... < sql/migrate_context_management.sql`
- API key: `export ANTHROPIC_API_KEY=...`
- Run: `python src/cli.py [target] analyze|edit [--flags]` or `python src/cli.py main [file] edit`

Docs
- Architecture: [docs/architecture.md](file:///home/ridgetop/ridge_base/docs/architecture.md)
- Decisions: [docs/decisions.md](file:///home/ridgetop/ridge_base/docs/decisions.md)
- TODO: [docs/TODO.md](file:///home/ridgetop/ridge_base/docs/TODO.md)
- Design refs: [ridge_cli_design.md](file:///home/ridgetop/ridge_base/docs/ridge_cli_design.md), [ridge_command_reference.md](file:///home/ridgetop/ridge_base/docs/ridge_command_reference.md), [ridge_phase4b_handoff.md](file:///home/ridgetop/ridge_base/docs/ridge_phase4b_handoff.md), [ridge_updated_todo.md](file:///home/ridgetop/ridge_base/docs/ridge_updated_todo.md)

Repo map
- CLI: [src/cli.py](file:///home/ridgetop/ridge_base/src/cli.py), Agents: [src/agents.py](file:///home/ridgetop/ridge_base/src/agents.py), API: [src/api.py](file:///home/ridgetop/ridge_base/src/api.py)
- Memory: [src/memory.py](file:///home/ridgetop/ridge_base/src/memory.py), Context: [src/context.py](file:///home/ridgetop/ridge_base/src/context.py)
- Persistence: [src/database.py](file:///home/ridgetop/ridge_base/src/database.py), [src/models.py](file:///home/ridgetop/ridge_base/src/models.py), SQL: [sql/](file:///home/ridgetop/ridge_base/sql)
- File tracking: [src/file_tracker.py](file:///home/ridgetop/ridge_base/src/file_tracker.py), Backups: [src/backup_manager.py](file:///home/ridgetop/ridge_base/src/backup_manager.py)

Editing flow (Phase 4B)
- Backup → AI suggestion → side-by-side diff → approval → apply → memory log. Use `--dry-run` to preview, `--allow-all` to auto-apply.

Conventions
- Python 3.10+, PEP 8. Local imports (`from models import Project`). Rich console for UX. Explicit try/except with `session.rollback()` on DB errors. Secrets via `python-dotenv`.
