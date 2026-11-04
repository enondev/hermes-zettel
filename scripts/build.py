#!/usr/bin/env python3
"""
Build script for hermes-zettel static site.
Converts Markdown files to HTML and outputs to _site/ directory.
"""
import os
import shutil
from pathlib import Path
import markdown
from markdown.extensions import codehilite, fenced_code, tables, toc

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
STATIC_FILES = ["index.html", "LICENSE.txt", "README.md", ".gitignore", "_headers"]
STATIC_DIRS = []  # Add any static asset directories here (css, js, images)


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


def build() -> None:
    """Main build function."""
    print("Starting build...")

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

    # Copy static files
    copy_static_files()

    # Create a simple index.html if it doesn't exist in output
    index_path = OUTPUT_DIR / "index.html"
    if not index_path.exists():
        # Check if there's a source index.html
        if (SOURCE_DIR / "index.html").exists():
            shutil.copy2(SOURCE_DIR / "index.html", index_path)
        else:
            # Generate a basic index
            with open(index_path, "w", encoding="utf-8") as f:
                f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hermes Zettel</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <h1>Hermes Zettel</h1>
    <p>Welcome to the Hermes Zettelkasten.</p>
</body>
</html>""")
            print("Created default index.html")

    print(f"Build complete! Output in {OUTPUT_DIR}")


if __name__ == "__main__":
    build()