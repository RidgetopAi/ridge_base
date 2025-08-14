# Ridge CLI - Command Reference Guide

## Command Pattern
```
ridge [target] [action] --[mode-flags] --[behavior-flags]
```

## Common Workflows

### File Operations
```bash
# Analyze a single file
ridge app.py analyze                    # Default partner agent
ridge app.py analyze --debug            # Debug agent reviews the file
ridge app.py analyze --professor        # Teaching breakdown of the code

# Edit files
ridge config.json edit --code           # Pure coding focus
ridge README.md edit --manager          # Project manager updates docs
ridge utils.py edit --debug --dry-run   # Debug agent shows what changes it would make

# Create new files
ridge database.py create --architect    # System design approach
ridge test_auth.py create --code        # Minimal explanation, just code
ridge CHANGELOG.md create --manager     # Project management formatting
```

### Folder Operations
```bash
# Analyze project structure
ridge src/ analyze --architect          # High-level design review
ridge tests/ analyze --debug            # Find testing issues
ridge docs/ analyze --manager           # Documentation audit

# Batch operations
ridge components/ edit --batch --code   # Update multiple components
ridge src/ analyze --batch --quick      # Fast analysis of all source files
```

### Project-Wide Operations
```bash
# Project health checks
ridge project status                    # Git, lint, tests, recent activity
ridge project health                    # Docker, DB, APIs, memory usage
ridge project analyze --manager         # Full project review and recommendations

# Deep project analysis
ridge project analyze --deep            # With web search for best practices
ridge project analyze --ultra --deep    # Maximum reasoning with web search
```

### Memory & Context Management
```bash
# Memory operations
ridge memory init FloorBuddy            # Start new project tracking
ridge memory status                     # Recent decisions, file changes
ridge memory search "authentication"    # Find all auth-related discussions
ridge memory decision "using FastAPI" --category=tech_choice

# Context management
ridge context status                    # Show context usage and checkpoints
ridge context checkpoint "auth working" # Manual checkpoint
ridge context reset-to latest          # Reset to latest auto-checkpoint
```

### Debug Workflows
```bash
# Static analysis first, then AI
ridge app.py debug                      # Runs ESLint/Pylint, then doctor.md agent
ridge src/ debug --batch               # Debug entire codebase
ridge main.py debug --interactive      # Back-and-forth debugging session

# Deep debugging
ridge error.log analyze --debug --deep # Web search for error solutions
ridge tests/ debug --ultra --deep      # Maximum debugging power
```

### Learning & Explanation
```bash
# Understanding code
ridge complex_function.py explain --professor    # Teaching breakdown
ridge library_usage.py explain --interactive    # Q&A about the code
ridge architecture.md explain --architect       # System design explanation

# Quick help
ridge auth.py explain --quick          # Fast explanation with Haiku
ridge utils.py explain --code          # Just the technical details
```

### Batch Processing
```bash
# Multiple file operations
ridge *.py analyze --batch             # Analyze all Python files
ridge components/ create --batch --manager  # Create multiple files with docs
ridge src/ edit --batch --code --dry-run    # Show what batch edits would do

# Different batch speeds
ridge tests/ analyze --batch --quick   # Fast batch with Haiku
ridge src/ review --batch --deep       # Thorough batch with web search
```

### Advanced Combinations
```bash
# Complex workflows
ridge app.py edit --debug --interactive --watch     # Debug, chat, monitor changes
ridge src/ analyze --architect --deep --batch       # Design review with research
ridge project create --manager --ultra --deep       # Full project planning

# Safety and approval
ridge config/ edit --batch --allow-all             # Skip approval prompts
ridge database.py edit --debug --dry-run           # Show changes without applying
ridge src/ create --manager --interactive          # Create with discussion
```

### Session Management
```bash
# Session control (rare usage)
ridge session --new                    # Start fresh context (breaks partnership)
ridge session status                   # Show current session info

# Most work stays in continuous partnership mode
ridge project analyze --manager        # Continues previous context
ridge memory recall --last-week        # Pull in recent project history
```

### Monitoring & Maintenance
```bash
# System health
ridge health                           # Check all Ridge systems
ridge memory cleanup                   # Clean old conversation logs
ridge cache clear                      # Clear Redis cache
ridge retry last                       # Retry failed command

# Performance monitoring
ridge context status                   # Context usage and optimization
ridge memory status                    # Memory usage and recent activity
```

## Flag Combinations That Make Sense

### Teaching & Learning
```bash
ridge complex_code.py explain --professor --interactive
ridge new_library.py analyze --professor --deep
ridge architecture.md create --professor --manager
```

### Production Debugging
```bash
ridge error.log debug --debug --deep --interactive
ridge failing_test.py debug --debug --ultra --deep
ridge performance_issue.py analyze --debug --batch
```

### Project Management
```bash
ridge project status --manager
ridge docs/ create --manager --batch
ridge CHANGELOG.md edit --manager --interactive
```

### Code Reviews
```bash
ridge pull_request/ analyze --reviewer --batch
ridge new_feature.py review --code --debug
ridge refactor/ analyze --architect --deep
```

## Common Patterns

### Daily Development Flow
```bash
# Start day
ridge project status --manager
ridge memory recall --yesterday

# Work on feature
ridge feature.py create --architect
ridge feature.py edit --code --watch
ridge feature.py debug --debug

# End day
ridge project analyze --manager
ridge memory decision "completed auth feature"
```

### Code Learning Sessions
```bash
# Understanding new codebase
ridge project analyze --professor --deep
ridge core/ explain --professor --batch --interactive
ridge complex_module.py explain --professor --ultra --deep
```

### Troubleshooting Workflow
```bash
# When things break
ridge project health
ridge error.log analyze --debug --deep
ridge failing_component.py debug --debug --interactive --watch
ridge memory search "similar error"
```