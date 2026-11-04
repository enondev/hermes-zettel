---
id: 20261103-0732
type: fleeting
author: human
tags: [promote-pattern, workflow]
status: active
---
# Promote Fleeting → Permanent Pattern

A repeatable workflow for turning a fleeting entry into permanent human and agent learning notes.

## Step‑by‑Step

1. **Create a fleeting note** in `/fleeting` with a timestamped slug (e.g., `fleeting-session-note-20261103.md`).  
   - Include a `## Prompt` section and a `## Observations` section.  
   - Add a `## References` block linking to `[[categories]]` and `[[000-baseline-index]]`.

2. **Review the fleeting entry** (manually or via a short‑circuit script).  
   - Identify concepts mastered by the human → create/update a note in `/literature/human`.  
   - Identify gaps bridged by Hermes → create/update a note in `/literature/agent`.

3. **Create the human progress note** (if new) or append to an existing one.  
   - Use the same `id` pattern: `YYYYMMDD-HHMM`.  
   - Include a `## References` section linking to `[[categories]]`, `[[000-baseline-index]]`, and the originating fleeting note (e.g., `[[fleeting-session-note-20261103]]`).

4. **Create the agent progress note** (if new) or append to an existing one.  
   - Same `id` pattern, with `author: hermes`.  
   - Link back the fleeting note in `## References`.

5. **Archive or delete the fleeting note**  
   - Option A: Move it to an `/archive/fleeting` sub‑folder and keep a WikiLink reference.  
   - Option B: Delete it if no longer needed, but ensure the human/agent notes retain the link for provenance.

6. **Update the garden overview**  
   - Re‑run the synthesis note (`permanent/synthesis-20261103.md`) or regenerate a “current state” view using Quartz graph features.

## Provenance Example

```
## References

- [[categories]]
- [[000-baseline-index]]
- [[fleeting-session-note-20261103]]
- [[human-progress-20261103]]
- [[agent-progress-20261103]]
```

## Tips

- Keep the fleeting note **short** (a few sentences). If it grows, consider promoting it sooner.
- Use **consistent tagging** (`tags: [learning-tracker, promote]``) so the entries are searchable.
- After promoting, **run a quick link‑check** (`git grep '\['` or Obsidian link validator) to ensure no orphan WikiLinks remain.