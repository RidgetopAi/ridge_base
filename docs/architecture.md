# Ridge Base Architecture

Scope
- CLI-first AI dev assistant with persistent memory, context mgmt, file analysis/editing (create planned).

Components
- CLI: [cli.py](file:///home/ridgetop/ridge_base/src/cli.py) — Click commands: `memory`, `context`, main `[target] [action]` (analyze/edit). Dispatch selects agent, builds prompt, renders Rich panels/tables, logs memory.
- Agents: [agents.py](file:///home/ridgetop/ridge_base/src/agents.py) loads markdown agents in [agents/](file:///home/ridgetop/ridge_base/agents) and builds system prompts.
- AI API: [api.py](file:///home/ridgetop/ridge_base/src/api.py) wraps Anthropic. Model map via flags: quick/deep/ultra; requires `ANTHROPIC_API_KEY`.
- Memory: [memory.py](file:///home/ridgetop/ridge_base/src/memory.py) logs conversations/decisions, auto-checkpoints after N messages/size.
- Context: [context.py](file:///home/ridgetop/ridge_base/src/context.py) shows usage, creates/resets checkpoints; token budgeting helpers.
- Persistence: [database.py](file:///home/ridgetop/ridge_base/src/database.py) SQLAlchemy session; models in [models.py](file:///home/ridgetop/ridge_base/src/models.py). Postgres/Redis via [docker-compose.yml](file:///home/ridgetop/ridge_base/docker-compose.yml). SQL in [sql/](file:///home/ridgetop/ridge_base/sql).
- File tracking: [file_tracker.py](file:///home/ridgetop/ridge_base/src/file_tracker.py) scans, hashes, tracks updates; Rich tables.
- Backups: [backup_manager.py](file:///home/ridgetop/ridge_base/src/backup_manager.py) creates timestamp/hash backups under [.ridge_backups/](file:///home/ridgetop/ridge_base/.ridge_backups/).
- Utils: [utils.py](file:///home/ridgetop/ridge_base/src/utils.py) file ops, hashing.

Data model (ORM)
- Project, Conversation(archived), Decision, FileTracked, Checkpoint(auto_created). See [models.py](file:///home/ridgetop/ridge_base/src/models.py) and SQL migrations in [sql/](file:///home/ridgetop/ridge_base/sql).

Workflows
- Analyze: read file → select agent → `api.chat_with_agent` → Rich panel → memory log.
- Edit: backup → prompt → AI suggests full file → side‑by‑side diff (Rich Table) → confirm (`--allow-all` to auto-apply) → write → memory log.

Commands (representative)
- Main: `python src/cli.py [target] analyze|edit [--flags]` or `python src/cli.py main [file] edit` per current flow
- Memory: `ridge memory init|status|search|decision`
- Context: `ridge context status|checkpoint|reset-to`

Environments
- Start: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && docker compose up -d`
- DB: Postgres 5433, Redis 6379. Apply SQL in [sql/](file:///home/ridgetop/ridge_base/sql).

Design docs (source)
- [ridge_cli_design.md](file:///home/ridgetop/ridge_base/docs/ridge_cli_design.md)
- [ridge_command_reference.md](file:///home/ridgetop/ridge_base/docs/ridge_command_reference.md)
- [ridge_phase4b_handoff.md](file:///home/ridgetop/ridge_base/docs/ridge_phase4b_handoff.md)
- [ridge_updated_todo.md](file:///home/ridgetop/ridge_base/docs/ridge_updated_todo.md)
