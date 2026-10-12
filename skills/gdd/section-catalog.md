# GDD Section Catalog

Section numbers are **stable IDs**, not positions. Skipped sections leave gaps (01, 03, 04, 08…) and numbers are never reused or renumbered, so `[[wiki-links]]` and commit history stay valid. Custom sections start at **30**.

## Default Sections

### Foundation

| # | Section | When Applicable | Suggested H2 Headings |
|---|---------|-----------------|----------------------|
| 01 | Game Overview | Always | Elevator Pitch, Design Pillars, Target Audience & Player Personas, Platforms & Engine, Unique Selling Points, What Success Looks Like |
| 02 | Market Research | Always (written from Phase 1) | Competitive Analysis, Common Patterns, Market Gaps, Risks & Saturated Mechanics, Sources |
| 03 | Glossary & Design Constants | Always | Terminology, Core Stats & Attributes, Currencies & Resources, Rarity / Tier Scales, Global Numbers (session length, player count, caps) |
| 04 | Core Loop | Always | Primary Loop, Session Flow, Nested Loops (moment / session / long-term), Tension Curve, Decision Points, Retention Hooks |
| 05 | Scope & MVP | Always | Vertical Slice Definition, MVP Feature List (Must / Should / Could / Won't), Cut List, Scope Risks |

### Narrative

| # | Section | When Applicable | Suggested H2 Headings |
|---|---------|-----------------|----------------------|
| 06 | World & Lore | Games with a setting | Setting Overview, History, Factions, Key Locations, Narrative Tone, Lore Delivery Methods |
| 07 | Story, Characters & Dialogue | Story-driven games | Story Synopsis, Act Structure, Main Characters, Character Arcs, Dialogue System, Branching & Choices, Endings |

### Gameplay Systems

| # | Section | When Applicable | Suggested H2 Headings |
|---|---------|-----------------|----------------------|
| 08 | Controls & Input | Always | Input Philosophy, Control Schemes (KB+M / Gamepad / Touch), Action Map, Camera, Remapping, Input Buffering & Feel |
| 09 | Movement & Exploration | Games with traversal/discovery | Movement Mechanics, Traversal Abilities, Discovery Systems, Gating & Keys, Environmental Storytelling, Points of Interest |
| 10 | Combat | Games with combat | Combat Philosophy, Attack / Defense Mechanics, Damage Model, Status Effects, Weapons & Abilities, Boss Design, Combat Feel |
| 11 | Enemies & AI | Games with enemies or NPC agents | Enemy Roster, Behaviour States, Perception, Difficulty Scaling, Spawning Rules, Companion / NPC AI |
| 12 | Levels & World Structure | Games with distinct areas | World Structure (linear / hub / open), Per-Level Breakdown, Pacing, Level Design Rules, Procedural Generation Rules |
| 13 | Progression & Economy | Games with progression or currency | XP & Leveling, Unlock Tree, Currencies (sources & sinks), Crafting, Economy Balance, Prestige / Meta-Progression |
| 14 | Puzzle Mechanics | Puzzle games or puzzle elements | Puzzle Philosophy, Mechanic Vocabulary, Difficulty Curve, Hint System, Solution Validation |
| 15 | Multiplayer & Social | Co-op, PvP or social play | Modes (co-op / PvP / async), Matchmaking, Party & Lobby, Ranking, Anti-Cheat & Anti-Grief, Communication, Social Features |
| 16 | Hub & Base Building | Games with a hub, base or home | Hub Purpose, Room / Building Types, Upgrade Paths, NPC Interactions, Storage, Customization |
| 17 | Signature Mechanic | Games built around a distinctive system (cards, extraction, time-loop, rhythm, deck-building, etc.) | Mechanic Philosophy, Rules & Anatomy, Content Catalog, Synergies & Archetypes, Risk / Reward, Expansion Framework — rename the section to the mechanic, e.g. `17 - Card System` |
| 18 | Tutorial & Onboarding | Always | First-Time User Experience, Teaching Sequence, Tutorial Gating, Difficulty Options, Re-engagement for Returning Players |

### Presentation

| # | Section | When Applicable | Suggested H2 Headings |
|---|---------|-----------------|----------------------|
| 19 | UI-UX & Accessibility | Always | HUD Design, Menu Flow, Notification Systems, Accessibility Options (visual / audio / motor / cognitive), Controller & Platform UI, Text & Font Scaling |
| 20 | Art Direction | Always | Visual Style, Reference Board, Color Palette, Character Design Language, Environment Art, VFX Philosophy, Animation Style |
| 21 | Audio Design | Always | Audio Philosophy, SFX Design, Music & Dynamic Music, Spatial Audio, Voice-Over, Adaptive Mixing |

### Production & Business

| # | Section | When Applicable | Suggested H2 Headings |
|---|---------|-----------------|----------------------|
| 22 | Technical Design | Always | Engine & Tools, Target Hardware & Performance Budgets, Architecture Overview, Save System, Networking, Platform Requirements, Third-Party Services |
| 23 | Business Model & Monetization | Always | Business Model (premium / F2P / subscription), Pricing, Store Strategy, Cosmetics / DLC / Season Pass (if any), Ethical Monetization Rules, Revenue Projections |
| 24 | Analytics & Live Ops | Live-service or data-driven games | Key Metrics & KPIs, Telemetry Events, Content Cadence, Events & Seasons, Patching Strategy, Community Management |
| 25 | Localization & Ratings | Shipping to multiple regions or stores | Target Languages, Text & VO Localization, Cultural Review, Age Ratings (ESRB / PEGI / IARC), Legal & Privacy |
| 26 | Development Roadmap | Always | Phase Breakdown, Milestone Definitions, Risk Register, Resource & Budget Estimates, Tooling |
| 27 | Decision Log | Always (created at setup) | One H2 per decision — see the template in `SKILL.md` |

## Content Type Guidance

| Content Type | When to Use | Format |
|---|---|---|
| Tables | Stats, parameters, item lists, comparisons, loot tables | Markdown tables |
| ASCII Diagrams | Flows, spatial layouts, state machines, HUD mockups | Code-fenced blocks (keep under ~100 characters wide so they fit a PDF page) |
| Prose | Philosophy, narrative, world-building | Paragraphs with bold/italic emphasis |
| Callout Boxes | Rules, pitfalls, rationale, open questions | `> [!TYPE]` Obsidian syntax — see the callout table in `SKILL.md` |

## Common Cross-References

| Section | Commonly Related To |
|---|---|
| 01 - Game Overview | All sections (foundational) |
| 03 - Glossary & Design Constants | All sections (shared names and numbers) |
| 04 - Core Loop | 09, 10, 12, 13, 17 |
| 05 - Scope & MVP | 26, every system section |
| 07 - Story, Characters & Dialogue | 06, 12, 21 |
| 10 - Combat | 08, 11, 13, 17 |
| 11 - Enemies & AI | 10, 12 |
| 12 - Levels & World Structure | 09, 11, 14 |
| 13 - Progression & Economy | 04, 16, 17, 23 |
| 15 - Multiplayer & Social | 10, 13, 22 |
| 17 - Signature Mechanic | 04, 10, 13 |
| 18 - Tutorial & Onboarding | 04, 08, 19 |
| 19 - UI-UX & Accessibility | 08, all system sections (09–17) |
| 22 - Technical Design | 15, 19, 24 |
| 23 - Business Model & Monetization | 13, 24 |
| 26 - Development Roadmap | 05, all sections |
