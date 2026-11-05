#!/usr/bin/env python3
"""
Build script for hermes-zettel static site.
Converts Markdown files to HTML and outputs to _site/ directory.
"""
import os
import shutil
import sys
from pathlib import Path
import markdown
from markdown.extensions import codehilite, fenced_code, tables, toc

# Add scripts directory to path for importing generate_context_handoff
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))
import generate_context_handoff

# Configuration
SOURCE_DIR = Path(".")
OUTPUT_DIR = Path("_site")
MARKDOWN_EXTENSIONS = [
    "codehilite",
    "fenced_code",
    "tables",
    "toc",
    "attr_list",
    "def_list",
    "footnotes",
    "md_in_html",
]

# Directories to process for markdown files
CONTENT_DIRS = ["fleeting", "literature", "permanent"]

# Files/directories to copy as-is
STATIC_FILES = ["LICENSE.txt", "README.md", ".gitignore", "_headers", "style.css", "github-markdown.css"]
STATIC_DIRS = []  # Add any static asset directories here (css, js, images)

# Template for directory index pages
DIR_INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Hermes Zettel</title>
    <link rel="stylesheet" href="/style.css">
    <link rel="stylesheet" href="/github-markdown.css">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 2rem; }}
        .markdown-body {{ font-size: 16px; }}
        pre {{ background: #f6f8fa; padding: 1rem; border-radius: 6px; overflow-x: auto; }}
        code {{ background: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; }}
        pre code {{ background: none; padding: 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
        th, td {{ border: 1px solid #d0d7de; padding: 0.5rem; text-align: left; }}
        th {{ background: #f6f8fa; }}
        a {{ color: #0969da; }}
        .toc {{ background: #f6f8fa; padding: 1rem; border-radius: 6px; margin-bottom: 2rem; }}
        .toc ul {{ list-style: none; padding-left: 1.5rem; }}
        .file-list {{ list-style: none; padding: 0; }}
        .file-list li {{ padding: 0.5rem 0; border-bottom: 1px solid #e1e4e8; }}
        .file-list li:last-child {{ border-bottom: none; }}
        .file-list a {{ text-decoration: none; font-weight: 500; }}
        .file-list a:hover {{ text-decoration: underline; }}
        .back-link {{ display: inline-block; margin-bottom: 1.5rem; color: #0969da; text-decoration: none; }}
        .back-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to Home</a>
    <h1>{title}</h1>
    <ul class="file-list">
{file_links}
    </ul>
</body>
</html>
"""

# Template for main index.html
MAIN_INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hermes-Zettel: Dual-Learning Context Ledger</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }}
        header {{
            text-align: center;
            padding: 3rem 0;
        }}
        h1 {{
            font-size: 3rem;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .subtitle {{
            font-size: 1.25rem;
            color: #666;
            margin-bottom: 2rem;
        }}
        .description {{
            font-size: 1.1rem;
            color: #444;
            margin-bottom: 3rem;
            text-align: left;
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .sections {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }}
        .section-card {{
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .section-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        }}
        .section-card h3 {{
            color: #1a1a2e;
            margin-bottom: 1rem;
            font-size: 1.25rem;
        }}
        .section-card p {{
            color: #666;
            margin-bottom: 1rem;
        }}
        .section-card a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        .section-card a:hover {{
            text-decoration: underline;
        }}
        .badge {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }}
        footer {{
            text-align: center;
            padding: 2rem;
            color: #888;
            font-size: 0.9rem;
        }}
        .icon {{
            font-size: 2rem;
            margin-bottom: 1rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Hermes-Zettel</h1>
            <p class="subtitle">Dual-Learning Context Ledger</p>
            <div>
                <span class="badge">Zettelkasten</span>
                <span class="badge">Digital Garden</span>
                <span class="badge">Agent-Human Collaboration</span>
            </div>
        </header>
        
        <div class="description">
            <p><strong>Hermes-Zettel</strong> is a dual-learning context ledger — a digital garden where human and agent insights grow together. Built on Zettelkasten principles, it captures fleeting thoughts, literature notes, and permanent knowledge in a structured, linkable format.</p>
            <p>This garden serves as both a personal knowledge base and a continuity mechanism for AI agents, enabling seamless context handoffs across sessions through automated context-handoff generation.</p>
        </div>

        <div class="sections">
            <div class="section-card">
                <div class="icon">📝</div>
                <h3>Fleeting Notes</h3>
                <p>Quick captures, in-the-moment observations, and transient ideas that may evolve into permanent knowledge.</p>
                <a href="fleeting/">Browse Fleeting →</a>
            </div>
            
            <div class="section-card">
                <div class="icon">📚</div>
                <h3>Literature Notes</h3>
                <p>Structured notes from external sources — papers, articles, books — with key insights extracted and linked.</p>
                <a href="literature/">Browse Literature →</a>
            </div>
            
            <div class="section-card">
                <div class="icon">🌳</div>
                <h3>Permanent Notes</h3>
                <p>Atomized, evergreen knowledge nodes — the core of the Zettelkasten. Each note is self-contained and densely linked.</p>
                <a href="permanent/">Browse Permanent →</a>
            </div>
            
            <div class="section-card">
                <div class="icon">🔄</div>
                <h3>Context Handoffs</h3>
                <p>Automated session continuity files enabling zero-review onboarding for agents. Always up-to-date project state.</p>
                <a href="permanent/context-handoff-latest.html">Latest Handoff →</a>
            </div>
            
            <div class="section-card">
                <div class="icon">📋</div>
                <h3>Session Progress</h3>
                <p>Chronological records of work sessions — human and agent — capturing decisions, discoveries, and next steps.</p>
                <a href="permanent/{latest_session_progress}">Latest Progress →</a>
            </div>
            
            <div class="section-card">
                <div class="icon">🔍</div>
                <h3>Search & Index</h3>
                <p>Navigation aids including category taxonomy, search index, and the baseline anchor for the garden.</p>
                <a href="permanent/search-index.html">Search Index →</a>
            </div>
        </div>

        <footer>
            <p>Generated by <a href="https://github.com/enondev/hermes-zettel" target="_blank">Hermes-Zettel</a> — Dual-learning context ledger for humans and agents</p>
            <p>Deployed via GitHub Pages • Built on Zettelkasten principles</p>
        </footer>
    </div>
</body>
</html>
"""


def convert_markdown_to_html(md_path: Path, output_path: Path) -> None:
    """Convert a single markdown file to HTML."""
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs={
            "codehilite": {"css_class": "highlight", "use_pygments": True},
            "toc": {"anchorlink": True},
        },
    )

    # Wrap in basic HTML structure
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{md_path.stem.replace('-', ' ').title()}</title>
    <link rel="stylesheet" href="/style.css">
    <link rel="stylesheet" href="/github-markdown.css">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 2rem; }}
        .markdown-body {{ font-size: 16px; }}
        pre {{ background: #f6f8fa; padding: 1rem; border-radius: 6px; overflow-x: auto; }}
        code {{ background: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; }}
        pre code {{ background: none; padding: 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
        th, td {{ border: 1px solid #d0d7de; padding: 0.5rem; text-align: left; }}
        th {{ background: #f6f8fa; }}
        a {{ color: #0969da; }}
        .toc {{ background: #f6f8fa; padding: 1rem; border-radius: 6px; margin-bottom: 2rem; }}
        .toc ul {{ list-style: none; padding-left: 1.5rem; }}
    </style>
</head>
<body>
    <article class="markdown-body">
        {html_content}
    </article>
</body>
</html>"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Converted: {md_path} -> {output_path}")


def copy_static_files() -> None:
    """Copy static files and directories to output."""
    for file_name in STATIC_FILES:
        src = SOURCE_DIR / file_name
        if src.exists():
            dst = OUTPUT_DIR / file_name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"Copied: {src} -> {dst}")

    for dir_name in STATIC_DIRS:
        src = SOURCE_DIR / dir_name
        if src.exists():
            dst = OUTPUT_DIR / dir_name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"Copied directory: {src} -> {dst}")


def find_latest_session_progress() -> str:
    """Find the latest session-progress HTML file in the permanent directory."""
    permanent_dir = OUTPUT_DIR / "permanent"
    if not permanent_dir.exists():
        return "session-progress-20261103-2040.html"  # fallback
    
    progress_files = list(permanent_dir.glob("session-progress-*.html"))
    if not progress_files:
        return "session-progress-20261103-2040.html"  # fallback
    
    # Sort by name (which includes timestamp) descending
    progress_files.sort(key=lambda f: f.stem, reverse=True)
    return progress_files[0].name


def generate_directory_index(output_dir: Path, title: str) -> None:
    """Generate an index.html for a directory listing all HTML files in it."""
    html_files = list(output_dir.glob("*.html"))
    subdirs = [d for d in output_dir.iterdir() if d.is_dir()]
    
    if not html_files and not subdirs:
        return
    
    file_links = []
    
    # Add subdirectory links first
    for subdir in sorted(subdirs, key=lambda d: d.name.lower()):
        file_links.append(f'        <li><a href="{subdir.name}/">{subdir.name.title()}/</a></li>')
    
    # Sort files: index.html first (if exists), then alphabetically
    html_files.sort(key=lambda f: (f.name != "index.html", f.name.lower()))
    
    for html_file in html_files:
        if html_file.name == "index.html":
            continue  # Don't link to itself
        # Create a readable title from the filename
        display_name = html_file.stem.replace('-', ' ').replace('_', ' ').title()
        file_links.append(f'        <li><a href="{html_file.name}">{display_name}</a></li>')
    
    if not file_links:
        return
    
    index_content = DIR_INDEX_TEMPLATE.format(
        title=title,
        file_links="\n".join(file_links)
    )
    
    index_path = output_dir / "index.html"
    index_path.write_text(index_content, encoding="utf-8")
    print(f"Generated directory index: {index_path}")


def build() -> None:
    """Main build function."""
    print("Starting build...")

    # Generate context handoff (updates permanent/context-handoff-latest.md)
    print("Generating context handoff...")
    generate_context_handoff.main()

    # Clean output directory
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Process markdown files in content directories
    for content_dir in CONTENT_DIRS:
        src_dir = SOURCE_DIR / content_dir
        if not src_dir.exists():
            print(f"Warning: {src_dir} does not exist, skipping")
            continue

        for md_file in src_dir.rglob("*.md"):
            # Determine output path
            rel_path = md_file.relative_to(SOURCE_DIR)
            output_path = OUTPUT_DIR / rel_path.with_suffix(".html")
            convert_markdown_to_html(md_file, output_path)

    # Copy static files (excluding index.html since we generate it dynamically)
    copy_static_files()

    # Find latest session progress for dynamic link
    latest_session_progress = find_latest_session_progress()
    print(f"Latest session progress: {latest_session_progress}")

    # Generate directory indexes for all content directories
    for content_dir in CONTENT_DIRS:
        output_subdir = OUTPUT_DIR / content_dir
        if output_subdir.exists() and output_subdir.is_dir():
            generate_directory_index(output_subdir, content_dir.title())
    
    # Also generate indexes for literature subdirectories
    for subdir in ["literature/agent", "literature/human"]:
        output_subdir = OUTPUT_DIR / subdir
        if output_subdir.exists() and output_subdir.is_dir():
            generate_directory_index(output_subdir, subdir.replace('/', ' / ').title())

    # Generate dynamic main index.html
    index_path = OUTPUT_DIR / "index.html"
    index_content = MAIN_INDEX_TEMPLATE.format(latest_session_progress=latest_session_progress)
    index_path.write_text(index_content, encoding="utf-8")
    print(f"Generated dynamic index.html: {index_path}")

    print(f"Build complete! Output in {OUTPUT_DIR}")


if __name__ == "__main__":
    build()