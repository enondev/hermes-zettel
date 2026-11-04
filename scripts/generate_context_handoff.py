#!/usr/bin/env python3
"""
Generate a context handoff file for the Hermes-Zettel garden.

This script scans the garden and produces a single .md file that encapsulates
the current state, so the next model doesn't need to review the entire project.

Only creates new timestamped files when the garden content has actually changed.
"""

import os
import re
import glob
import hashlib
from datetime import datetime
from pathlib import Path

GARDEN_ROOT = Path(__file__).parent.parent
FLEETING_DIR = GARDEN_ROOT / "fleeting"
LIT_HUMAN_DIR = GARDEN_ROOT / "literature" / "human"
LIT_AGENT_DIR = GARDEN_ROOT / "literature" / "agent"
PERMANENT_DIR = GARDEN_ROOT / "permanent"
OUTPUT_DIR = PERMANENT_DIR

FRONTMATTER_PATTERN = re.compile(r'^---\n(.*?)\n---', re.DOTALL)
FIELD_PATTERN = re.compile(r'^(\w+):\s*(.+)$', re.MULTILINE)


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}
    fm_text = match.group(1)
    fields = {}
    for field_match in FIELD_PATTERN.finditer(fm_text):
        key, value = field_match.groups()
        value = value.strip().strip('"\'')
        # Handle YAML arrays: [tag1, tag2] -> list
        if value.startswith('[') and value.endswith(']'):
            inner = value[1:-1].strip()
            if inner:
                fields[key] = [tag.strip() for tag in inner.split(',')]
            else:
                fields[key] = []
        else:
            fields[key] = value
    return fields


def scan_notes(directory: Path, pattern: str = "*.md") -> list:
    """Scan a directory for markdown notes and extract their metadata."""
    notes = []
    for filepath in directory.glob(pattern):
        if filepath.name.startswith(".") or filepath.name == "README.md":
            continue
        # Skip context handoff files to avoid self-reference
        if filepath.name.startswith("context-handoff"):
            continue
        try:
            content = filepath.read_text(encoding="utf-8")
            fm = parse_frontmatter(content)
            # Get the first heading as title
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else filepath.stem
            notes.append({
                "path": filepath.relative_to(GARDEN_ROOT),
                "filename": filepath.stem,
                "title": title,
                "frontmatter": fm,
                "content_preview": content[:500].replace('\n', ' ') + "..."
            })
        except Exception as e:
            notes.append({
                "path": filepath.relative_to(GARDEN_ROOT),
                "filename": filepath.stem,
                "title": filepath.stem,
                "frontmatter": {"error": str(e)},
                "content_preview": ""
            })
    return notes


def format_note_list(notes: list, section_name: str) -> str:
    """Format a list of notes as a markdown section."""
    if not notes:
        return f"## {section_name}\n\n*No entries found.*\n"

    lines = [f"## {section_name}\n"]
    for note in sorted(notes, key=lambda n: n["frontmatter"].get("id", ""), reverse=True):
        fm = note["frontmatter"]
        id_str = fm.get("id", "no-id")
        author = fm.get("author", "unknown")
        tags = fm.get("tags", [])
        status = fm.get("status", "unknown")
        tags_str = f" [{', '.join(tags)}]" if tags else ""
        lines.append(f"- **[[{note['filename']}]]** ({id_str}) — {note['title']}")
        lines.append(f"  - Author: {author} | Status: {status}{tags_str}")
    lines.append("")
    return "\n".join(lines)


def normalize_content(content: str) -> str:
    """
    Normalize content for comparison by removing timestamp/id fields
    that change on every generation but don't reflect actual garden state changes.
    """
    lines = content.split('\n')
    normalized = []
    in_frontmatter = False
    frontmatter_done = False

    for line in lines:
        if line.strip() == '---' and not frontmatter_done:
            in_frontmatter = not in_frontmatter
            normalized.append(line)
            if not in_frontmatter:
                frontmatter_done = True
            continue

        if in_frontmatter:
            # Skip id and timestamp fields in frontmatter
            if line.strip().startswith('id:') or line.strip().startswith('generated:'):
                continue
            normalized.append(line)
        else:
            # In body, normalize the title timestamp
            if line.startswith('# Context Handoff: Garden State ('):
                # Replace with placeholder
                normalized.append('# Context Handoff: Garden State (TIMESTAMP)')
            elif line.startswith('This note encapsulates the complete state of the Hermes-Zettel garden as of '):
                normalized.append('This note encapsulates the complete state of the Hermes-Zettel garden as of TIMESTAMP.')
            elif line.strip().startswith('- Generated by:'):
                normalized.append(line)
            elif line.strip().startswith('- Timestamp:'):
                normalized.append('- Timestamp: TIMESTAMP')
            elif line.strip().startswith('- Source:'):
                normalized.append(line)
            else:
                normalized.append(line)

    return '\n'.join(normalized)


def compute_content_hash(content: str) -> str:
    """Compute a hash of the normalized content for change detection."""
    normalized = normalize_content(content)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]


def get_existing_latest_hash() -> str | None:
    """Get the content hash of the existing latest handoff file."""
    latest_path = OUTPUT_DIR / "context-handoff-latest.md"
    if not latest_path.exists():
        return None
    try:
        content = latest_path.read_text(encoding="utf-8")
        return compute_content_hash(content)
    except Exception:
        return None


def generate_handoff() -> tuple[str, str]:
    """Generate the full context handoff markdown. Returns (content, timestamp)."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Scan all directories
    fleeting_notes = scan_notes(FLEETING_DIR)
    human_notes = scan_notes(LIT_HUMAN_DIR)
    agent_notes = scan_notes(LIT_AGENT_DIR)
    permanent_notes = scan_notes(PERMANENT_DIR)

    # Count totals
    total_notes = len(fleeting_notes) + len(human_notes) + len(agent_notes) + len(permanent_notes)

    # Build the handoff document
    lines = [
        f"---\nid: {timestamp}\ntype: permanent\nauthor: hermes\ntags: [context-handoff, session-summary, garden-state]\nstatus: active\ngenerated: {datetime.now().isoformat()}\n---",
        f"# Context Handoff: Garden State ({date_str})",
        "",
        f"This note encapsulates the complete state of the Hermes-Zettel garden as of {date_str}. ",
        f"It is generated automatically so the next model can acquire full context without reviewing every file.",
        "",
        f"## Garden Statistics",
        f"",
        f"- **Total notes**: {total_notes}",
        f"- **Fleeting (session buffer)**: {len(fleeting_notes)}",
        f"- **Literature (Human)**: {len(human_notes)}",
        f"- **Literature (Agent)**: {len(agent_notes)}",
        f"- **Permanent (synthesis/index)**: {len(permanent_notes)}",
        f"",
        "---",
        ""
    ]

    # Add each section
    lines.append(format_note_list(permanent_notes, "Permanent Notes (Synthesis & Indexes)"))
    lines.append(format_note_list(human_notes, "Human Literature (Concept Mastery)"))
    lines.append(format_note_list(agent_notes, "Agent Literature (Gaps Bridged)"))
    lines.append(format_note_list(fleeting_notes, "Fleeting Notes (Session Buffer)"))

    # Add key cross-references
    lines.extend([
        "---",
        "",
        "## Key Navigation Links",
        "",
        "- [[000-baseline-index]] — Root milestone anchoring all notes",
        "- [[categories]] — Tag/categorisation catalogue",
        "- [[search-index]] — Central navigation index with quick-link map",
        "- [[synthesis-20261103]] — Latest synthesis of human + agent progress",
        "",
        "## How to Use This Handoff",
        "",
        "1. **Start here** — This file gives you the complete garden inventory.",
        "2. **Follow WikiLinks** — Use `[[note-name]]` links to jump to any entry.",
        "3. **Check permanent/ first** — Synthesis and index notes provide the highest-level view.",
        "4. **Review fleeting/ last** — These are raw session buffers; promote if valuable.",
        "",
        "## Generation",
        "",
        f"- Generated by: `scripts/generate_context_handoff.py`",
        f"- Timestamp: {timestamp}",
    ])

    return "\n".join(lines), timestamp


def main():
    """Main entry point."""
    handoff_content, timestamp = generate_handoff()

    # Compute hash of new content (normalized)
    new_hash = compute_content_hash(handoff_content)
    existing_hash = get_existing_latest_hash()

    if new_hash == existing_hash:
        print(f"No changes detected in garden state (hash: {new_hash}). Skipping file generation.")
        print(f"Latest handoff remains: {OUTPUT_DIR / 'context-handoff-latest.md'}")
        return

    # Content has changed - write new files
    print(f"Garden state changed (old: {existing_hash}, new: {new_hash}). Generating new handoff.")

    # Write to a timestamped file (archival)
    output_path = OUTPUT_DIR / f"context-handoff-{timestamp}.md"
    output_path.write_text(handoff_content, encoding="utf-8")

    # Also write/update a stable "latest" copy
    latest_path = OUTPUT_DIR / "context-handoff-latest.md"
    latest_path.write_text(handoff_content, encoding="utf-8")

    print(f"Generated context handoff: {output_path}")
    print(f"Updated latest handoff: {latest_path}")


if __name__ == "__main__":
    main()