# Deployment

## Contents
- Scope priority order
- Container deploy fallback
- Post-deploy reminders

## Scope priority order

When subagent names collide, Claude Code resolves in this strict order (highest to lowest):

| Priority | Scope | Path | Use for |
|---|---|---|---|
| 1 | **Session** | defined in current session via SDK or hooks | Ephemeral experiments |
| 2 | **Project** | `./.claude/agents/<n>.md` | Tied to a repo, version-controlled, team-shared |
| 3 | **User** | `~/.claude/agents/<n>.md` | Personal, all projects on this machine |
| 4 | **Plugin** | bundled in installed plugin | Plugin distribution |

A library repo (e.g., `summit-claude-agents/`) is not a separate scope — it is just a tracked source the user clones or symlinks into one of the above locations.

## Container deploy fallback

Container sessions cannot `git push` without a PAT. Use `git format-patch` + `git am` instead:

```bash
git checkout -b agent-architect/add-<n>
git add .claude/agents/<n>.md
git commit -m "feat(agents): add <n> subagent"
git format-patch -1 HEAD --stdout > /tmp/<n>.patch
```

Surface the patch path so the user can apply locally:

```bash
git am < /tmp/<n>.patch
git push origin agent-architect/add-<n>
```

NEVER use `git commit --amend` in container sessions.

## Post-deploy reminders

Always remind the user:

> Subagents load at session start. Run `/agents` in Claude Code to reload, or restart the session, before invoking this agent.

Then suggest a test invocation:

> Try it: `Use the <n> subagent on <concrete example task>`
