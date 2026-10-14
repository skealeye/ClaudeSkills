# ClaudeSkills

A collection of skills for [Claude Code](https://claude.com/claude-code), distributed as a plugin marketplace.

## Included skills

| Skill | Description |
|-------|-------------|
| `gdd` | Researches your game's genre, then writes and maintains a full Game Design Document in a private GitHub repo. Every analysis (market research, consistency reviews, sprint plans) is shown as a visual web report. Read the GDD in Obsidian (the skill can install it for you) or as an exported PDF. |

## Installation

### 1. Add the marketplace

In Claude Code, run:

```
/plugin marketplace add skealeye/ClaudeSkills
```

### 2. Install the plugin

```
/plugin install gdd@claude-skills
```

Or run `/plugin` on its own to browse the marketplace and install from the menu.

### 3. Restart Claude Code

Restart Claude Code so the new skill loads. Then you can use it by typing `/gdd` or by asking Claude to create a game design document.

### Updating

To get the latest version:

```
/plugin marketplace update claude-skills
```

### Uninstalling

```
/plugin uninstall gdd@claude-skills
```

## Prerequisites

The `gdd` skill uses git and the GitHub CLI to create and version-control your GDD repository:

- [git](https://git-scm.com/downloads)
- [GitHub CLI (`gh`)](https://cli.github.com/), signed in with `gh auth login`

If `gh` isn't available, the skill can still work in local-only mode (local git, with no remote push).

### Reading your GDD

During setup the skill asks how you want to read the document:

- **Obsidian** (recommended): clickable links between sections, graph view and live editing. If Obsidian isn't installed, the skill can install it for you (`winget` on Windows, Homebrew on macOS, Flatpak/Snap on Linux), or you can download it from [obsidian.md](https://obsidian.md/download). Then choose *Open folder as vault* and select your game's `GDD` folder.
- **PDF**: a single document with a cover, contents page and clickable cross-references. It is rebuilt automatically whenever the GDD changes. This needs Python 3 and Chrome, Edge, Chromium or Brave. No other packages are required.
- **Both**: you can also ask for a PDF export at any time ("export my GDD to PDF").

## What's new in 2.1

- **Visual analysis reports:** market research, consistency reviews, sprint plans and any analysis you ask for are shown as clean web pages with charts: a rating heatmap with a source on every cell, bar charts, status checklists and a sprint timeline. With Artifacts available (claude.ai or Claude Code), the report is published as a private Artifact link. Otherwise it opens in your browser. A copy is saved in the GDD's `reports/` folder. This needs Python 3, the same as PDF export.

## What's new in 2.0

- **Section catalog for any genre:** adds Story & Characters, Controls & Input, Enemies & AI, Puzzle Mechanics, Multiplayer & Social, Tutorial & Onboarding, Technical Design, Analytics & Live Ops, Localization & Ratings, and Scope & MVP. Section numbers changed from 1.x.
- **Research is saved:** competitive analysis is stored in `02 - Market Research`, and every rating needs a source.
- **Fewer invented details:** unmade decisions become open questions, and you approve the pillars before anything else is written.
- **Consistent sections:** a shared Glossary & Design Constants file, plus a consistency review after each batch.
- **Decision Log:** records why each design change was made.
- **Better sprint planning:** plan length and sprint length are separate, tasks have sizes, and the plan can optionally be mirrored to GitHub Issues.
- **Obsidian install and PDF export.**
