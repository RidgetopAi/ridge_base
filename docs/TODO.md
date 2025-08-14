# Ridge Base TODO (source of truth)

Process
- Build-and-learn: user hand-types code; assistant proposes code/diffs unless explicitly asked to apply changes.
- Work in modular, incremental steps; update docs each session.

Status summary
- Phase 4B (File Editing) COMPLETE: backup + AI suggestion + side-by-side diff + approval + apply + memory log.
- Next focus: Phase 4C (Interactive mode) and File Creation.

Completed (today)
- File editing flow end-to-end
  - [x] Backup before edits via BackupManager
  - [x] AI suggestion pipeline (agent selection, prompt)
  - [x] Diff render (side-by-side Rich table)
  - [x] Approval flow (`--allow-all` bypass), `--dry-run` safety
  - [x] Apply changes and log to memory
  - [x] Helpers at module scope: `extract_code_from_response`, `show_diff_side_by_side`
  - [x] Fixed `console` scope bug (use module-level console only)

Next up
- Phase 4C: Interactive mode
  - [ ] `--interactive` loop for multi-turn edit/analyze sessions
  - [ ] Persist rolling context across turns
  - [ ] Clean exit and resume behavior
- File creation flow
  - [ ] `create` action with safe templates
  - [ ] Dry-run and approval path
  - [ ] Memory logging and optional backup of new file
- Caching and batch (after 4C)
  - [ ] Redis cache for analysis by file hash
  - [ ] `cache status|clear` commands
  - [ ] `--batch` progress + error handling

Quality/stability
- [ ] Improve error messages consistency and colors
- [ ] Add tests: backup manager, edit approve path, helpers parsing

Docs
- Keep [architecture.md](file:///home/ridgetop/ridge_base/docs/architecture.md) updated
- Log significant choices in [decisions.md](file:///home/ridgetop/ridge_base/docs/decisions.md)
