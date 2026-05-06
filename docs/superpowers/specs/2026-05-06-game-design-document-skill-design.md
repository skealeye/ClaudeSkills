# Game Design Document (GDD) Skill — Design Spec

## Overview

A Claude skill that standardizes the creation, authoring, and maintenance of Game Design Documents. The skill enforces a consistent structure across all game projects, outputs Obsidian-compatible markdown, automates GitHub version control, dispatches parallel subagents for efficient authoring, and generates sprint plans after the GDD is complete.

## Skill Identity

- **Name:** `gdd`
- **Slash command:** `/gdd`
- **Type:** Technique/workflow
- **Approach:** Single monolithic skill (Approach A) — one `SKILL.md` + one `section-catalog.md` reference file
- **Location:** Plugin directory at `D:\ClaudeSkills\GDD\skills\gdd\`
- **Trigger:** Use when the user asks to create a game design document, GDD, game spec, or wants to update/maintain an existing GDD project. Also triggered via `/gdd`.

---

## Prerequisites

Before any GitHub operations, the skill must verify:

1. **`gh` CLI is installed** — run `gh --version`
2. **`gh` is authenticated** — run `gh auth status`
3. **`git` is available** — run `git --version`

**Fallback:** If `gh` is unavailable or not authenticated, offer two options:
- Guide the user through `gh auth login`
- Work in local-only mode (init a local git repo without a remote, skip push operations)

If repo creation fails (name collision, permissions, network), present the error and let the user retry with a different name or connect to an existing repo instead.

---

## Phase 1: Project Setup

### Repo Decision

Prompt the user: *"Create a new private GitHub repo, or connect to an existing one?"*

**New repo path:**
1. Prompt for game title
2. `gh repo create <GameTitle> --private`
3. Clone locally
4. Scaffold initial structure

**Existing repo path:**
1. Prompt for repo URL
2. Clone or confirm local path
3. Validate/create GDD folder structure

### Scaffold Structure

The repo root is `<GameTitle>/` (created by `gh repo clone`). Inside the repo, the GDD lives at `<GameTitle>/GDD/`:

```
<repo-root>/              <- repo root (named after the game title)
├── README.md             <- high-level project overview
└── <GameTitle>/
    └── GDD/
        └── 00 - Index.md <- Obsidian hub with Document Map
```

The outer directory is the repo clone folder. The inner `<GameTitle>/GDD/` nesting is intentional — it supports monorepo use cases where multiple game projects could coexist, and matches the established pattern from CipherRun (`CipherRun/GDD/`), SignalDecay (`SignalDecay/GDD/`), and CraterKings (`CraterKings/GDD/`).

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

### 00 - Index.md (Hub File)

Contents:
- Quick reference table (genre, engine, platform, players)
- Document Map table linking all active sections with one-line descriptions
- "How to Use This Document" guide (conventions for callouts, wiki-links)
- Updated automatically when sections are added or removed

### Initial Commit

Commit and push scaffold: `"Initialize GDD structure for <GameTitle>"`

---

## Phase 2: Section Selection

1. Present the default section catalog (16 sections) to the user
2. Ask which sections are applicable to this game
3. Allow the user to add custom sections (numbered sequentially after 16)
4. Sections marked "Always" in the catalog are included by default

### Default Section Catalog

| # | Section | When Applicable |
|---|---------|-----------------|
| 01 | Game Overview | Always |
| 02 | World & Lore | Always |
| 03 | Core Loop | Always |
| 04 | Exploration | Games with traversal/discovery |
| 05 | Combat System | Games with combat |
| 06 | Card System | Games with card mechanics |
| 07 | Zones & Maps | Games with distinct areas |
| 08 | Extraction Mechanics | Extraction-style games |
| 09 | PvP System | Games with PvP |
| 10 | Progression & Economy | Games with progression/currency |
| 11 | The Hideout | Games with a hub/base |
| 12 | UI-UX | Always |
| 13 | Art Direction | Always |
| 14 | Audio Design | Always |
| 15 | Monetization | Games with monetization |
| 16 | Development Roadmap | Always |

This catalog is stored in `section-catalog.md` as a supporting reference file. The catalog contains:
- The applicability table above
- Per-section guidance: suggested H2 headings, typical content types (tables, diagrams, prose), and cross-reference expectations
- Notes on which sections commonly relate to each other

---

## Phase 3: Section Authoring

### Section File Template

Every section file follows this mandatory structure:

**Filename:** `NN - Section Name.md` (zero-padded, spaces around dash)

**YAML Frontmatter:**
```yaml
---
title: "NN - Section Name"
tags: [gdd, <topic-tags>]
status: draft
version: 0.1
created: <YYYY-MM-DD>
parent: "[[00 - Index]]"
related:
  - "[[other-sections]]"
---
```

**Frontmatter field rules:**
- `status`: Valid values are `draft`, `review`, `final`. New sections start as `draft`. Set to `review` when requesting feedback. Set to `final` when the section is approved and locked.
- `version`: Increment minor version on each change (0.1 → 0.2 → 0.3). Set to `1.0` when status changes to `final`.
- `related`: Populated with sections that are directly referenced via `[[wiki-links]]` in the body of the document. Updated automatically when cross-references are added or removed.

**Body:**
1. `# NN - Section Name` — H1 matching filename
2. `> [!IMPORTANT]` callout — design authority statement (what this section controls and why it matters)
3. `---` divider
4. H2 sections — philosophy/overview first, core mechanics middle, edge cases last
5. Heavy use of **tables** for structured data (stats, items, comparisons, parameters)
6. **ASCII diagrams** in code blocks for flows, spatial layouts, state machines
7. **Obsidian callouts** throughout:
   - `[!IMPORTANT]` — hard design rules
   - `[!WARNING]` — design pitfalls
   - `[!TIP]` — design rationale
   - `[!NOTE]` — cross-references, context
8. `[[wiki-links]]` for cross-references (with optional heading anchors)
9. Related Documents footer

---

## Phase 4: Parallel Subagent Dispatch

During authoring, the skill identifies independent sections and dispatches subagents to work in parallel. Each subagent follows the same authoring template.

### Orchestrator Pattern

**Critical:** Subagents do NOT touch `00 - Index.md` or run git operations. The lead agent (orchestrator) handles all shared state:

1. Orchestrator dispatches a batch of subagents
2. Each subagent writes ONLY its assigned section file(s) and returns the content
3. Orchestrator collects all results from the batch
4. Orchestrator updates `00 - Index.md` once for the entire batch
5. Orchestrator commits and pushes all batch files in a single commit

This prevents race conditions on the Index file and git lock conflicts.

### Dependency-Aware Batching

```
Batch 1: 01 - Game Overview
         (foundational — must be written first, establishes pillars and identity)

Batch 2: 02 - World & Lore
         03 - Core Loop
         13 - Art Direction
         14 - Audio Design
         (independent from each other, only depend on 01)

Batch 3: All selected sections from 04-11, run in parallel
         (these are all system-specific sections that depend on Batch 1-2
          but are independent from each other — each describes a self-contained
          game system)

Batch 4: 12 - UI-UX
         15 - Monetization
         (depend on knowing what systems exist from Batches 1-3)

Batch 5: 16 - Development Roadmap
         (references all other sections, must be last)
```

**Custom sections** (numbered 17+) are placed in **Batch 3** by default (treated as system-specific sections) unless the user explicitly marks them as dependent on all other sections, in which case they go in Batch 4.

### Commit Per Batch

After each batch completes, the orchestrator makes a single commit:
- Batch 1: `"Add Game Overview for <GameTitle>"`
- Batches 2-4: `"Add GDD sections: <comma-separated section names>"`
- Batch 5: `"Add Development Roadmap for <GameTitle>"`

---

## Phase 5: Sprint Planning

Triggered after all GDD sections are complete.

### Setup

1. Ask user for sprint duration — default **12 weeks**, adjustable
2. Create `sprint-plan/` subfolder inside the GDD directory

### Sprint File Structure

```
<repo-root>/
└── <GameTitle>/
    └── GDD/
        ├── 00 - Index.md
        ├── 01 - Game Overview.md
        ├── ...
        └── sprint-plan/
            ├── 00 - Sprint Overview.md
            ├── Sprint-01.md
            ├── Sprint-02.md
            └── ...
```

### Task Derivation

Sprint tasks are derived from the GDD content as follows:
- Each **H2 subsystem** within a section becomes a **task group**
- Implementation tasks are generated from the subsystem descriptions, tables, and specifications
- Tasks are ordered by dependency: foundational systems first (core loop, progression), dependent systems later (UI, monetization)
- Each task is categorized as Claude/Human/Both based on the nature of the work

### 00 - Sprint Overview.md

- Total timeline and milestone summary
- Phase breakdown
- High-level deliverables per sprint

### Per-Sprint Files (Sprint-NN.md)

Each sprint file contains:
- Sprint goals
- Task table with columns:

| Task | Category | Section Reference | Status |
|------|----------|-------------------|--------|
| Description | `Claude` / `Human` / `Both` | `[[section]]` | Pending |

- Dependencies on previous sprints
- Deliverables checklist

### Task Categories

| Tag | Meaning | Examples |
|-----|---------|---------|
| `Claude` | Fully automatable by Claude | Generate placeholder lore, scaffold UI layouts, write data tables |
| `Human` | Requires human work only | Concept art, voice acting, playtesting, music composition |
| `Both` | Claude assists, human validates | Level design, balancing, narrative review, UX testing |

### Commit + Push

Commit: `"Add sprint plan for <GameTitle>"`. Index is updated to link to the Sprint Overview.

---

## Phase 6: Ongoing Maintenance

### Design Change Workflow

When the user requests a design change:
1. Update the affected section file(s)
2. Update the Index if sections are added or removed
3. Bump the `version` in frontmatter (minor increment: 0.1 → 0.2)
4. Update the `related:` field if cross-references changed
5. Commit with descriptive message: `"Update <Section Name>: <brief description of change>"`
6. Push to origin

### Section Removal

When a section is no longer needed:
1. Delete the section file
2. Remove the entry from `00 - Index.md` Document Map
3. Search all remaining sections for `[[wiki-links]]` referencing the removed section
4. Update or remove broken references
5. Commit: `"Remove <Section Name>: <reason>"`
6. Push to origin

### Rules Enforced at All Times

- Obsidian-compatible markdown only (wiki-links, callouts)
- Consistent YAML frontmatter schema on every section
- Design authority callout on every section
- Numbered file naming: `NN - Section Name.md`
- Index always reflects current state of all sections
- Every change triggers commit + push
- Repos are private by default
- Work on `main` branch (the skill does not manage feature branches)

---

## File Deliverables

The skill consists of two files:

```
skills/gdd/
├── SKILL.md              <- Main skill: workflow, template, rules, automation
└── section-catalog.md    <- Reference: default 16 sections with per-section guidance
```
