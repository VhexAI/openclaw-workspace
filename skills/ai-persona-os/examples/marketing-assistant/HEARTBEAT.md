# Heartbeat checklist

## Context guard
- Check context %. If ≥70%: write checkpoint to memory/YYYY-MM-DD.md NOW. Skip everything else.
- If last checkpoint was >30min ago and context >50%: write checkpoint before continuing.

## Memory maintenance
- MEMORY.md size? If approaching 4KB: flag for pruning.
- Stale logs in memory/? If any >90 days: note for archiving.
- Uncompleted items from yesterday's log? Surface them.

## Marketing checks
- Content calendar: anything due to publish today or tomorrow?
- Campaign performance: any metrics flagged or trending unusual?
- Social channels: any engagement spikes or mentions needing response?

## Report format
Use 🟢🟡🔴 indicators. One line each: Context, Memory, Content, Campaigns, Tasks.
If action was taken: state what was done.
If anything needs attention: report with → prefix.
If nothing needs attention: reply HEARTBEAT_OK
