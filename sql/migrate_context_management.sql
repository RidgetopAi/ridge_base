-- sql/migrate_context_management.sql
-- Migration script to add context management features

-- Add archived column to conversations table for context management
ALTER TABLE conversations
ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT FALSE;

-- Add auto_crated column to checkpoints table
ALTER TABLE checkpoints
ADD COLUMN IF NOT EXISTS auto_created BOOLEAN DEFAULT FALSE;

-- Create index for better performance on archived conversations
CREATE INDEX IF NOT EXISTS idx_conversations_archived ON conversations(project_id, archived, timestamp DESC);

-- Create index for checkpoint lookups
CREATE INDEX IF NOT EXISTS idx_checkpoints_project_timestamp ON checkpoints(project_id, timestamp DESC);

-- Create index for file tracking
CREATE INDEX IF NOT EXISTS idx_files_tracked_project_path ON files_tracked(project_id, path);

-- Update any existing checkpoints to be marked as manual (not auto-created)
UPDATE checkpoints SET auto_created = FALSE WHERE auto_created IS NULL;