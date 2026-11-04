---
id: 20261103-0734
type: permanent
author: human
tags: [search, index, navigation]
status: active
---
# Search & Index

This note serves as the central index for the Hermes‑Zettel garden. Quartz (the static‑site generator used by this repository) automatically builds a searchable page from WikiLinks and frontmatter tags, but this note gathers the most useful cross‑references in one place for quick manual navigation.

## Human‑focused entries

- [[human-progress-20261103]] – What I learned about setting up the Zettelkasten.
- [[categories]] – Tag/categorisation catalogue.

## Agent‑focused entries

- [[agent-progress-20261103]] – Context gaps bridged during infrastructure setup.
- [[000-baseline-index]] – Root milestone that anchors all other notes.

## Quick‑link map

| Category | Linked note |
|----------|-------------|
| Baseline | [[000-baseline-index]] |
| Categories | [[categories]] |
| Human progress | [[human-progress-20261103]] |
| Agent progress | [[agent-progress-20261103]] |
| Synthesis | [[synthesis-20261103]] |
| Session Progress | [[session-progress-20261103-2040]] |
| Context Handoff | [[context-handoff-latest]] |

## How Quartz uses this file

- Every WikiLink `[[…]]` in any `.md` file under the repository is parsed and added to the site‑wide search index.
- Tags declared in YAML frontmatter (`tags: [...]`) are also indexed, allowing filter‑by‑tag pages.
- This note itself contains multiple links, so it appears in the graph view and can be reached from the “Search” textbox on the deployed site.

## Future extensions

- Add new entries here as the garden grows.
- Introduce tag‑specific index notes (e.g., `permanent/index-prompt-engineering.md`) if the tag count becomes large.
- Integrate with an external search engine (e.g., Algolia) by exporting the frontmatter data, but for now Quartz’s built‑in search is sufficient.