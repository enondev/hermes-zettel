---
id: 20261105-0625
type: human
author: human
tags: [git, cleanup, workflow, context-handoff, rebase]
status: active
---
# Git Cleanup Workflow for Context Handoff Files

**Originating fleeting note:** [[context-handoff-cleanup-20261105]]

## Scenario

Cleaned up obsolete context handoff files that accumulated during initial integration of the context handoff generation system. The deduplication logic was working correctly, but a self-referential snapshot file from the first generation remained in the repository.

## Workflow Steps

1. **Create a cleanup branch** from the current worktree
   ```bash
   git checkout -b chore/git-cleanup-context-handoff
   ```

2. **Remove obsolete files** — In this case, `permanent/context-handoff-20261103-2031.md` which was self-referential and contained links to itself and `context-handoff-latest`

3. **Commit with conventional message**
   ```bash
   git commit -m "chore: remove obsolete context handoff snapshot (20261103-2031)"
   ```

4. **Fast-forward merge to master**
   ```bash
   git checkout master
   git merge chore/git-cleanup-context-handoff  # fast-forward
   ```

5. **Rebase onto remote master** (divergent history)
   ```bash
   git pull --rebase origin master
   ```

6. **Push to origin**
   ```bash
   git push origin master
   ```

## Verification Checklist

- [ ] `git status` shows clean working tree on master
- [ ] All expected context handoff files present:
  - `context-handoff-20261103-2124.md` (valid historical snapshot)
  - `context-handoff-20261104-2022.md` (valid historical snapshot)
  - `context-handoff-latest.md` (current stable copy)
- [ ] Generation script (`scripts/generate_context_handoff.py`) unchanged and functional
- [ ] No broken WikiLinks in remaining files

## Key Learnings

- **Self-referential handoff files** can occur during initial integration when the generation script runs before the "latest" copy exists
- **Deduplication via content normalization** (stripping timestamps/IDs before hashing) correctly prevents redundant file generation
- **Fast-forward + rebase workflow** keeps history clean when local and remote have diverged
- **File references in task bodies may not match reality** — verify actual repository state before assuming files exist

## References

- [[context-handoff-cleanup-20261105]]
- [[categories]]
- [[000-baseline-index]]
- [[context-handoff-deduplication-20261105]]