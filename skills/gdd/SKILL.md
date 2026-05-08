---
name: gdd
description: Use when creating, updating, or maintaining a Game Design Document (GDD) — covers concept research, genre analysis, competitive analysis, project setup, GitHub repo creation, Obsidian-compatible section authoring, and version control
---

# Game Design Document

## Overview

Standardized workflow for creating and maintaining Game Design Documents. Enforces consistent structure, Obsidian-compatible markdown, automated GitHub version control, parallel subagent authoring, and sprint planning.

## When to Use

- User asks to create a GDD, game design document, or game spec
- User wants to update or maintain an existing GDD project
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

---

## Phase 1: Concept & Research

Ask: *"Do you already have a game concept, or would you like help brainstorming one?"*

If the user already has a detailed concept and wants to skip research, proceed directly to **Phase 2: Project Setup**.

### Path A — User Has an Idea

1. Ask them to describe their game concept (elevator pitch, core mechanics, theme)
2. Identify the primary genre(s) it falls into
3. Proceed to **Genre Research** below

### Path B — User Wants Help Brainstorming

1. Ask: *"What genre or genres are you interested in?"*
   - Offer common genres: Action, RPG, Roguelike, Strategy, Simulation, Survival, Horror, Puzzle, Platformer, FPS, MOBA, Card Game, Extraction Shooter, Idle/Incremental, etc.
   - Allow multiple genre selections for hybrid concepts
2. Proceed to **Genre Research** below
3. After presenting research, collaborate with the user to shape a concept from the findings

### Genre Research — Competitive Analysis

For each selected genre, use `WebSearch` to find the most popular and notable titles. Present findings in a comparison table:

```markdown
## Competitive Analysis: <Genre>

| Game | Similarities | Popularity | Userbase | Profit | Critical Reception | Community | Replayability | Streaming |
|------|-------------|:----------:|:--------:|:------:|:-----------------:|:---------:|:-------------:|:---------:|
| Game Title | Shared mechanics, themes | ★★★★☆ | ★★★☆☆ | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★★ | ★★★★☆ |
```

**Rating dimensions (1–5 stars):**

| Dimension | What to Evaluate |
|-----------|-----------------|
| Popularity | Overall market presence, sales volume, brand recognition |
| Userbase | Active player count, retention, growth trend |
| Profit | Revenue, commercial success, ROI |
| Critical Reception | Critic scores, user review aggregates (Metacritic, Steam) |
| Community | Modding scene, Discord/forum activity, wiki contributions |
| Replayability | Session variety, procedural content, endgame depth |
| Streaming | Twitch/YouTube presence, content creator adoption |

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

Ask: *"Based on this research, are you happy with your concept direction? Any adjustments before we set up the project?"*

Once confirmed, proceed to **Phase 2: Project Setup**.

---

## Phase 2: Project Setup

Ask: *"Create a new private GitHub repo, or connect to an existing one?"*

**New repo:**
1. Prompt for game title
2. `gh repo create <GameTitle> --private`
3. Clone locally
4. Scaffold structure

**Existing repo:**
1. Prompt for repo URL
2. Clone or confirm local path
3. Validate/create GDD folder

### Scaffold

```
<repo-root>/
├── README.md
└── <GameTitle>/
    └── GDD/
        └── 00 - Index.md
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
| Team Size | <solo/team size> |

## Game Design Document
The full GDD is located in [`<GameTitle>/GDD/`](<GameTitle>/GDD/00%20-%20Index.md).
```

### 00 - Index.md Template

```markdown
---
title: "00 - Index"
tags: [gdd, index]
status: draft
version: 0.1
created: <YYYY-MM-DD>
---

# <GameTitle> — Game Design Document

> [!IMPORTANT]
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

## Document Map

| # | Section | Status | Description |
|---|---------|--------|-------------|
| 01 | [[01 - Game Overview]] | Draft | Design pillars, pitch, audience |
| ... | ... | ... | ... |

## How to Use This Document

- **Navigation:** Click `[[wiki-links]]` to jump between sections
- **Callouts:** `[!IMPORTANT]` = hard rules, `[!WARNING]` = pitfalls, `[!TIP]` = rationale, `[!NOTE]` = context
- **Status:** `draft` → `review` → `final`
```

Commit: `"Initialize GDD structure for <GameTitle>"` → push.

---

## Phase 3: Section Selection

1. Present default catalog from `section-catalog.md` (16 sections)
2. Ask which are applicable — "Always" sections included by default
3. Allow custom sections (numbered 17+)

---

## Phase 4: Section Authoring

### File Naming

`NN - Section Name.md` (zero-padded, spaces around dash)

### Mandatory Template

**Frontmatter:**
```yaml
---
title: "NN - Section Name"
tags: [gdd, <topic-tags>]
status: draft
version: 0.1
created: <YYYY-MM-DD>
parent: "[[00 - Index]]"
related:
  - "[[cross-referenced-sections]]"
---
```

**Status values:** `draft` → `review` → `final`
**Version:** Increment minor on each change (0.1 → 0.2). Set 1.0 when `final`.
**Related:** Auto-populated from `[[wiki-links]]` in the body.

**Body structure:**
1. `# NN - Section Name`
2. `> [!IMPORTANT]` design authority callout
3. `---` divider
4. H2 sections: philosophy/overview → core mechanics → edge cases
5. Tables for structured data
6. ASCII diagrams in code blocks for flows/layouts
7. Obsidian callouts: `[!IMPORTANT]` rules, `[!WARNING]` pitfalls, `[!TIP]` rationale, `[!NOTE]` context
8. `[[wiki-links]]` with optional heading anchors
9. Related Documents footer

---

## Phase 5: Parallel Subagent Dispatch

### Orchestrator Pattern

Subagents do NOT touch `00 - Index.md` or run git operations. The lead agent orchestrates:

1. Dispatch batch of subagents
2. Each subagent writes ONLY its assigned section file(s)
3. Orchestrator collects results
4. Orchestrator updates Index once per batch
5. Orchestrator commits + pushes once per batch

### Dependency Batching

```
Batch 1: 01 - Game Overview (foundational, written first)

Batch 2: 02 - World & Lore, 03 - Core Loop, 13 - Art Direction, 14 - Audio Design
         (independent, depend only on 01)

Batch 3: All selected sections from 04-11 (parallel, all independent system sections)
         Custom sections (17+) go here by default

Batch 4: 12 - UI-UX, 15 - Monetization (depend on system sections)
         Custom sections explicitly marked as dependent on all systems also go here

Batch 5: 16 - Development Roadmap (references everything, written last)
```

### Commit Per Batch

- Batch 1: `"Add Game Overview for <GameTitle>"`
- Batches 2-4: `"Add GDD sections: <section names>"`
- Batch 5: `"Add Development Roadmap for <GameTitle>"`

---

## Phase 6: Sprint Planning

Triggered after all GDD sections are complete.

1. Ask sprint duration — default **12 weeks**, adjustable
2. Create `sprint-plan/` subfolder in GDD directory

### Task Derivation

- Each H2 subsystem in a section → task group
- Tasks generated from subsystem descriptions, tables, specs
- Ordered by dependency: foundational systems first
- Each task tagged: `Claude`, `Human`, or `Both`

| Tag | Meaning |
|-----|---------|
| `Claude` | Fully automatable (scaffold, generate data, write tables) |
| `Human` | Human only (concept art, voice acting, playtesting) |
| `Both` | Claude assists, human validates (level design, balancing) |

### Files

- `00 - Sprint Overview.md` — timeline, milestones, phase breakdown, high-level deliverables per sprint
- `Sprint-NN.md` (zero-padded) per week, containing:
  - Sprint goals
  - Task table:

    | Task | Category | Section Reference | Status |
    |------|----------|-------------------|--------|
    | Description | `Claude` / `Human` / `Both` | `[[section]]` | Pending |

  - Dependencies on previous sprints
  - Deliverables checklist

Commit: `"Add sprint plan for <GameTitle>"` → push. Update Index.

---

## Phase 7: Ongoing Maintenance

On every design change:
1. Update affected section(s)
2. Update Index if sections added/removed
3. Bump version (minor increment)
4. Update `related:` if cross-references changed
5. Commit: `"Update <Section Name>: <brief description>"` → push

### Section Removal

1. Delete the file
2. Remove from Index
3. Find and fix broken `[[wiki-links]]` in other sections
4. Commit: `"Remove <Section Name>: <reason>"` → push

---

## Rules (Always Enforced)

- Obsidian-compatible markdown only (wiki-links, callouts)
- Consistent YAML frontmatter on every section
- Design authority callout on every section
- `NN - Section Name.md` file naming
- Index always reflects current state
- Every change = commit + push
- Private repos by default
- Work on `main` branch
