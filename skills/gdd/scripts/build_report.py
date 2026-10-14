#!/usr/bin/env python3
"""Build a visual HTML analysis report from a JSON spec.

Usage:
    python build_report.py <spec.json> -o <report.html> [--fragment] [--open]

The spec describes a page as a list of blocks (stats, ratings heatmap, bar
charts, findings, consistency checks, sprint timeline, tables, sources).
See the "Analysis Reports" section of SKILL.md for the format.

By default the output is a standalone HTML document that opens in any browser.
--fragment writes the page without <!doctype>/<html>/<head>/<body>, ready to be
published as a claude.ai Artifact (which adds its own skeleton).

Standard library only.
"""

import argparse
import datetime as _dt
import html
import json
import os
import re
import subprocess
import sys
import webbrowser

# ---------------------------------------------------------------- helpers

def esc(value):
    return html.escape("" if value is None else str(value), quote=True)


_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_CODE = re.compile(r"`([^`]+)`")
_WIKI = re.compile(r"\[\[([^\]]+)\]\]")


def inline(text):
    """Escape text, then allow **bold**, `code`, [[wiki-links]] and [label](https://url)."""
    out = esc(text)
    out = _LINK.sub(lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>', out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _CODE.sub(r"<code>\1</code>", out)
    out = _WIKI.sub(r'<span class="wl">\1</span>', out)
    return out


def paragraphs(text):
    if isinstance(text, list):
        parts = text
    else:
        parts = [p for p in re.split(r"\n\s*\n", str(text or "")) if p.strip()]
    return "".join(f"<p>{inline(p.strip())}</p>" for p in parts)


def num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt(value):
    if value is None:
        return "?"
    return f"{value:.1f}".rstrip("0").rstrip(".") if isinstance(value, float) else str(value)


# Icon + label for every status, so meaning never relies on color alone.
STATUS = {
    "pass":     ("&#10003;", "Pass"),
    "ok":       ("&#10003;", "OK"),
    "fixed":    ("&#8635;", "Fixed"),
    "conflict": ("&#9888;", "Needs decision"),
    "warning":  ("&#9888;", "Warning"),
    "fail":     ("&#10005;", "Fail"),
    "info":     ("i", "Info"),
}

FINDING = {
    "takeaway": ("&#9670;", "Takeaway"),
    "gap":      ("&#9711;", "Market gap"),
    "risk":     ("&#9888;", "Risk"),
    "pattern":  ("&#8801;", "Pattern"),
    "question": ("?", "Open question"),
    "decision": ("&#10003;", "Decision"),
    "note":     ("i", "Note"),
}

# ---------------------------------------------------------------- blocks

def block_text(b):
    return f'<div class="prose">{paragraphs(b.get("body", ""))}</div>'


def block_stats(b):
    tiles = []
    for s in b.get("items", []):
        note = f'<div class="stat-note">{inline(s["note"])}</div>' if s.get("note") else ""
        tiles.append(
            f'<div class="stat"><div class="stat-label">{esc(s.get("label"))}</div>'
            f'<div class="stat-value">{esc(s.get("value"))}</div>{note}</div>'
        )
    return f'<div class="stats">{"".join(tiles)}</div>'


def block_ratings(b):
    dims = b.get("dimensions", [])
    rows = b.get("rows", [])
    scale = int(b.get("scale", 5))
    head = "".join(f'<th scope="col" class="num">{esc(d)}</th>' for d in dims)
    body = []
    for r in rows:
        ratings = r.get("ratings", {})
        evidence = r.get("evidence", {})
        known = [num(ratings.get(d)) for d in dims if num(ratings.get(d)) is not None]
        avg = sum(known) / len(known) if known else None
        cells = []
        for d in dims:
            v = num(ratings.get(d))
            tip = f'{r.get("name")} · {d}: ' + (f"{fmt(v)}/{scale}" if v is not None else "unknown")
            if evidence.get(d):
                tip += f" — {evidence[d]}"
            if v is None:
                cells.append(f'<td class="heat heat-x" title="{esc(tip)}">?</td>')
            else:
                lvl = max(1, min(5, round(v / scale * 5)))
                cells.append(f'<td class="heat heat-{lvl}" title="{esc(tip)}">{fmt(v)}</td>')
        avg_w = 0 if avg is None else avg / scale * 100
        avg_cell = (
            f'<td class="avg"><div class="avg-wrap"><span class="avg-bar"><i style="width:{avg_w:.1f}%"></i></span>'
            f'<span class="avg-num">{fmt(round(avg, 1)) if avg is not None else "?"}</span></div></td>'
        )
        year = f'<span class="year">{esc(r.get("year"))}</span>' if r.get("year") else ""
        sim = f'<div class="sim">{inline(r["similarities"])}</div>' if r.get("similarities") else ""
        hl = ' class="highlight"' if r.get("highlight") else ""
        body.append(
            f'<tr{hl}><th scope="row" class="game"><div class="game-name">{esc(r.get("name"))}{year}</div>{sim}</th>'
            f'{"".join(cells)}{avg_cell}</tr>'
        )
    legend = "".join(
        f'<span class="lg"><i class="heat-{i}"></i>{i}</span>' for i in range(1, 6)
    )
    return (
        f'<div class="scroll"><table class="ratings"><thead><tr><th scope="col">Game</th>{head}'
        f'<th scope="col">Average</th></tr></thead><tbody>{"".join(body)}</tbody></table></div>'
        f'<div class="legend"><span class="lg-label">Rating</span>{legend}'
        f'<span class="lg"><i class="heat-x"></i>? no evidence</span>'
        f'<span class="lg-hint">Hover a cell for its source</span></div>'
    )


def block_bars(b):
    items = b.get("items", [])
    values = [num(i.get("value")) or 0 for i in items]
    top = num(b.get("max")) or (max(values) if values else 1) or 1
    unit = b.get("unit", "")
    rows = []
    for i, v in zip(items, values):
        w = max(0.0, min(100.0, v / top * 100))
        shown = i.get("display") or f"{fmt(v)}{unit}"
        hl = " hl" if i.get("highlight") else ""
        rows.append(
            f'<div class="bar-row{hl}" title="{esc(i.get("label"))}: {esc(shown)}">'
            f'<div class="bar-label">{esc(i.get("label"))}</div>'
            f'<div class="bar-track"><span style="width:{w:.2f}%"></span></div>'
            f'<div class="bar-value">{esc(shown)}</div></div>'
        )
    caption = f'<div class="caption">{inline(b["caption"])}</div>' if b.get("caption") else ""
    return f'<div class="bars">{"".join(rows)}</div>{caption}'


def block_findings(b):
    cards = []
    for f in b.get("items", []):
        kind = f.get("kind", "note")
        icon, label = FINDING.get(kind, FINDING["note"])
        cards.append(
            f'<article class="finding f-{esc(kind)}"><div class="f-kind"><span class="f-icon" aria-hidden="true">{icon}</span>{label}</div>'
            f'<h4>{inline(f.get("title", ""))}</h4><div class="prose">{paragraphs(f.get("body", ""))}</div></article>'
        )
    return f'<div class="findings">{"".join(cards)}</div>'


def block_checks(b):
    items = b.get("items", [])
    counts = {}
    for c in items:
        counts[c.get("status", "info")] = counts.get(c.get("status", "info"), 0) + 1
    summary = "".join(
        f'<span class="pill s-{k}"><span aria-hidden="true">{STATUS.get(k, STATUS["info"])[0]}</span>'
        f'{n} {STATUS.get(k, STATUS["info"])[1]}</span>'
        for k, n in counts.items()
    )
    rows = []
    for c in items:
        k = c.get("status", "info")
        icon, label = STATUS.get(k, STATUS["info"])
        detail = f'<div class="check-detail">{inline(c["detail"])}</div>' if c.get("detail") else ""
        rows.append(
            f'<li class="check s-{esc(k)}"><span class="pill s-{esc(k)}"><span aria-hidden="true">{icon}</span>{label}</span>'
            f'<div class="check-body"><div class="check-label">{inline(c.get("label", ""))}</div>{detail}</div></li>'
        )
    return f'<div class="check-summary">{summary}</div><ul class="checks">{"".join(rows)}</ul>'


def block_timeline(b):
    items = b.get("items", [])
    total = int(b.get("weeks") or max((int(i.get("start", 1)) + int(i.get("length", 1)) - 1 for i in items), default=1))
    unit = b.get("unit", "Week")
    step = max(1, total // 12 + (1 if total % 12 else 0)) if total > 12 else 1
    ticks = "".join(
        f'<span style="left:{(w - 1) / total * 100:.3f}%">{w}</span>' for w in range(1, total + 1, step)
    )
    rows = []
    for i in items:
        start, length = int(i.get("start", 1)), int(i.get("length", 1))
        left = (start - 1) / total * 100
        width = length / total * 100
        cat = esc(i.get("category", "default")).lower()
        tip = f'{i.get("label")}: {unit.lower()} {start}' + (f'–{start + length - 1}' if length > 1 else "")
        rows.append(
            f'<div class="tl-row" title="{esc(tip)}"><div class="tl-label">{esc(i.get("label"))}</div>'
            f'<div class="tl-track"><span class="tl-bar c-{cat}" style="left:{left:.3f}%;width:{width:.3f}%"></span></div></div>'
        )
    cats = sorted({str(i.get("category", "")).lower() for i in items if i.get("category")})
    legend = "".join(f'<span class="lg"><i class="c-{esc(c)}"></i>{esc(c.title())}</span>' for c in cats)
    legend_html = f'<div class="legend">{legend}</div>' if legend else ""
    return (
        f'<div class="scroll"><div class="timeline"><div class="tl-row tl-axis"><div class="tl-label">{esc(unit)}</div>'
        f'<div class="tl-track tl-ticks">{ticks}</div></div>{"".join(rows)}</div></div>{legend_html}'
    )


def block_table(b):
    headers = b.get("headers", [])
    head = "".join(f'<th scope="col">{esc(h)}</th>' for h in headers)
    rows = "".join(
        "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>" for row in b.get("rows", [])
    )
    return f'<div class="scroll"><table class="plain"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'


def block_list(b):
    tag = "ol" if b.get("ordered") else "ul"
    return f'<{tag} class="list">' + "".join(f"<li>{inline(i)}</li>" for i in b.get("items", [])) + f"</{tag}>"


def block_sources(b):
    rows = []
    for s in b.get("items", []):
        label = inline(s.get("label", s.get("url", "")))
        url = s.get("url")
        link = f'<a href="{esc(url)}" target="_blank" rel="noopener">{label}</a>' if url else label
        note = f'<span class="src-note">{inline(s["note"])}</span>' if s.get("note") else ""
        rows.append(f"<li>{link}{note}</li>")
    return f'<ol class="sources">{"".join(rows)}</ol>'


BLOCKS = {
    "text": block_text,
    "stats": block_stats,
    "ratings": block_ratings,
    "bars": block_bars,
    "findings": block_findings,
    "checks": block_checks,
    "timeline": block_timeline,
    "table": block_table,
    "list": block_list,
    "sources": block_sources,
}

# ---------------------------------------------------------------- page

CSS = r"""
/* Layout: one reading column (max 72rem), sections separated by hairlines; data blocks go full column width. */
:root{
  --bg:#f6f7f9; --surface:#ffffff; --fg:#151821; --muted:#5d6475; --faint:#8a90a0;
  --line:#e2e5eb; --accent:#3451d1; --accent-soft:#e8ecfb;
  --h1:#cde2fb; --h2:#9ec5f4; --h3:#6da7ec; --h4:#2a78d6; --h5:#1c5cab; --hx:#eef0f3;
  --h1t:#151821; --h2t:#151821; --h3t:#151821; --h4t:#ffffff; --h5t:#ffffff;
  --good:#0a7d0a; --good-bg:#e6f4e6; --warn:#8a5a00; --warn-bg:#fdf1d6; --bad:#b42c2c; --bad-bg:#fbe7e7;
  --info:#3451d1; --info-bg:#e8ecfb;
  --c-claude:#2a78d6; --c-human:#eb6834; --c-both:#1baf7a; --c-default:#6250d6;
  --font-display:"Bricolage Grotesque", "Segoe UI", system-ui, sans-serif;
  --font-body:"Source Sans 3", "Segoe UI", system-ui, -apple-system, sans-serif;
  --font-data:"JetBrains Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#0e1116; --surface:#161a22; --fg:#e7eaf0; --muted:#a2a9b8; --faint:#737a8a;
  --line:#262c37; --accent:#8ea0f5; --accent-soft:#1f2643;
  --h1:#16263f; --h2:#184f95; --h3:#256abf; --h4:#3987e5; --h5:#86b6ef; --hx:#1d222b;
  --h1t:#c9d6ea; --h2t:#ffffff; --h3t:#ffffff; --h4t:#ffffff; --h5t:#0e1116;
  --good:#4cc94c; --good-bg:#14301a; --warn:#f2b631; --warn-bg:#352a10; --bad:#ef7b7b; --bad-bg:#3a1a1c;
  --info:#8ea0f5; --info-bg:#1f2643;
  --c-claude:#3987e5; --c-human:#d95926; --c-both:#199e70; --c-default:#9085e9;
  color-scheme:dark;
}}
:root[data-theme="dark"]{
  --bg:#0e1116; --surface:#161a22; --fg:#e7eaf0; --muted:#a2a9b8; --faint:#737a8a;
  --line:#262c37; --accent:#8ea0f5; --accent-soft:#1f2643;
  --h1:#16263f; --h2:#184f95; --h3:#256abf; --h4:#3987e5; --h5:#86b6ef; --hx:#1d222b;
  --h1t:#c9d6ea; --h2t:#ffffff; --h3t:#ffffff; --h4t:#ffffff; --h5t:#0e1116;
  --good:#4cc94c; --good-bg:#14301a; --warn:#f2b631; --warn-bg:#352a10; --bad:#ef7b7b; --bad-bg:#3a1a1c;
  --info:#8ea0f5; --info-bg:#1f2643;
  --c-claude:#3987e5; --c-human:#d95926; --c-both:#199e70; --c-default:#9085e9;
  color-scheme:dark;
}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--font-body);font-size:16px;line-height:1.55;margin:0}
.page{max-width:72rem;margin:0 auto;padding-block:40px 64px;
  padding-left:max(16px, env(safe-area-inset-left, 0px));padding-right:max(16px, env(safe-area-inset-right, 0px));
  display:flex;flex-direction:column;gap:40px}
a{color:var(--accent);text-underline-offset:2px}
.wl{color:var(--accent);font-weight:600;white-space:nowrap}
a:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:2px}
code{font-family:var(--font-data);font-size:.88em;background:var(--accent-soft);padding:1px 5px;border-radius:4px}
header.top{display:flex;flex-direction:column;gap:10px;padding-bottom:28px;border-bottom:1px solid var(--line)}
.eyebrow{font-family:var(--font-data);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px 14px}
.eyebrow span+span::before{content:"/";margin-right:14px;color:var(--faint)}
h1{font-family:var(--font-display);font-weight:700;font-size:clamp(30px,5vw,46px);line-height:1.08;letter-spacing:-.02em;margin:0;text-wrap:balance}
.subtitle{font-size:19px;color:var(--muted);max-width:60ch;margin:0}
section.block{display:flex;flex-direction:column;gap:16px;min-width:0}
section.block>h2{font-family:var(--font-display);font-size:24px;font-weight:650;letter-spacing:-.01em;margin:0;text-wrap:balance}
.intro{color:var(--muted);max-width:68ch}
.intro p,.prose p{margin:0 0 .6em}.intro p:last-child,.prose p:last-child{margin-bottom:0}
.prose{max-width:68ch}
.scroll{overflow-x:auto;min-width:0;border:1px solid var(--line);border-radius:10px;background:var(--surface)}
/* stats */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px 18px;display:flex;flex-direction:column;gap:4px;min-width:0}
.stat-label{font-family:var(--font-data);font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
.stat-value{font-family:var(--font-display);font-size:30px;font-weight:700;line-height:1.15}
.stat-note{font-size:14px;color:var(--muted)}
/* ratings heatmap */
table{border-collapse:collapse;width:100%;font-size:14.5px}
.ratings th,.ratings td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}
.ratings thead th{font-family:var(--font-data);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:500;white-space:nowrap;background:var(--surface)}
.ratings th.num{text-align:center}
.ratings tbody tr:last-child>*{border-bottom:0}
.ratings .game{min-width:220px;max-width:340px;font-weight:400}
.game-name{font-weight:650;display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}
.year{font-family:var(--font-data);font-size:12px;color:var(--faint);font-weight:400}
.sim{font-size:13.5px;color:var(--muted);margin-top:2px}
.ratings tr.highlight .game-name::after{content:"Your concept";font-family:var(--font-data);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);border:1px solid var(--accent);border-radius:999px;padding:0 7px}
td.heat{text-align:center;font-family:var(--font-data);font-variant-numeric:tabular-nums;font-weight:600;min-width:56px;border:2px solid var(--surface);border-radius:6px;cursor:default}
.heat-1{background:var(--h1);color:var(--h1t)}.heat-2{background:var(--h2);color:var(--h2t)}.heat-3{background:var(--h3);color:var(--h3t)}
.heat-4{background:var(--h4);color:var(--h4t)}.heat-5{background:var(--h5);color:var(--h5t)}
.heat-x{background:var(--hx);color:var(--faint);font-weight:400}
td.heat:hover{outline:2px solid var(--fg);outline-offset:-2px}
.avg{min-width:130px}
.avg-wrap{display:flex;align-items:center;gap:8px}
.avg-bar{flex:1;height:8px;background:var(--hx);border-radius:4px;overflow:hidden;display:block}
.avg-bar i{display:block;height:100%;background:var(--accent);border-radius:0 4px 4px 0}
.avg-num{font-family:var(--font-data);font-variant-numeric:tabular-nums;font-size:13px;width:2.4em;text-align:right}
.legend{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;font-size:13px;color:var(--muted)}
.lg{display:inline-flex;align-items:center;gap:6px;font-family:var(--font-data);font-size:12px}
.lg i{width:14px;height:14px;border-radius:3px;display:inline-block}
.lg i.c-claude,.lg i.c-human,.lg i.c-both,.lg i.c-default{border-radius:7px;width:22px;height:10px}
.lg-label{font-family:var(--font-data);font-size:11px;letter-spacing:.06em;text-transform:uppercase}
.lg-hint{margin-left:auto;font-style:italic}
/* bars */
.bars{display:flex;flex-direction:column;gap:10px;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:18px}
.bar-row{display:grid;grid-template-columns:minmax(90px,30%) 1fr auto;gap:12px;align-items:center}
.bar-label{font-size:14.5px;overflow-wrap:anywhere}
.bar-track{height:14px;background:var(--hx);border-radius:4px;overflow:hidden}
.bar-track span{display:block;height:100%;background:var(--h4);border-radius:0 4px 4px 0}
.bar-row.hl .bar-track span{background:var(--accent)}
.bar-row.hl .bar-label{font-weight:650}
.bar-value{font-family:var(--font-data);font-variant-numeric:tabular-nums;font-size:13px;color:var(--muted);text-align:right;min-width:4ch}
.caption{font-size:13px;color:var(--muted)}
/* findings */
.findings{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.finding{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px 18px;display:flex;flex-direction:column;gap:6px;min-width:0}
.finding h4{margin:0;font-size:17px;font-weight:650;line-height:1.3}
.finding .prose{font-size:15px;color:var(--muted)}
.f-kind{display:flex;align-items:center;gap:7px;font-family:var(--font-data);font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
.f-icon{width:20px;height:20px;border-radius:50%;display:inline-grid;place-items:center;font-size:11px;font-weight:700}
.f-takeaway .f-icon,.f-pattern .f-icon,.f-note .f-icon{background:var(--info-bg);color:var(--info)}
.f-gap .f-icon,.f-decision .f-icon{background:var(--good-bg);color:var(--good)}
.f-risk .f-icon{background:var(--bad-bg);color:var(--bad)}
.f-question .f-icon{background:var(--warn-bg);color:var(--warn)}
/* checks */
.check-summary{display:flex;flex-wrap:wrap;gap:8px}
.pill{display:inline-flex;align-items:center;gap:6px;font-family:var(--font-data);font-size:12px;font-weight:600;padding:3px 10px;border-radius:999px;white-space:nowrap}
.s-pass,.s-ok{--pc:var(--good);--pb:var(--good-bg)}
.s-fixed,.s-info{--pc:var(--info);--pb:var(--info-bg)}
.s-conflict,.s-warning{--pc:var(--warn);--pb:var(--warn-bg)}
.s-fail{--pc:var(--bad);--pb:var(--bad-bg)}
.pill{color:var(--pc);background:var(--pb)}
.checks{list-style:none;margin:0;padding:0;background:var(--surface);border:1px solid var(--line);border-radius:10px}
.check{display:grid;grid-template-columns:150px 1fr;gap:14px;padding:12px 16px;border-bottom:1px solid var(--line);align-items:start}
.check:last-child{border-bottom:0}
.check .pill{justify-self:start;margin-top:1px}
.check-body{min-width:0}
.check-label{font-weight:600}
.check-detail{font-size:14.5px;color:var(--muted)}
/* timeline */
.timeline{min-width:640px;padding:14px 16px;display:flex;flex-direction:column;gap:6px}
.tl-row{display:grid;grid-template-columns:200px 1fr;gap:12px;align-items:center}
.tl-label{font-size:14px;overflow-wrap:anywhere}
.tl-track{position:relative;height:20px;background:var(--hx);border-radius:4px}
.tl-axis .tl-track{background:none;border-bottom:1px solid var(--line);border-radius:0}
.tl-bar{position:absolute;top:3px;bottom:3px;border-radius:4px;box-shadow:0 0 0 2px var(--surface)}
.c-claude{background:var(--c-claude)}.c-human{background:var(--c-human)}.c-both{background:var(--c-both)}.c-default{background:var(--c-default)}
.tl-axis .tl-label{font-family:var(--font-data);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.tl-ticks span{position:absolute;top:2px;font-family:var(--font-data);font-size:11px;color:var(--muted);font-variant-numeric:tabular-nums}
/* plain table, lists, sources */
.plain th,.plain td{padding:10px 14px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.plain thead th{font-family:var(--font-data);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:500}
.plain tbody tr:last-child td{border-bottom:0}
.list{margin:0;padding-left:1.3em;max-width:68ch;display:flex;flex-direction:column;gap:4px}
.sources{margin:0;padding-left:1.6em;font-size:14px;display:flex;flex-direction:column;gap:6px;color:var(--muted)}
.sources a{overflow-wrap:anywhere}
.src-note{color:var(--muted)}.src-note::before{content:" — "}
footer{font-size:13px;color:var(--faint);border-top:1px solid var(--line);padding-top:16px}
@media (max-width:560px){
  .check{grid-template-columns:1fr;gap:6px}
  .bar-row{grid-template-columns:1fr auto}.bar-row .bar-track{grid-column:1 / -1;grid-row:2}
  .lg-hint{margin-left:0}
}
@media (prefers-reduced-motion:no-preference){a,td.heat{transition:outline-color .15s}}
"""

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700'
    '&family=JetBrains+Mono:wght@400;500;600&family=Source+Sans+3:wght@400;600;700&display=swap">'
)


def render(spec, fragment=False):
    title = spec.get("title", "Analysis Report")
    eyebrow = [x for x in (spec.get("project"), spec.get("kind"), spec.get("date") or _dt.date.today().isoformat()) if x]
    eyebrow_html = "".join(f"<span>{esc(x)}</span>" for x in eyebrow)
    subtitle = f'<p class="subtitle">{inline(spec["subtitle"])}</p>' if spec.get("subtitle") else ""

    sections = []
    for b in spec.get("blocks", []):
        kind = b.get("type")
        fn = BLOCKS.get(kind)
        if fn is None:
            print(f"warning: unknown block type {kind!r} skipped", file=sys.stderr)
            continue
        heading = f'<h2>{inline(b["heading"])}</h2>' if b.get("heading") else ""
        intro = f'<div class="intro">{paragraphs(b["intro"])}</div>' if b.get("intro") else ""
        sections.append(f'<section class="block b-{kind}">{heading}{intro}{fn(b)}</section>')

    footer = spec.get("footer", "Generated by the gdd skill")
    content = (
        f"<title>{esc(title)}</title>\n"
        '<meta name="claude:viewport-fit-sides" content="cover">\n'
        f"{FONTS}\n<style>{CSS}</style>\n"
        f'<main class="page"><header class="top"><div class="eyebrow">{eyebrow_html}</div>'
        f"<h1>{inline(title)}</h1>{subtitle}</header>\n"
        + "\n".join(sections)
        + f"\n<footer>{inline(footer)}</footer></main>\n"
    )
    if fragment:
        return content
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + content.replace("</style>\n<main", "</style>\n</head><body>\n<main", 1)
        + "</body></html>\n"
    )


def open_file(path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception:
        webbrowser.open("file://" + os.path.abspath(path))


def main():
    ap = argparse.ArgumentParser(description="Build a visual HTML analysis report from a JSON spec.")
    ap.add_argument("spec", help="Path to the JSON spec")
    ap.add_argument("-o", "--output", help="Output HTML path (default: spec path with .html)")
    ap.add_argument("--fragment", action="store_true", help="Write an Artifact-ready page with no document skeleton")
    ap.add_argument("--open", action="store_true", help="Open the result in the default browser")
    args = ap.parse_args()

    with open(args.spec, encoding="utf-8") as fh:
        spec = json.load(fh)
    out = args.output or os.path.splitext(args.spec)[0] + ".html"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(render(spec, fragment=args.fragment))
    print(out)
    if args.open:
        open_file(out)


if __name__ == "__main__":
    main()
