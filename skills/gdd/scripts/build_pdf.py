#!/usr/bin/env python3
"""Export an Obsidian-style GDD folder to a single PDF.

Standard library only. Converts the GDD's markdown (wiki-links, callouts,
tables, ASCII diagrams) to one HTML document, then prints it to PDF with a
headless Chromium browser (Chrome, Edge, Chromium or Brave).

Usage:
    python build_pdf.py <GDD folder> [-o OUT.pdf] [--title TITLE]
                        [--include-sprints] [--paper A4|Letter] [--html-only]

Exit codes: 0 = PDF written, 1 = bad input, 2 = no browser found (HTML written
instead so the user can print it manually).
"""

import argparse
import datetime
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SECTION_RE = re.compile(r"^(\d+) - .+\.md$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})\s*([\w+-]*)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
HR_RE = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$")
CALLOUT_RE = re.compile(r"^\[!(\w+)\]([+-]?)\s*(.*)$")

CALLOUT_ALIASES = {
    "summary": "abstract", "tldr": "abstract", "hint": "tip", "important": "tip",
    "check": "success", "done": "success", "help": "question", "faq": "question",
    "caution": "warning", "attention": "warning", "fail": "failure",
    "missing": "failure", "error": "danger", "cite": "quote",
}
CALLOUT_ICONS = {
    "note": "✎", "abstract": "≡", "info": "ℹ", "todo": "☐", "tip": "★",
    "success": "✓", "question": "?", "warning": "⚠", "failure": "✗",
    "danger": "⛔", "bug": "✱", "example": "▸", "quote": "❝",
}


def slug(text):
    text = re.sub(r"[`*_~=\[\]]", "", text).strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "section"


def read_frontmatter(text):
    """Return (frontmatter dict, body) — flat `key: value` pairs only."""
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                m = re.match(r"^([\w-]+):\s*(.*)$", line)
                if m:
                    meta[m.group(1)] = m.group(2).strip().strip("\"'")
            text = text[end + 4:].split("\n", 1)[1] if "\n" in text[end + 4:] else ""
    return meta, text


class Context:
    def __init__(self, vault, notes):
        self.vault = vault
        self.notes = {n.lower(): slug(n) for n in notes}  # note name -> anchor
        self.current = None
        self.current_dir = None
        self.heading_ids = set()
        self._files = None

    def find_file(self, name):
        if self._files is None:
            self._files = {}
            for p in self.vault.rglob("*"):
                if p.is_file() and ".obsidian" not in p.parts:
                    self._files.setdefault(p.name.lower(), p)
        return self._files.get(Path(name).name.lower())

    def link_target(self, target):
        """Resolve 'Note#Heading' to an in-document anchor, or None."""
        note, _, heading = target.partition("#")
        note = note.strip() or self.current
        anchor = self.notes.get(note.lower())
        if anchor is None:
            return None
        if heading:
            return f"{anchor}--{slug(heading.split('#')[-1])}"
        return anchor


# ---------------------------------------------------------------- inline

def render_inline(text, ctx):
    stash = []

    def keep(fragment):
        stash.append(fragment)
        return f"\x00{len(stash) - 1}\x00"

    def code(m):
        return keep(f"<code>{html.escape(m.group(2).strip())}</code>")

    def embed(m):
        target, _, opt = m.group(1).partition("|")
        found = ctx.find_file(target.strip())
        if found and found.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"):
            width = f' width="{opt.strip()}"' if opt.strip().isdigit() else ""
            return keep(f'<img src="{found.resolve().as_uri()}"{width} alt="{html.escape(target)}">')
        return wiki(m)

    def wiki(m):
        target, _, alias = m.group(1).partition("|")
        label = alias.strip() or target.strip().lstrip("#").replace("#", " › ")
        anchor = ctx.link_target(target.strip())
        if anchor:
            return keep(f'<a href="#{anchor}">{html.escape(label)}</a>')
        return keep(f'<span class="missing-link">{html.escape(label)}</span>')

    def image(m):
        src = m.group(2).strip()
        if not re.match(r"^[a-z]+:", src) and ctx.current_dir:
            p = (ctx.current_dir / src).resolve()
            src = p.as_uri() if p.exists() else src
        return keep(f'<img src="{html.escape(src)}" alt="{html.escape(m.group(1))}">')

    def link(m):
        href = m.group(2).strip()
        label = render_inline(m.group(1), ctx)
        if not re.match(r"^[a-z]+:", href):
            target = re.sub(r"\.md$", "", re.sub(r"%20", " ", href.split("/")[-1]))
            anchor = ctx.link_target(target)
            if anchor:
                return keep(f'<a href="#{anchor}">{label}</a>')
        return keep(f'<a href="{html.escape(href)}">{label}</a>')

    text = re.sub(r"(`+)(.+?)\1", code, text)
    text = re.sub(r"!\[\[([^\]]+)\]\]", embed, text)
    text = re.sub(r"\[\[([^\]]+)\]\]", wiki, text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"<br\s*/?>", lambda m: keep("<br>"), text, flags=re.I)

    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\w)__(?=\S)(.+?)(?<=\S)__(?!\w)", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*(?=\S)(.+?)(?<=\S)\*(?![*\w])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![_\w])_(?=\S)(.+?)(?<=\S)_(?![_\w])", r"<em>\1</em>", text)
    text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)
    text = re.sub(r"==(.+?)==", r"<mark>\1</mark>", text)

    while "\x00" in text:
        text = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)
    return text


# ---------------------------------------------------------------- blocks

def indent_of(line):
    return len(line) - len(line.lstrip(" "))


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    cells, buf, depth, in_code = [], "", 0, False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            buf += "|"
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
        elif line.startswith("[[", i):
            depth += 1
        elif line.startswith("]]", i) and depth:
            depth -= 1
        if ch == "|" and not depth and not in_code:
            cells.append(buf.strip())
            buf = ""
        else:
            buf += ch
        i += 1
    cells.append(buf.strip())
    return cells


def starts_block(lines, i):
    line = lines[i]
    nxt = lines[i + 1] if i + 1 < len(lines) else ""
    return bool(
        FENCE_RE.match(line) or HEADING_RE.match(line) or HR_RE.match(line)
        or line.lstrip().startswith(">") or LIST_RE.match(line)
        or ("|" in line and TABLE_SEP_RE.match(nxt))
    )


def render_blocks(lines, ctx):
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        m = FENCE_RE.match(line)
        if m:
            fence, lang = m.group(1), m.group(2)
            body = []
            i += 1
            while i < n and not lines[i].strip().startswith(fence):
                body.append(lines[i])
                i += 1
            i += 1
            cls = f' class="lang-{lang}"' if lang else ""
            out.append(f"<pre{cls}><code>{html.escape(chr(10).join(body))}</code></pre>")
            continue

        m = HEADING_RE.match(line)
        if m:
            level, text = len(m.group(1)), m.group(2)
            hid = f"{ctx.notes.get(ctx.current.lower(), slug(ctx.current))}--{slug(text)}"
            base, k = hid, 2
            while hid in ctx.heading_ids:
                hid, k = f"{base}-{k}", k + 1
            ctx.heading_ids.add(hid)
            out.append(f'<h{level} id="{hid}">{render_inline(text, ctx)}</h{level}>')
            i += 1
            continue

        if HR_RE.match(line):
            out.append("<hr>")
            i += 1
            continue

        if line.lstrip().startswith(">"):
            body = []
            while i < n and lines[i].lstrip().startswith(">"):
                body.append(re.sub(r"^\s*> ?", "", lines[i]))
                i += 1
            cm = CALLOUT_RE.match(body[0].strip())
            if cm:
                kind = cm.group(1).lower()
                kind = CALLOUT_ALIASES.get(kind, kind)
                title = cm.group(3) or cm.group(1).capitalize()
                icon = CALLOUT_ICONS.get(kind, "•")
                inner = render_blocks(body[1:], ctx)
                out.append(
                    f'<div class="callout callout-{kind}"><div class="callout-title">'
                    f"{icon} {render_inline(title, ctx)}</div>{inner}</div>"
                )
            else:
                out.append(f"<blockquote>{render_blocks(body, ctx)}</blockquote>")
            continue

        if "|" in line and i + 1 < n and TABLE_SEP_RE.match(lines[i + 1]):
            head = split_row(line)
            aligns = []
            for cell in split_row(lines[i + 1]):
                cell = cell.strip()
                if cell.startswith(":") and cell.endswith(":"):
                    aligns.append("center")
                elif cell.endswith(":"):
                    aligns.append("right")
                else:
                    aligns.append("")
            i += 2
            rows = []
            while i < n and lines[i].strip() and "|" in lines[i]:
                rows.append(split_row(lines[i]))
                i += 1

            def cell_html(tag, cells):
                parts = []
                for j in range(len(head)):
                    text = cells[j] if j < len(cells) else ""
                    a = aligns[j] if j < len(aligns) else ""
                    style = f' style="text-align:{a}"' if a else ""
                    parts.append(f"<{tag}{style}>{render_inline(text, ctx)}</{tag}>")
                return "<tr>" + "".join(parts) + "</tr>"

            body_html = "".join(cell_html("td", r) for r in rows)
            out.append(f"<table><thead>{cell_html('th', head)}</thead><tbody>{body_html}</tbody></table>")
            continue

        m = LIST_RE.match(line)
        if m:
            i = render_list(lines, i, ctx, out)
            continue

        para = [line.strip()]
        i += 1
        while i < n and lines[i].strip() and not starts_block(lines, i):
            para.append(lines[i].strip())
            i += 1
        # Obsidian treats single newlines as line breaks by default.
        out.append("<p>" + "<br>".join(render_inline(p, ctx) for p in para) + "</p>")
    return "\n".join(out)


def render_list(lines, i, ctx, out):
    n = len(lines)
    first = LIST_RE.match(lines[i])
    base = len(first.group(1))
    ordered = first.group(2)[0].isdigit()
    start = int(re.match(r"\d+", first.group(2)).group()) if ordered else 1
    items = []
    while i < n:
        m = LIST_RE.match(lines[i])
        if not m or len(m.group(1)) != base or m.group(2)[0].isdigit() != ordered:
            break
        width = base + len(m.group(2)) + 1
        content = [m.group(3)]
        i += 1
        while i < n:
            line = lines[i]
            if not line.strip():
                j = i + 1
                while j < n and not lines[j].strip():
                    j += 1
                if j < n and indent_of(lines[j]) > base:
                    content.extend([""] * (j - i))
                    i = j
                    continue
                break
            if indent_of(line) > base:
                cut = min(indent_of(line), width)
                content.append(line[cut:])
                i += 1
            elif not LIST_RE.match(line) and not starts_block(lines, i):
                content.append(line.strip())  # lazy continuation
                i += 1
            else:
                break
        items.append(content)

    parts = []
    for content in items:
        lead = []
        while content and content[0].strip() and not (lead and starts_block(content, 0)):
            lead.append(content.pop(0).strip())
        text = " ".join(lead)
        task = re.match(r"^\[([ xX])\]\s+(.*)$", text)
        if task:
            box = "☑" if task.group(1).lower() == "x" else "☐"
            text_html = f'<span class="task">{box}</span> {render_inline(task.group(2), ctx)}'
        else:
            text_html = render_inline(text, ctx)
        rest = render_blocks(content, ctx) if any(c.strip() for c in content) else ""
        parts.append(f"<li>{text_html}{rest}</li>")
    tag = "ol" if ordered else "ul"
    start_attr = f' start="{start}"' if ordered and start != 1 else ""
    out.append(f"<{tag}{start_attr}>" + "".join(parts) + f"</{tag}>")
    return i


# ---------------------------------------------------------------- document

CSS = """
@page { size: %(paper)s; margin: 18mm 16mm 20mm 16mm;
        @bottom-center { content: counter(page); font: 9pt sans-serif; color: #777; } }
* { box-sizing: border-box; }
body { font: 10.5pt/1.5 "Segoe UI", -apple-system, "Helvetica Neue", Arial, sans-serif;
       color: #1f2328; margin: 0; width: %(width)s; }
.cover { height: %(cover)s; display: flex; flex-direction: column; justify-content: center;
         align-items: center; text-align: center; page-break-after: always; }
.cover .kicker { letter-spacing: .3em; text-transform: uppercase; color: #6e7781; font-size: 11pt; }
.cover h1 { font-size: 34pt; margin: 12px 0 18px; border: 0; }
.cover .meta { color: #57606a; font-size: 10.5pt; }
.toc { page-break-after: always; }
.toc ol { list-style: none; padding: 0; }
.toc li { display: flex; gap: 8px; padding: 5px 0; border-bottom: 1px dotted #d0d7de; }
.toc li a { flex: 1; color: #1f2328; text-decoration: none; }
.toc .badge { font-size: 8.5pt; color: #57606a; }
section.gdd-section { page-break-before: always; }
.section-meta { color: #6e7781; font-size: 9pt; margin: -6px 0 14px; }
h1, h2, h3, h4 { line-height: 1.25; page-break-after: avoid; break-after: avoid; }
h1 { font-size: 22pt; border-bottom: 2px solid #1f2328; padding-bottom: 6px; }
h2 { font-size: 15pt; border-bottom: 1px solid #d0d7de; padding-bottom: 4px; margin-top: 26px; }
h3 { font-size: 12.5pt; margin-top: 20px; }
h4 { font-size: 11pt; }
a { color: #0969da; text-decoration: none; }
.missing-link { color: #8c959f; border-bottom: 1px dashed #8c959f; }
code { font: 9pt Consolas, "SF Mono", Menlo, monospace; background: #f3f4f6;
       padding: 1px 4px; border-radius: 3px; }
pre { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 5px; padding: 10px 12px;
      white-space: pre; overflow: hidden; break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 8.5pt; line-height: 1.3; }
table { border-collapse: collapse; width: 100%%; margin: 12px 0; font-size: 9.5pt; }
th, td { border: 1px solid #d0d7de; padding: 5px 8px; vertical-align: top; text-align: left; }
th { background: #f3f4f6; }
tr { break-inside: avoid; }
blockquote { margin: 12px 0; padding: 2px 14px; border-left: 4px solid #d0d7de; color: #57606a; }
.callout { margin: 12px 0; padding: 8px 14px; border-radius: 5px; border-left: 4px solid;
           break-inside: avoid; }
.callout-title { font-weight: 600; margin-bottom: 2px; }
.callout p { margin: 4px 0; }
.callout-note, .callout-info, .callout-todo { border-color: #0969da; background: #ddf4ff; }
.callout-abstract, .callout-example { border-color: #8250df; background: #fbefff; }
.callout-tip, .callout-success { border-color: #1a7f37; background: #dafbe1; }
.callout-question { border-color: #bf8700; background: #fff8c5; }
.callout-warning { border-color: #bc4c00; background: #fff1e5; }
.callout-danger, .callout-failure, .callout-bug { border-color: #cf222e; background: #ffebe9; }
.callout-quote { border-color: #8c959f; background: #f6f8fa; }
.task { font-size: 11pt; }
img { max-width: 100%%; }
mark { background: #fff8c5; }
hr { border: 0; border-top: 1px solid #d0d7de; margin: 18px 0; }
"""

# Page width minus margins, so on-screen layout (used to measure diagrams)
# matches the printed page.
PRINT_WIDTH = {"A4": "178mm", "Letter": "183.9mm"}
COVER_HEIGHT = {"A4": "250mm", "Letter": "232mm"}

# Shrinks wide ASCII diagrams to fit the page instead of cutting them off.
FIT_SCRIPT = """
document.querySelectorAll('pre').forEach(function (pre) {
  var code = pre.querySelector('code'), size = 8.5;
  while (pre.scrollWidth > pre.clientWidth && size > 5) {
    size -= 0.5; code.style.fontSize = size + 'pt';
  }
  if (pre.scrollWidth > pre.clientWidth) pre.style.whiteSpace = 'pre-wrap';
});
"""


def collect_notes(gdd, include_sprints):
    notes = sorted(
        (p for p in gdd.iterdir() if p.is_file() and SECTION_RE.match(p.name)),
        key=lambda p: (int(SECTION_RE.match(p.name).group(1)), p.name.lower()),
    )
    sprint_dir = gdd / "sprint-plan"
    if include_sprints and sprint_dir.is_dir():
        notes += sorted(p for p in sprint_dir.iterdir() if p.suffix == ".md")
    return notes


def build_html(gdd, title, paper, include_sprints):
    paths = collect_notes(gdd, include_sprints)
    if not paths:
        raise SystemExit(f"No 'NN - Name.md' sections found in {gdd}")
    ctx = Context(gdd, [p.stem for p in paths])
    loaded = []
    for p in paths:
        meta, body = read_frontmatter(p.read_text(encoding="utf-8"))
        loaded.append((p, meta, body))

    index_meta = next((m for p, m, _ in loaded if p.stem.startswith("00")), {})
    toc, sections = [], []
    for p, meta, body in loaded:
        ctx.current, ctx.current_dir = p.stem, p.parent
        anchor = ctx.notes[p.stem.lower()]
        lines = body.expandtabs(4).splitlines()
        # The note's first H1 becomes the section title.
        heading = p.stem
        for k, line in enumerate(lines):
            if line.strip():
                h = HEADING_RE.match(line)
                if h and len(h.group(1)) == 1:
                    heading = h.group(2)
                    del lines[k]
                break
        bits = [b for b in (
            meta.get("status", "").capitalize(),
            f"v{meta['version']}" if meta.get("version") else "",
            f"Updated {meta['updated']}" if meta.get("updated") else "",
        ) if b]
        badge = " · ".join(bits)
        toc.append(
            f'<li><a href="#{anchor}">{render_inline(heading, ctx)}</a>'
            f'<span class="badge">{html.escape(badge)}</span></li>'
        )
        meta_html = f'<div class="section-meta">{html.escape(badge)}</div>' if badge else ""
        sections.append(
            f'<section class="gdd-section" id="{anchor}"><h1>{render_inline(heading, ctx)}</h1>'
            f"{meta_html}{render_blocks(lines, ctx)}</section>"
        )

    today = datetime.date.today().isoformat()
    version = index_meta.get("version", "")
    cover_meta = " · ".join(b for b in (f"Version {version}" if version else "", f"Exported {today}") if b)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{html.escape(title)} — Game Design Document</title>
<style>{CSS % {"paper": paper, "width": PRINT_WIDTH[paper], "cover": COVER_HEIGHT[paper]}}</style></head><body>
<div class="cover"><div class="kicker">Game Design Document</div>
<h1>{html.escape(title)}</h1><div class="meta">{html.escape(cover_meta)}</div></div>
<nav class="toc"><h1>Contents</h1><ol>{''.join(toc)}</ol></nav>
{''.join(sections)}
<script>{FIT_SCRIPT}</script>
</body></html>"""


def find_browser():
    env = os.environ.get("CHROME_PATH")
    if env and Path(env).exists():
        return env
    candidates = []
    if sys.platform == "win32":
        for root in filter(None, (os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"),
                                  os.environ.get("LOCALAPPDATA"))):
            candidates += [
                Path(root, "Google/Chrome/Application/chrome.exe"),
                Path(root, "Microsoft/Edge/Application/msedge.exe"),
                Path(root, "BraveSoftware/Brave-Browser/Application/brave.exe"),
                Path(root, "Chromium/Application/chrome.exe"),
            ]
    elif sys.platform == "darwin":
        for app in ("Google Chrome", "Microsoft Edge", "Chromium", "Brave Browser"):
            candidates.append(Path(f"/Applications/{app}.app/Contents/MacOS/{app}"))
    for c in candidates:
        if c.exists():
            return str(c)
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
                 "microsoft-edge", "brave-browser", "chrome", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    return None


def print_pdf(browser, html_path, pdf_path):
    with tempfile.TemporaryDirectory() as profile:
        cmd = [
            browser, "--headless=new", "--disable-gpu", "--no-first-run",
            f"--user-data-dir={profile}", "--no-pdf-header-footer",
            "--print-to-pdf-no-header", f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    return pdf_path.exists() and pdf_path.stat().st_size > 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("gdd", type=Path, help="the GDD folder (contains '00 - Index.md')")
    ap.add_argument("-o", "--output", type=Path, help="PDF path (default: <GDD>/exports/<Title> - GDD.pdf)")
    ap.add_argument("--title", help="game title (default: the GDD folder's parent folder name)")
    ap.add_argument("--include-sprints", action="store_true", help="append the sprint-plan/ notes")
    ap.add_argument("--paper", default="A4", choices=["A4", "Letter"])
    ap.add_argument("--html-only", action="store_true", help="write the HTML and skip the PDF step")
    args = ap.parse_args()

    gdd = args.gdd.resolve()
    if not gdd.is_dir():
        print(f"Not a folder: {gdd}", file=sys.stderr)
        return 1
    title = args.title or (gdd.parent.name if gdd.name.lower() == "gdd" else gdd.name)
    pdf_path = (args.output or gdd / "exports" / f"{title} - GDD.pdf").resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    html_path = pdf_path.with_suffix(".html")
    html_path.write_text(build_html(gdd, title, args.paper, args.include_sprints), encoding="utf-8")

    if args.html_only:
        print(f"HTML written: {html_path}")
        return 0
    browser = find_browser()
    if not browser:
        print(f"No Chrome/Edge/Chromium found. HTML written to {html_path} — open it in a browser "
              "and use Print > Save as PDF, or set CHROME_PATH.", file=sys.stderr)
        return 2
    if pdf_path.exists():
        pdf_path.unlink()
    if not print_pdf(browser, html_path, pdf_path):
        print(f"Browser failed to print. HTML kept at {html_path}.", file=sys.stderr)
        return 2
    html_path.unlink()
    print(f"PDF written: {pdf_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
