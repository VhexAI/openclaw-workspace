# Heartbeat checklist

## Context guard
- Check context %. If ≥70%: write checkpoint to memory/YYYY-MM-DD.md NOW. Skip everything else.
- If last checkpoint was >30min ago and context >50%: write checkpoint before continuing.

## Memory maintenance
- MEMORY.md size? If approaching 4KB: flag for pruning.
- Stale logs in memory/? If any >90 days: note for archiving.
- Uncompleted items from yesterday's log? Surface them.

## Exec checks
- Calendar: any meetings in the next 2 hours needing prep?
- Comms: any urgent messages or overdue follow-ups?
- Deadlines: anything due today not yet addressed?

## Report format
Use 🟢🟡🔴 indicators. One line each: Context, Memory, Calendar, Comms, Tasks.
If action was taken: state what was done.
If anything needs attention: report with → prefix.
If nothing needs attention: reply HEARTBEAT_OK
