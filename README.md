# ClaudeSkills

A collection of skills for [Claude Code](https://claude.com/claude-code), distributed as a plugin marketplace.

## Included skills

| Skill | Description |
|-------|-------------|
| `gdd` | Standardized Game Design Document creation, authoring, and maintenance with Obsidian-compatible output and GitHub automation. |

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
