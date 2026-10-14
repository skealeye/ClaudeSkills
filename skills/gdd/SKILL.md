---
name: gdd
description: Use when creating, updating, or maintaining a Game Design Document (GDD) — covers concept research, genre analysis, competitive analysis with visual web reports, project setup, GitHub repo creation, Obsidian-compatible section authoring, Obsidian installation, PDF export, and version control
---

# Game Design Document

## Overview

Standardized workflow for creating and maintaining Game Design Documents. Enforces consistent structure, Obsidian-compatible markdown, automated GitHub version control, parallel subagent authoring with consistency checks, and sprint planning. The GDD can be read in Obsidian, exported to PDF, or both. Every analysis is also shown to the user as a clean visual web page (see **Analysis Reports**).

**The user owns the design.** Claude researches, structures, drafts and proposes. It does not silently make design decisions the user hasn't made — unknowns become open questions (see **Open Questions** below).

## When to Use

- User asks to create a GDD, game design document, or game spec
- User wants to update or maintain an existing GDD project
- User wants to export a GDD to PDF or open it in Obsidian
- Invoked via `/gdd`

## Prerequisites

Before any GitHub operations, verify:

1. `gh --version` — gh CLI installed
2. `gh auth status` — authenticated
3. `git --version` — git available

If `gh` is unavailable or not authenticated:
- Offer to guide through `gh auth login`
- Or work in local-only mode (local git, no remote push)

If repo creation fails, present the error and let user retry or connect to existing repo.

PDF export additionally needs Python 3 and Chrome, Edge, Chromium or Brave — checked only if the user picks PDF (see **Phase 2: Reading Setup**).

---

## Phase 1: Concept & Research

Ask: *"Do you already have a game concept, or would you like help brainstorming one?"*

If the user already has a detailed concept and wants to skip research, collect the **Key Details** below and proceed to **Phase 2**. Note in `02 - Market Research` that research was skipped.

### Path A — User Has an Idea

1. Ask them to describe their game concept (elevator pitch, core mechanics, theme)
2. Identify the primary genre(s) it falls into
3. Proceed to **Genre Research** below

### Path B — User Wants Help Brainstorming

1. Ask: *"What genre or genres are you interested in?"*
   - Offer common genres: Action, RPG, Roguelike, Strategy, Simulation, Survival, Horror, Puzzle, Platformer, FPS, MOBA, Card Game, Extraction Shooter, Idle/Incremental, Narrative/Adventure, Rhythm, Sports/Racing, etc.
   - Allow multiple genre selections for hybrid concepts
2. Proceed to **Genre Research** below
3. After presenting research, collaborate with the user to shape a concept from the findings

### Genre Research — Competitive Analysis

For each selected genre, use `WebSearch` to find the most popular and notable titles. Present findings in a comparison table:

```markdown
## Competitive Analysis: <Genre>

| Game | Year | Similarities | Popularity | Userbase | Commercial | Critical Reception | Community | Replayability | Streaming |
|------|:----:|-------------|:----------:|:--------:|:----------:|:-----------------:|:---------:|:-------------:|:---------:|
| Game Title | 2023 | Shared mechanics, themes | ★★★★☆ | ★★★☆☆ | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★★ | ★★★★☆ |
```

**Rating dimensions (1–5 stars, or `?` when unknown):**

| Dimension | What to Evaluate | Good Evidence |
|-----------|-----------------|---------------|
| Popularity | Market presence, sales volume, brand recognition | Reported sales, Steam review count, wishlist rankings |
| Userbase | Active players, retention, growth trend | SteamDB current / all-time peak players, publisher-reported MAU |
| Commercial | Revenue, commercial success | Publisher earnings reports, reported revenue, Gamalytic / VG Insights estimates |
| Critical Reception | Critic and user scores | Metacritic / OpenCritic score, Steam review % |
| Community | Modding, Discord/forum activity, wikis | Discord member count, Nexus / Workshop mod counts, subreddit size |
| Replayability | Session variety, procedural content, endgame depth | Reviews, design analysis |
| Streaming | Twitch/YouTube presence | TwitchTracker / SullyGnome average viewers |

> [!WARNING] No invented numbers
> Every star rating must be backed by something found in research. If no evidence was found, use `?` — never guess. Below each table, list the key figure and source URL behind each rating (e.g. *"Userbase ★★★★☆ — 98k all-time peak, SteamDB"*). Label estimates as estimates.

**Research guidelines:**
- Find 5–8 comparable titles per genre
- Prioritize games from the last 5 years, but include landmark older titles if highly relevant
- Note which mechanics, themes, or design patterns appear across multiple successful titles
- Highlight market gaps — underserved niches or mechanics no current title handles well

### Concept Confirmation

After research, summarize:
1. **Key takeaways** — what works in this genre, common patterns
2. **Market gaps** — opportunities the user's concept could fill
3. **Risks** — oversaturated mechanics or declining trends

Build the **Market Research** analysis report (see **Analysis Reports**): stat tiles, a `ratings` heatmap per genre (with each rating's evidence as its tooltip), `findings` for takeaways / gaps / risks, and `sources`. Show it to the user, then give a short text summary in chat.

Ask: *"Based on this research, are you happy with your concept direction? Any adjustments before we set up the project?"*

### Key Details

Before leaving Phase 1, collect (ask only for what the user hasn't already said; "undecided" is a valid answer and becomes an open question):

| Detail | Example |
|--------|---------|
| Game title (working title is fine) | Ember Tide |
| Genre(s) | Extraction roguelite |
| Platform(s) | PC (Steam), later consoles |
| Engine | Godot 4 / Unity / Unreal / undecided |
| Target audience | Mid-core co-op players, 18–35 |
| Player count | 1–3 co-op |
| Business model | Premium $20 / F2P / undecided |
| Team size | Solo / 3 people |

Keep the research tables, sources, takeaways and these details — they are written into the repo in Phase 2. Do not let them exist only in chat.

---

## Phase 2: Project Setup

Ask: *"Create a new private GitHub repo, or connect to an existing one?"*

**New repo:**
1. Derive a repo name from the title: lowercase, spaces → hyphens, strip anything other than letters, digits, `-` and `_` (`Ember Tide: Rising!` → `ember-tide-rising`). Confirm it with the user.
2. `gh repo create <repo-name> --private --clone`
3. Scaffold structure

**Existing repo:**
1. Prompt for repo URL
2. Clone or confirm local path
3. Validate/create GDD folder

Detect the default branch with `git symbolic-ref --short HEAD` (or `gh repo view --json defaultBranchRef`) and use it for all commits — don't assume `main`.

### Scaffold

```
<repo-root>/
├── README.md
├── .gitignore
└── <GameTitle>/
    └── GDD/
        ├── .obsidian/
        │   └── app.json
        ├── 00 - Index.md
        ├── 02 - Market Research.md
        └── 27 - Decision Log.md
```

`.gitignore`:
```
# Obsidian per-user state
.obsidian/workspace*.json
.obsidian/cache
.trash/
```

`.obsidian/app.json` (keeps wiki-links correct when notes are renamed in Obsidian):
```json
{ "alwaysUpdateLinks": true }
```

### README.md Template

```markdown
# <GameTitle>

## Overview
<Elevator pitch — 2-3 sentences>

## Key Details
| Field | Value |
|-------|-------|
| Genre | <genre> |
| Platform | <platforms> |
| Engine | <engine> |
| Target Audience | <audience> |
| Business Model | <model> |
| Team Size | <solo/team size> |

## Game Design Document
The full GDD is located in [`<GameTitle>/GDD/`](<GameTitle>/GDD/00%20-%20Index.md).

**How to read it:**
- **Obsidian (recommended):** install from [obsidian.md](https://obsidian.md/download), choose *Open folder as vault*, and select the `<GameTitle>/GDD` folder.
- **PDF:** see [`<GameTitle>/GDD/exports/`](<GameTitle>/GDD/exports/) <!-- only if PDF export is enabled -->
- **GitHub:** pages render here, but `[[wiki-links]]` between sections are not clickable on GitHub.
```

### 00 - Index.md Template

```markdown
---
title: "00 - Index"
tags: [gdd, index]
status: draft
version: 0.1
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
export_pdf: <true|false>
---

# <GameTitle> — Game Design Document

> [!INFO] Design Authority
> This is the central hub for all GDD sections. All design documents are linked below.

---

## Quick Reference

| Field | Value |
|-------|-------|
| Title | <GameTitle> |
| Genre | <genre> |
| Platform | <platforms> |
| Engine | <engine> |
| Players | <player count> |
| Business Model | <model> |

## Document Map

| # | Section | Status | Version | Description |
|---|---------|--------|---------|-------------|
| 01 | [[01 - Game Overview]] | draft | 0.1 | Design pillars, pitch, audience |
| ... | ... | ... | ... | ... |

## Open Questions

| Question | Raised In | Status |
|----------|-----------|--------|
| <question> | [[NN - Section#Heading]] | open |

## How to Use This Document

- **Navigation:** Click `[[wiki-links]]` to jump between sections
- **Callouts:** `[!DANGER]` = hard rules, `[!WARNING]` = pitfalls, `[!TIP]` = rationale, `[!NOTE]` = context, `[!QUESTION]` = open questions
- **Status:** `draft` → `review` → `final`
- **Decisions:** the reasoning behind design changes is recorded in [[27 - Decision Log]]
```

### 02 - Market Research

Write it now from the Phase 1 results, using the standard section template (Phase 4): competitive analysis tables, sources list, common patterns, market gaps, risks. If research was skipped, write a short note saying so with a `[!QUESTION]` callout suggesting it be done later.

### 27 - Decision Log

Create it with the standard frontmatter, a short intro, and one entry per decision already made in Phase 1 (concept direction, genre, platform, engine, business model). Entry template — newest first:

```markdown
## <YYYY-MM-DD> — <Decision title>

- **Decision:** <what was decided>
- **Alternatives considered:** <options rejected>
- **Rationale:** <why>
- **Affects:** [[NN - Section]], [[NN - Section]]
```

### Reading Setup — Obsidian and/or PDF

Ask: *"How would you like to read the GDD? Obsidian (best — clickable links, graph view, live editing), a PDF export, or both?"*

Record the answer as `export_pdf: true|false` in `00 - Index.md` frontmatter so later sessions know whether to rebuild the PDF.

**If Obsidian (or both):**

1. Check whether it's installed:

   | OS | Check |
   |----|-------|
   | Windows | `Test-Path "$env:LOCALAPPDATA\Programs\Obsidian\Obsidian.exe"` or `winget list --id Obsidian.Obsidian` |
   | macOS | `test -d /Applications/Obsidian.app` |
   | Linux | `flatpak info md.obsidian.Obsidian`, `snap list obsidian`, or `command -v obsidian` |

2. If missing, ask permission, then install:

   | OS | Install |
   |----|---------|
   | Windows | `winget install --id Obsidian.Obsidian -e --accept-source-agreements --accept-package-agreements` |
   | macOS | `brew install --cask obsidian` |
   | Linux | `flatpak install -y flathub md.obsidian.Obsidian` (or `sudo snap install obsidian --classic`) |

   If the package manager is unavailable or the install fails, point the user to <https://obsidian.md/download>.

3. Tell the user how to open the vault (first time only — Obsidian has no command to register a vault):
   1. Launch Obsidian
   2. Choose **Open folder as vault**
   3. Select `<repo-root>/<GameTitle>/GDD`
   4. If prompted, choose **Trust author and enable plugins** (the vault ships no plugins)

   After that, the vault can be reopened with the URI `obsidian://open?vault=GDD` (Windows: `start "" "obsidian://open?vault=GDD"`, macOS: `open "obsidian://open?vault=GDD"`, Linux: `xdg-open "obsidian://open?vault=GDD"`).

**If PDF (or both):** check `python --version` (or `python3`) and that the export script can find a browser. If neither Chrome, Edge, Chromium nor Brave is installed, offer to install one or fall back to HTML that the user prints with any browser. The first PDF is built at the end of Phase 5 (see **PDF Export**).

Commit: `"Initialize GDD structure for <GameTitle>"` → push.

---

## Phase 3: Section Selection

1. Present the catalog from `section-catalog.md`, grouped (Foundation, Narrative, Gameplay Systems, Presentation, Production & Business)
2. Pre-select "Always" sections and any that clearly match the genre and Key Details (e.g. combat game → `10 - Combat`, co-op → `15 - Multiplayer & Social`)
3. Ask the user to confirm, add, or remove
4. If the game has a distinctive core system, name `17 - Signature Mechanic` after it (`17 - Card System`, `17 - Extraction`). If there are several, use `17` for the main one and custom numbers for the rest
5. Allow custom sections, numbered from **30**

Numbers are stable IDs: skipped sections leave gaps, and numbers are never reused or renumbered.

---

## Phase 4: Section Authoring

### File Naming

`NN - Section Name.md` (zero-padded, spaces around dash). Avoid `#`, `|`, `[`, `]`, `^` and `:` in names — they break wiki-links.

### Mandatory Template

**Frontmatter:**
```yaml
---
title: "NN - Section Name"
tags: [gdd, <topic-tags>]
status: draft
version: 0.1
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
parent: "[[00 - Index]]"
related:
  - "[[cross-referenced-sections]]"
---
```

**Status values:** `draft` → `review` → `final`
**Version:** Increment minor on each change (0.1 → 0.2). Set 1.0 when the user approves it as `final`. Editing a `final` section bumps to 1.1 and sets status back to `review` until the user re-approves.
**Updated:** Today's date on every change.
**Related:** Maintained by the orchestrator (not subagents) from the `[[wiki-links]]` in the body during the consistency review.

**Body structure:**
1. `# NN - Section Name`
2. Design authority callout (below)
3. `---` divider
4. H2 sections: philosophy/overview → core mechanics → edge cases
5. Tables for structured data
6. ASCII diagrams in code blocks for flows/layouts (keep them under ~100 characters wide)
7. Callouts (table below)
8. `[[wiki-links]]` with optional heading anchors (`[[10 - Combat#Damage Model]]`)
9. `## Open Questions` (if any) and `## Related Documents` footer

**Design authority callout** — states what this section owns and what it defers to:

```markdown
> [!INFO] Design Authority
> This document is the source of truth for **<scope, e.g. damage, status effects and weapon stats>**.
> Pillars and audience defer to [[01 - Game Overview]]; names and shared numbers defer to [[03 - Glossary & Design Constants]].
```

### Callouts

| Callout | Use For |
|---------|---------|
| `> [!DANGER]` | Hard design rules that must not be broken |
| `> [!WARNING]` | Pitfalls and known risks |
| `> [!TIP]` | Rationale — why a design choice was made |
| `> [!NOTE]` | Context and background |
| `> [!QUESTION]` | Open questions awaiting a decision |
| `> [!INFO]` | Design authority (top of every section) |

Don't use `[!IMPORTANT]` — Obsidian renders it identically to `[!TIP]`, so rules and rationale become indistinguishable.

### Open Questions

When a design detail is needed but the user hasn't decided it, **do not invent a final answer.** Instead:

```markdown
> [!QUESTION] Run length
> 20 or 30 minutes? **Proposed:** 25 minutes — fits the extraction timer in [[17 - Extraction]].
```

A proposal is welcome; it must be labelled as a proposal. Placeholder numbers (e.g. balance values) are fine if marked `(placeholder)`. The orchestrator copies every `[!QUESTION]` into the Index's Open Questions table.

### Glossary & Design Constants

`03 - Glossary & Design Constants` is the single source for names and shared numbers (currency names, stat names, rarity tiers, max party size, session length). Every section uses those exact names and values, and links to the glossary rather than restating numbers that live there.

---

## Phase 5: Parallel Subagent Dispatch

### Orchestrator Pattern

Subagents do NOT touch `00 - Index.md`, `03 - Glossary & Design Constants.md`, `27 - Decision Log.md`, the `related:` field, or run git operations. The lead agent orchestrates:

1. Dispatch batch of subagents
2. Each subagent writes ONLY its assigned section file(s)
3. Orchestrator collects results
4. Orchestrator runs the **Consistency Review**
5. Orchestrator updates Index (Document Map + Open Questions), Glossary and `related:` once per batch
6. Orchestrator commits + pushes once per batch

### Subagent Brief

Every subagent prompt includes:

- The section number, name, and suggested H2 headings from the catalog
- The full text of `01 - Game Overview` and `03 - Glossary & Design Constants`
- The full text of already-written sections this one depends on (see Common Cross-References in the catalog)
- The Key Details from Phase 1 and any relevant user statements made in conversation
- The Phase 4 template, callout table and Open Questions rule
- This instruction: *"Use names and numbers from the Glossary exactly. Don't invent design decisions the user hasn't made — raise them as `[!QUESTION]` callouts with a labelled proposal. At the end of your reply, list (a) new terms or shared numbers you introduced, for the Glossary, and (b) any contradictions you noticed with other sections."*

### Dependency Batching

```
Batch 1: 01 - Game Overview, 03 - Glossary & Design Constants (draft)
         (written by the orchestrator, not subagents — they set the foundation)

  ► USER CHECKPOINT — present the pillars, pitch, audience and glossary.
    Ask: "Do these pillars and terms match your vision? Changes now are cheap."
    Do not start Batch 2 until the user approves. Log decisions in 27.

Batch 2: 04 - Core Loop, 05 - Scope & MVP, 06 - World & Lore, 08 - Controls & Input,
         20 - Art Direction, 21 - Audio Design
         (depend only on 01 and 03)

Batch 3: All selected system sections from 07, 09–17
         Custom sections (30+) go here by default

Batch 4: 18 - Tutorial & Onboarding, 19 - UI-UX & Accessibility, 22 - Technical Design,
         23 - Business Model & Monetization, 24 - Analytics & Live Ops,
         25 - Localization & Ratings
         (depend on system sections)
         Custom sections explicitly marked as dependent on all systems also go here

Batch 5: 26 - Development Roadmap (references everything, written last; builds on 05 - Scope & MVP)
```

Skip any batch member the user didn't select. After Batch 3, offer a second short checkpoint: *"The core systems are drafted — want to review them before UI, tech and business sections build on them?"*

### Consistency Review (after every batch)

Before committing, the orchestrator checks the batch against everything already written:

1. **Glossary** — merge new terms the subagents reported into `03`; fix any section using a different name for an existing term
2. **Numbers** — the same quantity (prices, caps, durations, stats) has one value everywhere; conflicts go to the user as a `[!QUESTION]`, not silently picked
3. **Links** — every `[[wiki-link]]` points to an existing note and heading; fix or remove broken ones
4. **Related** — update each new section's `related:` from its body links
5. **Open Questions** — copy every new `[!QUESTION]` into the Index table
6. **Pillars** — flag any mechanic that contradicts a design pillar in `01`

Report what was fixed and any conflicts needing a decision as a **Consistency Review** analysis report (a `checks` block, one row per check with `pass` / `fixed` / `conflict`, plus `findings` of kind `question` for each decision needed — see **Analysis Reports**), and a short summary in chat.

### Commit Per Batch

- Batch 1: `"Add Game Overview and Glossary for <GameTitle>"`
- Batches 2-4: `"Add GDD sections: <section names>"`
- Batch 5: `"Add Development Roadmap for <GameTitle>"`

After Batch 5, if `export_pdf: true`, build the PDF (see **PDF Export**) and commit it with the last batch.

---

## Phase 6: Sprint Planning

Triggered after all GDD sections are complete, if the user wants it.

1. Ask:
   - **Plan length** — how long until the target milestone (default: until the vertical slice in `05 - Scope & MVP`, or **12 weeks**)
   - **Sprint length** — default **2 weeks**
   - **Weekly capacity** — hours per week per person (solo devs especially)
2. Create `sprint-plan/` subfolder in GDD directory

### Task Derivation

- Start from the milestones in `26 - Development Roadmap` and the Must-haves in `05 - Scope & MVP` — sprints serve those milestones; Could/Won't items stay out of the plan
- Each H2 subsystem in a section → task group
- Tasks generated from subsystem descriptions, tables, specs
- Ordered by dependency: foundational systems first
- Each task tagged: `Claude`, `Human`, or `Both`
- Each task sized `S` (≤ half a day), `M` (1–2 days) or `L` (3–5 days); split anything larger. Don't plan more per sprint than the stated capacity
- Unresolved `[!QUESTION]`s that block a task become a "decide X" task before it

| Tag | Meaning |
|-----|---------|
| `Claude` | Fully automatable (scaffold, generate data, write tables) |
| `Human` | Human only (concept art, voice acting, playtesting) |
| `Both` | Claude assists, human validates (level design, balancing) |

### Files

- `00 - Sprint Overview.md` — timeline, milestones, phase breakdown, high-level deliverables per sprint, capacity assumptions
- `Sprint-NN.md` (zero-padded) per sprint, containing:
  - Sprint goals and dates
  - Task table:

    | Task | Category | Size | Section Reference | Status |
    |------|----------|:----:|-------------------|--------|
    | Description | `Claude` / `Human` / `Both` | S / M / L | `[[section]]` | Pending |

  - Dependencies on previous sprints
  - Deliverables checklist

**Optional — GitHub tracking:** offer to mirror the plan to GitHub: one milestone per sprint (`gh api repos/{owner}/{repo}/milestones -f title="Sprint 01" -f due_on=<ISO date>`) and one issue per task (`gh issue create --title <task> --milestone "Sprint 01" --label <Claude|Human|Both>`). Create the labels first with `gh label create`. Ask before creating — it's many issues.

Build a **Sprint Plan** analysis report: stat tiles (sprints, tasks, total hours vs. capacity), a `timeline` of task groups by week (category `claude` / `human` / `both`), and a `bars` block of planned hours per sprint against capacity.

Commit: `"Add sprint plan for <GameTitle>"` → push. Update Index.

---

## Phase 7: Ongoing Maintenance

On every design change:
1. Update affected section(s), bump version (minor), set `updated:` to today
2. If the change is a decision (not a typo fix), add an entry to `27 - Decision Log`
3. Update `03 - Glossary & Design Constants` if a name or shared number changed, and every section using it
4. Update Index if sections added/removed, statuses changed, or open questions resolved
5. Update `related:` if cross-references changed
6. If `export_pdf: true`, rebuild the PDF
7. Commit: `"Update <Section Name>: <brief description>"` → push

When the user answers an open question: replace the `[!QUESTION]` callout with the decided design, log it in the Decision Log, and mark it `resolved` in the Index.

### Section Removal

1. Delete the file (its number is retired, not reused)
2. Remove from Index
3. Find and fix broken `[[wiki-links]]` in other sections
4. Log the removal and reason in `27 - Decision Log`
5. Commit: `"Remove <Section Name>: <reason>"` → push

---

## PDF Export

Can run any time the user asks, and automatically per `export_pdf`. Uses `scripts/build_pdf.py` in this skill's directory (Python standard library only):

```bash
python "<skill-dir>/scripts/build_pdf.py" "<repo-root>/<GameTitle>/GDD"
```

| Option | Effect |
|--------|--------|
| `-o <path>` | Output path (default: `<GDD>/exports/<GameTitle> - GDD.pdf`) |
| `--title <name>` | Title on the cover (default: the folder above `GDD/`) |
| `--paper Letter` | US Letter instead of A4 |
| `--include-sprints` | Append the `sprint-plan/` notes |
| `--html-only` | Write HTML instead (for manual printing) |

The script builds a cover page, a contents page with each section's status and version, and one section per page. Wiki-links become clickable in-document links, callouts keep their colours, and wide ASCII diagrams shrink to fit. It prints with headless Chrome / Edge / Chromium / Brave (set `CHROME_PATH` to override).

Exit code `2` means no browser was found: an HTML file was written next to the target PDF path — tell the user to open it and use **Print → Save as PDF**.

Commit the PDF with the change that produced it: `"Export GDD PDF"` (or include it in the update commit). After exporting, open the PDF for the user if they asked to see it.

---

## Analysis Reports

**Whenever the skill does analysis, show it to the user as a visual web page** — not only as chat text or markdown. This covers:

| Trigger | Report |
|---------|--------|
| Phase 1 genre / competitive research | Market Research |
| Consistency Review after each batch | Consistency Review — Batch N |
| Phase 6 sprint planning | Sprint Plan |
| Any analysis the user asks for (balance, scope, economy, pacing, GDD health, competitor deep-dive…) | Named after the question |

Reports are built with `scripts/build_report.py` (Python standard library only) from a JSON spec, so every report shares one clean, readable design with light and dark themes and works on phones.

### Spec

```json
{
  "title": "Ember Tide Market Research",
  "project": "Ember Tide",
  "kind": "Market Research",
  "subtitle": "One sentence on what this report answers.",
  "blocks": [ { "type": "stats", "items": [ { "label": "Titles compared", "value": "6", "note": "optional" } ] } ]
}
```

Every block takes an optional `heading` and `intro`. Text fields accept `**bold**`, `` `code` ``, `[[wiki-links]]` and `[label](https://url)`.

| Block `type` | Fields | Use for |
|--------------|--------|---------|
| `stats` | `items: [{label, value, note?}]` | 2–4 headline numbers at the top |
| `ratings` | `dimensions: [..]`, `rows: [{name, year?, similarities?, ratings: {dim: 1–5 or null}, evidence?: {dim: "figure, source"}, highlight?}]`, `scale?` | Competitive-analysis heatmap; `null` shows `?`; evidence becomes the cell tooltip; adds an Average column |
| `bars` | `items: [{label, value, display?, highlight?}]`, `unit?`, `max?`, `caption?` | Ranked comparisons (review scores, hours per sprint, cost per system) |
| `findings` | `items: [{kind, title, body}]` — kind: `takeaway`, `pattern`, `gap`, `risk`, `question`, `decision`, `note` | Insight cards |
| `checks` | `items: [{status, label, detail?}]` — status: `pass`, `fixed`, `conflict`, `warning`, `fail`, `info` | Checklists with a status summary |
| `timeline` | `items: [{label, start, length, category?}]`, `weeks?`, `unit?` — category: `claude`, `human`, `both` | Sprint / roadmap Gantt |
| `table` | `headers: [..]`, `rows: [[..]]` | Any other tabular data |
| `list` | `items: [..]`, `ordered?` | Short bullet lists |
| `text` | `body` (paragraphs separated by blank lines) | Narrative |
| `sources` | `items: [{label, url?, note?}]` | Every source behind the numbers |

Put the answer first: stats, then the main chart, then findings, then detail and sources. Use only numbers found in research or in the GDD — the same no-invented-numbers rule as the competitive analysis.

### Build and show

1. Write the spec to a temp file (e.g. `<repo-root>/<GameTitle>/GDD/reports/.spec.json`, deleted after).
2. Build the standalone copy into the repo, so the report is kept with the GDD:
   ```bash
   python "<skill-dir>/scripts/build_report.py" spec.json -o "<repo-root>/<GameTitle>/GDD/reports/<YYYY-MM-DD> - <Report Name>.html"
   ```
3. Show it to the user:
   - **If the `Artifact` tool is available** (claude.ai / Claude Code with Artifacts): build an Artifact-ready copy with `--fragment` into a temp folder, named after the report (e.g. `Ember Tide Market Research.html`), and publish it with `Artifact` (`icon: "chart"`, a one-sentence `description`). Give the user the link. When the same report is rebuilt later in the session (e.g. the next consistency batch), publish a new file for a new report, or the same path to update an existing one.
   - **Otherwise:** add `--open` to step 2 to open the standalone page in the default browser, and tell the user the file path.
4. Commit the HTML in `reports/` with the change that produced it. Link it from `00 - Index.md` under a `## Reports` list (`- [<Report Name>](reports/<file>.html)`); Obsidian opens it in the browser.

The PDF export ignores `reports/`.

---

## Rules (Always Enforced)

- Obsidian-compatible markdown only (wiki-links, callouts)
- Consistent YAML frontmatter on every section, including `updated:`
- Design authority callout on every section
- `NN - Section Name.md` file naming; numbers are stable and never reused
- Names and shared numbers come from `03 - Glossary & Design Constants`
- Unmade decisions are `[!QUESTION]` callouts, never silent inventions
- Every competitive-analysis rating has a source, or is `?`
- Every analysis is shown as a visual web report (Artifact when available, otherwise a local HTML page)
- Index always reflects current state, including open questions
- Decisions are logged in `27 - Decision Log`
- Consistency review before every batch commit
- User checkpoint after Batch 1
- Every change = commit + push; rebuild the PDF first when `export_pdf: true`
- Private repos by default
- Work on the repo's default branch
