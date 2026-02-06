# Heartbeat checklist

## Context guard
- Check context %. If ≥70%: write checkpoint to memory/YYYY-MM-DD.md NOW. Skip everything else.
- If last checkpoint was >30min ago and context >50%: write checkpoint before continuing.

## Memory maintenance
- MEMORY.md size? If approaching 4KB: flag for pruning.
- Stale logs in memory/? If any >90 days: note for archiving.
- Uncompleted items from yesterday's log? Surface them.

## Report format
Use 🟢🟡🔴 indicators for each system. One line each:
- Context: % and status
- Memory: sync state and last checkpoint age
- Workspace: file access and cleanliness
- Tasks: pending or overdue items

If action was taken (checkpoint written, cleanup done): state what was done.
If anything needs user attention: report with → prefix and specifics.
If nothing needs attention: reply HEARTBEAT_OK
