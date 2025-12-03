#!/usr/bin/env python3
"""
Build script for DataDive25 GitHub Pages site.

This script converts markdown files from Team_Projects into HTML
and generates the docs directory for GitHub Pages deployment.

Usage:
    python .github/workflows/build.py

Requirements:
    pip install markdown
"""

from pathlib import Path
import markdown


def get_root_dir() -> Path:
    """Get the project root directory."""
    # When run from .github/workflows/, go up two levels
    # When run from project root, stay there
    script_dir = Path(__file__).resolve().parent
    if script_dir.name == "workflows" and script_dir.parent.name == ".github":
        return script_dir.parent.parent
    return Path.cwd()


def get_css_content() -> str:
    """Return the CSS stylesheet content."""
    return """body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  color: #333;
}

h1, h2, h3 {
  color: #2c3e50;
}

code {
  background-color: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

pre {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 5px;
  overflow-x: auto;
}

pre code {
  background-color: transparent;
  padding: 0;
}

blockquote {
  border-left: 4px solid #ddd;
  margin: 0;
  padding-left: 16px;
  color: #666;
}

table {
  border-collapse: collapse;
  width: 100%;
  margin: 20px 0;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

th {
  background-color: #f8f9fa;
  font-weight: bold;
}

a {
  color: #007acc;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}"""


def render_markdown(md_path: Path) -> str:
    """Convert a markdown file to HTML with styling."""
    text = md_path.read_text(encoding="utf-8")
    body_html = markdown.markdown(text, extensions=["fenced_code", "tables"])
    title = f"{md_path.parent.name} - {md_path.stem}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <link rel="stylesheet" href="/Team_Projects/style.css">
</head>
<body>
  <h1>{title}</h1>
  {body_html}
</body>
</html>
"""


def build_team_links(data: list) -> str:
    """Build HTML for team project links."""
    if not data:
        return ""

    lines = ["\n<h2>Team Projects</h2>", "<ul>"]
    for team_name, html_files in data:
        lines.append(f"  <li><strong>{team_name}</strong>")
        lines.append("    <ul>")
        for html_file in html_files:
            title = html_file.replace('.html', '')
            lines.append(f'      <li><a href="/Team_Projects/{team_name}/{html_file}">{title}</a></li>')
        lines.append("    </ul>")
        lines.append("  </li>")
    lines.append("</ul>\n")
    return "\n".join(lines)


def build_site():
    """Main build function to generate the docs directory."""
    root = get_root_dir()
    docs_dir = root / "docs"
    team_src_dir = root / "Team_Projects"
    team_dst_base = docs_dir / "Team_Projects"

    print(f"Building site from: {root}")
    print(f"Output directory: {docs_dir}")

    # Create output directories
    docs_dir.mkdir(exist_ok=True)
    team_dst_base.mkdir(parents=True, exist_ok=True)

    # Copy index.html
    index_src = root / "index.html"
    index_dst = docs_dir / "index.html"
    if index_src.exists():
        index_dst.write_text(index_src.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Copied: {index_src} -> {index_dst}")
    else:
        index_dst.write_text("<!DOCTYPE html><html><body></body></html>", encoding="utf-8")
        print(f"Created default: {index_dst}")

    # Write CSS
    css_path = team_dst_base / "style.css"
    css_path.write_text(get_css_content(), encoding="utf-8")
    print(f"Created: {css_path}")

    # Process team projects
    teams = []
    if team_src_dir.exists():
        for team_dir in sorted(team_src_dir.iterdir()):
            if not team_dir.is_dir() or team_dir.name == "template":
                continue

            dest_dir = team_dst_base / team_dir.name
            dest_dir.mkdir(parents=True, exist_ok=True)

            html_files = []
            for md_file in sorted(team_dir.glob("*.md")):
                output_file = dest_dir / f"{md_file.stem}.html"
                output_file.write_text(render_markdown(md_file), encoding="utf-8")
                html_files.append(output_file.name)
                print(f"Converted: {md_file} -> {output_file}")

            if html_files:
                teams.append((team_dir.name, html_files))

    # Update index.html with team links
    team_links_html = build_team_links(teams)
    if team_links_html:
        current_index = index_dst.read_text(encoding="utf-8")
        if "</body>" in current_index:
            updated_index = current_index.replace("</body>", f"{team_links_html}\n</body>", 1)
        else:
            updated_index = current_index + team_links_html
        index_dst.write_text(updated_index, encoding="utf-8")
        print(f"Updated index.html with {len(teams)} team(s)")

    print("Build complete!")


if __name__ == "__main__":
    build_site()