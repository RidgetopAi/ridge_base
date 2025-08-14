# Decisions Log

Guiding principles
- Build-and-learn: user types code; assistant proposes code and diffs unless explicitly asked to edit files.
- Modular, incremental phases; document changes and rationale.

Recorded decisions
- CLI pattern: `ridge [target] [action] --flags` (see [ridge_cli_design.md](file:///home/ridgetop/ridge_base/docs/ridge_cli_design.md)).
- Agents as markdown configs in [agents/](file:///home/ridgetop/ridge_base/agents); selected by flags (debug/manager/code/professor/quick/deep/ultra).
- Persistent memory in Postgres; Redis reserved for caching later.
- Context limits: ~32k tokens budget; auto-checkpoint every 25 msgs or >28k tokens.
- Backups required before edits via [backup_manager.py](file:///home/ridgetop/ridge_base/src/backup_manager.py); backups git-ignored.
- Safety: `--dry-run` and `--allow-all` control edit application.
- Model map set in [api.py](file:///home/ridgetop/ridge_base/src/api.py) per flags.
- Default diff view for edits: side-by-side Rich table; unified diff kept as fallback.
- Helpers `extract_code_from_response` and diff renderers live at module scope in [cli.py](file:///home/ridgetop/ridge_base/src/cli.py) to avoid scope issues.
- Avoid assigning to `console` inside functions; use the module-level `console` only.

Open questions
- Batch operations defaults and concurrency limits.
- Redis cache keys and invalidation strategy.
- Side-by-side diff color/width tuning and optional `--unified` flag.

How to add a decision
- Append a bullet with context, decision, and rationale. Significant choices should also be logged via `ridge memory decision`.
