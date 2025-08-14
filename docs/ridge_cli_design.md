# Ridge CLI - Final Architecture

<!--ascii art banner will be placed at top-->

## Core Philosophy
- **Context-Aware**: CLI understands project state, file changes, and conversation history
- **Mode-Driven**: Different flags activate different AI personalities/capabilities  
- **Agent-Based**: Specialized .md files define different AI behaviors
- **Memory-Persistent**: Ongoing partnership, not session-based
- **Cost-Optimized**: Smart caching and model selection

## Command Structure
```
ridge [target] [action] --[mode-flags] --[behavior-flags]
```

## Targets
- `file` - Single file operations
- `folder` - Directory-based operations  
- `project` - Entire project context
- `memory` - Agent memory files (.md configs)
- `context` - Access conversation history
- `session` - Session management

## Actions

### Direct Actions
- `edit` - Modify file/folder (user approval required unless `--allow-all` set)
- `create` - Create new file/folder (user approval required unless `--allow-all` set)  
- `analyze` - Read and analyze target
- `debug` - Static analysis tools first, then doctor.md agent

### Query Actions  
- `status` - Git status, lint results, test status, recent activity
- `health` - Docker containers, database connections, API status, memory usage
- `explain` - Teaching mode with practical examples and breakdown

### Meta Actions
- `memory` - Memory management (init, search, decisions, recall)
- `config` - Configuration management  
- `history` - Conversation history management
- `context` - Context management (checkpoints, reset, summary)

## Model Selection & Flags

### Mode Flags (How AI Thinks)
- `--deep` - Web search + reasoning (claude-sonnet-4-20250514)
- `--ultra --deep` - Web search + maximum reasoning (claude-opus-4-1-20250805)
- `--debug` - Debug agent from doctor.md
- `--code` - Pure coding focus from code.md
- `--explain` - Teaching mode from professor.md (claude-3-5-sonnet-20241022)  
- `--quick` - Fast responses (claude-3-5-haiku-20241022)
- `--manager` - Project management from manager.md

### Behavior Flags (What AI Does)
- `--watch` - Monitor file changes and auto-respond
- `--interactive` - Back-and-forth conversation mode
- `--batch` - Process multiple targets (claude-3-5-sonnet-20241022 default)
- `--batch --quick` - Fast batch processing (claude-3-5-haiku-20241022)
- `--batch --ultra --deep` - Deep batch processing (claude-opus-4-1-20250805)
- `--dry-run` - Show what would happen, don't execute
- `--allow-all` - Skip approval prompts for session

## Agent System

```
agents/
├── partner.md      # Default AI personality  
├── manager.md      # Project management, docs, logs
├── doctor.md       # Debug specialist
├── professor.md    # Teaching specialist
├── code.md         # Pure coding focus
├── architect.md    # System design specialist
└── reviewer.md     # Code review specialist
```

### Agent Definitions

**professor.md Role**: Senior software engineer who breaks down complex code, functions, tools, and libraries. Starts high-level then drills into practical working examples so Brian can apply the concepts immediately.

**manager.md Role**: Project coordinator who generates and maintains documentation, tracks decisions, manages logs, monitors project health, and keeps development organized.

## Context Management

### Smart Context Strategy
- **Default**: Continuous partnership mode (context persists)
- **Auto-checkpoints**: Every 25 messages, auto-checkpoint with summary
- **Smart summarization**: Compress context older than 100 messages, keep recent 50 full
- **First 10 guarantee**: Always preserve first 10 messages of project
- **Context tracker**: Visual progress bar showing context usage
- **Selective context**: Include only relevant cached insights, not full history

### Context Commands
```bash
ridge context status                    # Show context usage, checkpoints
ridge context checkpoint "auth working" # Manual checkpoint  
ridge context reset-to latest          # Reset to latest auto-checkpoint
ridge context reset-to "auth working"  # Reset to named checkpoint
ridge session --new                    # Start fresh session (rare use)
```

## Local Caching (Redis)
- **File analysis**: Cache by file hash, reuse if unchanged
- **Project summaries**: Cache structure overviews, update on file add/remove
- **Agent processing**: Cache parsed .md agent files
- **API responses**: Cache common explanations and patterns
- **Static analysis**: Cache lint results, syntax checks

## Memory Architecture

### Database Schema (PostgreSQL)
```sql
projects (project_id, name, path, created_at, last_active, status)
conversations (id, project_id, timestamp, command, context_snapshot, response)  
decisions (id, project_id, category, decision, reasoning, timestamp)
files_tracked (id, project_id, path, hash, last_analyzed, insights)
checkpoints (id, project_id, message_id, description, timestamp)
```

### Auto-Memory Features
- Every `ridge` command logged automatically
- File changes detected and stored
- Key decisions extracted from AI responses  
- Context building pulls relevant memory before API calls
- 30-day retention for detailed logs

## Error Recovery Strategy

### Graceful Degradation
1. **API failure**: Fall back to cached responses if available
2. **Network issues**: Queue commands for retry with exponential backoff
3. **Context overflow**: Auto-summarize and checkpoint
4. **Memory full**: Auto-cleanup old conversations, keep decisions
5. **Static analysis failure**: Continue with Claude analysis, log warning

### Error Commands
```bash
ridge health                 # Check all systems
ridge memory cleanup         # Manual cleanup old data  
ridge cache clear           # Clear all caches
ridge retry last            # Retry failed command
```

## Implementation Phases

### Phase 1: Foundation (Night 1-2)
- [ ] CLI parser with argument validation
- [ ] Basic API wrapper with model selection
- [ ] Agent .md file loading system
- [ ] Docker setup (PostgreSQL + Redis)
- [ ] Simple file operations with caching

### Phase 2: Memory & Context (Night 3-4)  
- [ ] Database schema and connection
- [ ] Context management with auto-checkpoints
- [ ] Memory commands (init, search, recall)
- [ ] Conversation logging and retrieval

### Phase 3: Intelligence (Night 5-6)
- [ ] Smart context building from memory
- [ ] Static analysis integration (ESLint, Pylint)
- [ ] Error recovery and graceful degradation
- [ ] Agent personality application

### Phase 4: Polish (Night 7-8)
- [ ] Interactive mode with memory continuity
- [ ] Batch processing with progress tracking  
- [ ] Configuration system and customization
- [ ] Performance optimization and monitoring

## Key Technical Decisions

### Context Limits Strategy
**Target**: 32k tokens max per API call
- Recent context: ~8k tokens (last 50 messages)
- File content: ~16k tokens (current target files)
- Memory insights: ~4k tokens (relevant decisions/patterns)
- Agent instructions: ~2k tokens (personality/tools)
- Buffer: ~2k tokens (safety margin)

### Auto-Checkpoint Logic
```python
def should_checkpoint(message_count, context_size):
    return (
        message_count % 25 == 0 or           # Every 25 messages
        context_size > 28000 or              # Approaching limit
        detect_major_decision(last_response) # AI made important decision
    )
```

### File Change Detection
- Watch git status for tracked files
- Monitor file modification times in project root
- Hash-based change detection for accuracy
- Ignore build artifacts and dependencies

## Extension Points
- ✅ Custom agent creation wizard
- ✅ Plugin system for new commands  
- ✅ Integration hooks for development tools
- ✅ Team sharing of agent configurations
- ✅ Project-specific overrides and templates

## Questions Resolved

1. **Context Limits**: 32k token strategy with smart layering ✅
2. **Memory Granularity**: 30-day detailed retention with decision permanence ✅  
3. **Tool Access**: Partner controls other agents, all have project CRUD access ✅
4. **Error Recovery**: Graceful degradation with fallbacks ✅
5. **Auto-Checkpoints**: Every 25 messages + size triggers + decision detection ✅

---

**Status**: Ready to build. Foundation is solid, complexity is managed, cost optimization built-in.