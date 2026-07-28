"""Render the handout markdown files to print-ready A4 PDFs.

Run:  py -3.11 make_pdfs.py

Edit the .md files, re-run this, and the PDFs regenerate. Uses Chromium via
Playwright so the typography matches what a browser would print.
"""

from __future__ import annotations

import sys
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
HANDOUT = ROOT / "handout"

DOCS = [
    ("participant-handout.md", "Build Your Own Clinical AI Agent — Handout"),
    ("prompt-pack.md", "Clinical AI Agent Prompt Pack"),
    ("safety-checklist.md", "Clinical AI Safety Checklist"),
    ("mcqs-and-feedback.md", "Assessment & Feedback"),
]

CSS = """
@page { size: A4; margin: 16mm 15mm 16mm 15mm; }
* { box-sizing: border-box; }
body {
  font-family: "Segoe UI", Calibri, system-ui, sans-serif;
  font-size: 10.5pt; line-height: 1.5; color: #1b2733; margin: 0;
}
h1 { font-size: 20pt; color: #142C4F; margin: 0 0 4pt; line-height: 1.2;
     border-bottom: 3px solid #0E8F84; padding-bottom: 6pt; }
h2 { font-size: 13.5pt; color: #1D4E89; margin: 16pt 0 6pt;
     page-break-after: avoid; }
h3 { font-size: 11.5pt; color: #142C4F; margin: 12pt 0 4pt;
     page-break-after: avoid; }
p { margin: 0 0 7pt; }
ul, ol { margin: 0 0 8pt; padding-left: 17pt; }
li { margin-bottom: 3pt; }
strong { color: #142C4F; }
hr { border: 0; border-top: 1px solid #d6dee6; margin: 13pt 0; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0 12pt;
        font-size: 9.5pt; page-break-inside: avoid; }
th { background: #142C4F; color: #fff; text-align: left;
     padding: 6pt 7pt; font-size: 9.5pt; }
td { padding: 5.5pt 7pt; border-bottom: 1px solid #e3e9ee; vertical-align: top; }
tr:nth-child(even) td { background: #f4f7f9; }
code { font-family: Consolas, "Courier New", monospace; font-size: 9pt;
       background: #eef2f6; padding: 1pt 3pt; border-radius: 3px; color: #14453d; }
pre { background: #f4f7f9; border-left: 3px solid #0E8F84; padding: 9pt 11pt;
      border-radius: 4px; overflow-x: auto; page-break-inside: avoid;
      margin: 7pt 0 11pt; }
pre code { background: none; padding: 0; font-size: 8.8pt; line-height: 1.45; }
blockquote { border-left: 3px solid #B8760B; background: #fffaf0;
             margin: 9pt 0; padding: 7pt 11pt; color: #6b4a10;
             page-break-inside: avoid; }
blockquote p { margin: 0; }
em { color: #5A6672; }
"""


def render(md_path: Path, title: str) -> str:
    html_body = markdown.markdown(
        md_path.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "sane_lists", "md_in_html"],
    )
    return (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>{title}</title><style>{CSS}</style></head>"
            f"<body>{html_body}</body></html>")


def main() -> int:
    written = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for filename, title in DOCS:
            source = HANDOUT / filename
            if not source.exists():
                print(f"SKIP  {filename} (not found)", file=sys.stderr)
                continue
            page.set_content(render(source, title), wait_until="load")
            out = source.with_suffix(".pdf")
            page.pdf(path=str(out), format="A4", print_background=True,
                     margin={"top": "16mm", "bottom": "16mm",
                             "left": "15mm", "right": "15mm"})
            written.append(out)
            print(f"OK    {out.name}")
        browser.close()

    print(f"\n{len(written)} PDF(s) written to {HANDOUT}")
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())
