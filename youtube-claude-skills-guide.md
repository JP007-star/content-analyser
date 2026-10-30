# YouTube Claude Skills Guide

> **Interactive reference for all available Claude Code skills** — search, filter, and copy skill names for quick access

![Skills Count](https://img.shields.io/badge/skills-17-brightgreen)
![Categories](https://img.shields.io/badge/categories-13-blue)
![Format](https://img.shields.io/badge/format-Markdown-orange)

---

## Quick Navigation

| Category | Skills |
|----------|--------|
| [Artifacts](#artifacts) | `artifact-design`, `artifact-diagramming` |
| [Configuration](#configuration) | `update-config`, `keybindings-help`, `fewer-permission-prompts` |
| [Code Quality](#code-quality) | `code-review`, `simplify` |
| [Automation](#automation) | `loop` |
| [Reference](#reference) | `claude-api` |
| [Workflows](#workflows) | `workflow-authoring` |
| [Development](#development) | `run` |
| [Advanced](#advanced) | `plugin-authoring` |
| [Setup](#setup) | `init` |
| [Security](#security) | `security-review` |
| [Frameworks](#frameworks) | `developing-with-streamlit` |
| [Tools](#tools) | `hf-cli` |
| [Visualization](#visualization) | `dataviz` |

---

## Artifacts

### `artifact-design` 🎨

**Design guidance and fundamentals for Artifacts.** Load before writing any artifact, including a skill-instructed Markdown one. Markdown is never a shortcut past the design pass.

| Aspect | Details |
|--------|---------|
| **Triggers** | `artifact`, `HTML page`, `web page`, `visualization`, `dashboard`, `artifact-design` |
| **Covers** | Design tokens, responsive layout, theming, typography, color systems, CSP constraints |
| **When to use** | Before creating ANY artifact (HTML, dashboard, visualization, tool, app) |

```bash
# Load before writing artifacts
/skill artifact-design
```

---

### `artifact-diagramming` 📐

**Diagramming know-how for Artifacts** — when a picture earns its place, how to draw one that shows the real mechanism, and the inline-SVG mechanics that keep it legible in both themes.

| Aspect | Details |
|--------|---------|
| **Triggers** | `diagram`, `flowchart`, `architecture diagram`, `sequence diagram`, `SVG`, `visual explanation` |
| **Covers** | Mermaid alternatives, inline SVG, theme-aware diagrams, visual hierarchy |
| **When to use** | Creating architecture diagrams, flowcharts, sequence diagrams, system visualizations |

```bash
# Load before creating diagrams
/skill artifact-diagramming
```

---

## Configuration

### `update-config` ⚙️

**Configure the Claude Code harness via settings.json.** Automated behaviors (hooks), permissions, env vars, hook troubleshooting.

| Aspect | Details |
|--------|---------|
| **Triggers** | `settings.json`, `hooks`, `permissions`, `allow command`, `env var`, `configuration`, `harness config` |
| **Covers** | hooks, permissions, env vars, settings.local.json, automated behaviors |
| **Examples** | `"allow npm commands"`, `"add bq permission to global settings"`, `"set DEBUG=true"` |

```bash
# Configure permissions, hooks, env vars
/skill update-config
```

---

### `keybindings-help` ⌨️

**Customize keyboard shortcuts, rebind keys, add chord bindings, or modify `~/.claude/keybindings.json`.**

| Aspect | Details |
|--------|---------|
| **Triggers** | `keybindings`, `keyboard shortcut`, `rebind key`, `chord binding`, `submit key`, `shortcut` |
| **Covers** | keybindings.json, chords, rebinding, custom shortcuts |
| **Examples** | `"rebind ctrl+s"`, `"add a chord shortcut"`, `"change the submit key"` |

```bash
# Customize keybindings
/skill keybindings-help
```

---

### `fewer-permission-prompts` 🔓

**Scan transcripts for common read-only Bash and MCP tool calls, then add a prioritized allowlist to project `.claude/settings.json` to reduce permission prompts.**

| Aspect | Details |
|--------|---------|
| **Triggers** | `permission prompts`, `reduce prompts`, `allowlist`, `settings.json`, `read-only tools` |
| **Covers** | Transcript analysis, allowlist generation, settings.json, prompt reduction |
| **When to use** | Reducing repetitive permission prompts for read-only operations |

```bash
# Analyze and reduce permission prompts
/skill fewer-permission-prompts
```

---

## Code Quality

### `code-review` 🔍

**Review the current diff, PR, branch, or path for correctness bugs plus reuse/simplification/efficiency cleanups.**

| Aspect | Details |
|--------|---------|
| **Triggers** | `code review`, `review diff`, `review PR`, `find bugs`, `check correctness`, `--comment`, `--fix` |
| **Covers** | Bug detection, correctness, simplification, efficiency, PR comments, auto-fix |
| **Effort Levels** | `low` \| `medium` \| `high` \| `xhigh` \| `max` |
| **Options** | `--comment` (inline PR comments), `--fix` (apply fixes), `--max-findings <n>` |

```bash
# Review with medium effort (default)
/code-review

# Review specific PR with high effort
/code-review --pr 123 --effort high

# Apply fixes automatically
/code-review --fix
```

---

### `simplify` ✨

**Review changed code for reuse, simplification, efficiency, and altitude cleanups, then apply the fixes. Quality only — does not hunt for bugs; use `code-review` for that.**

| Aspect | Details |
|--------|---------|
| **Triggers** | `simplify code`, `refactor`, `clean up`, `reduce complexity`, `simplify` |
| **Covers** | Code simplification, reuse patterns, efficiency, altitude cleanups |
| **When to use** | After making changes, to clean up and simplify code |

```bash
# Simplify recent changes
/simplify
```

---

## Automation

### `loop` 🔄

**Run a prompt or slash command on a recurring interval** (e.g. `/loop 5m /foo`). Omit the interval to let the model self-pace.

| Aspect | Details |
|--------|---------|
| **Triggers** | `recurring task`, `poll for status`, `run repeatedly`, `interval`, `cron`, `loop`, `/loop` |
| **Covers** | Self-pacing, dynamic intervals, recurring execution, status polling |
| **Examples** | `/loop 5m /code-review`, `/loop /babysit-prs` |

```bash
# Run every 5 minutes
/loop 5m /code-review

# Self-paced (model decides interval)
/loop /check-deploy-status
```

---

## Reference

### `claude-api` 📚

**Reference for the Claude API / Anthropic SDK** — model IDs, pricing, params, streaming, tool use, MCP, agents, caching, token counting, model migration.

| Aspect | Details |
|--------|---------|
| **Triggers** | `Claude API`, `Anthropic SDK`, `model pricing`, `token counting`, `prompt caching`, `MCP`, `tool use`, `streaming` |
| **Covers** | Models, pricing, streaming, tools, MCP, agents, caching, migration |
| **⚠️ Required** | Read BEFORE opening target files when Claude/Anthropic is mentioned in any form |

```bash
# Load API reference
/skill claude-api
```

---

## Workflows

### `workflow-authoring` 🔧

**Reference for writing a Workflow tool script** — script API and gotchas, resume, quality patterns, worked examples.

| Aspect | Details |
|--------|---------|
| **Triggers** | `workflow`, `multi-agent`, `orchestration`, `subagents`, `pipeline`, `parallel`, `workflow script` |
| **Covers** | `agent()`, `parallel()`, `pipeline()`, `phase()`, resume, quality patterns |
| **When to use** | Before authoring a Workflow script the user already opted into |

```bash
# Learn workflow authoring
/skill workflow-authoring
```

---

## Development

### `run` ▶️

**Launch and drive this project's app to see a change working.** Use when asked to run, start, or screenshot the app, or confirm a change works.

| Aspect | Details |
|--------|---------|
| **Triggers** | `run app`, `start server`, `screenshot`, `verify change`, `launch`, `dev server`, `test app` |
| **Covers** | Project detection, CLI, server, TUI, Electron, browser-driven, library patterns |
| **When to use** | Verifying changes work in the real app (not just tests) |

```bash
# Run the project
/run
```

---

## Advanced

### `plugin-authoring` 🧩

**Make a mod: a change to Claude's own interface or behaviour** — a panel, pane, band, status line, toast, slash command, or hook on tool calls.

| Aspect | Details |
|--------|---------|
| **Triggers** | `plugin`, `mod`, `panel`, `pane`, `status line`, `slash command`, `hook`, `interface`, `custom UI` |
| **Covers** | UI mods, panels, status lines, toasts, slash commands, tool hooks |
| **When to use** | Building custom Claude Code extensions/modifications |

```bash
# Create a plugin/mod
/skill plugin-authoring
```

---

## Setup

### `init` 🚀

**Initialize a new project or workspace with Claude Code.** Sets up configuration, permissions, and project structure for optimal Claude Code usage.

| Aspect | Details |
|--------|---------|
| **Triggers** | `init project`, `initialize`, `setup`, `new project`, `workspace setup`, `bootstrap` |
| **Covers** | Project initialization, configuration setup, permissions, structure |
| **When to use** | Starting a new project with Claude Code |

```bash
# Initialize new project
/init
```

---

## Security

### `security-review` 🔒

**Security-focused code review for vulnerabilities, injection risks, auth issues, secrets exposure, and secure coding practices.** Complements `code-review` with security lens.

| Aspect | Details |
|--------|---------|
| **Triggers** | `security review`, `vulnerability`, `injection`, `auth`, `secrets`, `secure coding`, `OWASP` |
| **Covers** | Vulnerabilities, injection, authentication, secrets, secure patterns |
| **When to use** | Security auditing, pre-deployment checks, handling sensitive data |

```bash
# Security-focused review
/skill security-review
```

---

## Frameworks

### `developing-with-streamlit` 📊

**Guidance for building Streamlit applications with Claude Code** — components, state management, caching, deployment, and best practices for data apps.

| Aspect | Details |
|--------|---------|
| **Triggers** | `Streamlit`, `streamlit`, `data app`, `st.`, `dataframe`, `dashboard`, `Python web app` |
| **Covers** | Components, session state, caching, deployment, data visualization |
| **When to use** | Building Streamlit data applications |

```bash
# Streamlit development guidance
/skill developing-with-streamlit
```

---

## Tools

### `hf-cli` 🤗

**Reference for the Hugging Face CLI** — model downloads, dataset management, Space deployment, token authentication, and repository operations.

| Aspect | Details |
|--------|---------|
| **Triggers** | `Hugging Face`, `hf cli`, `huggingface`, `model download`, `dataset`, `Space deploy`, `token auth` |
| **Covers** | Models, datasets, Spaces, authentication, repos, transformers |
| **When to use** | Working with Hugging Face Hub, models, datasets |

```bash
# HF CLI reference
/skill hf-cli
```

---

## Visualization

### `dataviz` 📈

**Use whenever creating ANY chart, graph, plot, dashboard, or data visualization.** Produces visualizations that read as one system — elegant, accessible, consistent in light and dark. Includes palette validator.

| Aspect | Details |
|--------|---------|
| **Triggers** | `chart`, `graph`, `plot`, `data viz`, `visualization`, `dashboard`, `analytics`, `visualize data`, `categorical colors`, `palette`, `heatmap` |
| **Covers** | Color formulas, mark specs, interaction rules, palette validator, accessibility |
| **⚠️ Required** | Load BEFORE writing ANY chart code |

```bash
# Load before creating visualizations
/skill dataviz
```

---

## Quick Reference Card

```markdown
# All Skills Alphabetically

- artifact-design
- artifact-diagramming
- claude-api
- code-review
- dataviz
- developing-with-streamlit
- fewer-permission-prompts
- hf-cli
- init
- keybindings-help
- loop
- plugin-authoring
- run
- security-review
- simplify
- update-config
- workflow-authoring
```

---

## Usage Patterns

### For YouTube Content Creation

| Task | Skills to Load |
|------|----------------|
| **Script writing** | `claude-api` (for API refs), `code-review` (quality check) |
| **Code tutorials** | `run` (verify code works), `code-review` (check correctness) |
| **Data visualizations** | `dataviz` (required), `artifact-design` (if making artifacts) |
| **Architecture diagrams** | `artifact-diagramming`, `artifact-design` |
| **Streamlit demos** | `developing-with-streamlit`, `dataviz` |
| **HF model showcases** | `hf-cli`, `run` |
| **Security topics** | `security-review`, `code-review` |

### For Daily Development

| Workflow | Skills |
|----------|--------|
| **Morning setup** | `init` (new projects), `fewer-permission-prompts` (reduce noise) |
| **Code changes** | `code-review` (before commit), `simplify` (after changes) |
| **Recurring checks** | `loop` (CI status, deploy health) |
| **Config changes** | `update-config`, `keybindings-help` |
| **Building tools** | `plugin-authoring`, `artifact-design` |

---

## Skill Loading Syntax

```bash
# Load a single skill
/skill skill-name

# Load multiple skills (space-separated)
/skill artifact-design dataviz

# Skills auto-load on trigger phrases
# e.g., mentioning "chart" auto-loads dataviz
```

---

## Pro Tips

1. **Always load `artifact-design` first** when creating any artifact
2. **Load `dataviz` before ANY chart code** — it's mandatory per the skill
3. **Use `code-review --fix`** to auto-apply safe fixes
4. **Run `fewer-permission-prompts`** periodically to reduce friction
5. **Check `claude-api`** before working with model-specific features
6. **Combine skills**: `/skill artifact-design dataviz` for data viz artifacts

---

## Contributing

This guide reflects the skills available as of **2026-10-31**. Skills may be added/updated over time.

To verify current skills in your session:
```bash
/skills
```

---

*Generated for YouTube Claude Skills Guide — comprehensive reference for all 17 available skills across 13 categories*