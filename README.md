# Claude Code Skills & Config

My personal [Claude Code](https://docs.anthropic.com/en/docs/claude-code) workspace — custom skills, global rules, and memory files. This is a living backup that syncs across machines.

> **This is a personal setup.** The skills reference my specific tools (GitHub orgs, Jira, esa.io) and workflows. They won't work out of the box for everyone, but they're a good starting point if you want to build your own.

## Setup

### Quick start (recommended)

If you just want one skill, copy it directly:

```bash
# Copy the skill into your Claude Code skills directory
cp -r skills/hnh-pr-review ~/.claude/skills/
```

Then restart Claude Code — it picks up new skills automatically.

### Full workspace setup

The `hnh-setup` skill bootstraps the entire workspace — directory structure, skills, rules, and memory. To use it:

1. **Install the setup skill first** (the one skill you need to copy manually):

   ```bash
   mkdir -p ~/.claude/skills
   cp -r skills/hnh-setup ~/.claude/skills/
   ```

2. **Run it** in Claude Code:

   ```
   /hnh-setup
   ```

   It clones this repo, creates the directory layout, and installs everything.

### Credentials

Most skills reference credentials from `~/.zshrc` and assume a specific directory layout (`~/ws/code/github.com/{org}/{repo}/`). Edit the skills to match your own setup.

Skills that call external APIs expect env vars like these:

```bash
# Example — adjust for your own services
export JIRA_BASE_URL="https://your-org.atlassian.net"
export JIRA_EMAIL="you@company.com"
export JIRA_API_TOKEN="your-token"
export ESA_ACCESS_TOKEN="your-token"
export NOTION_API_TOKEN="your-notion-token"
export GITHUB_WORK_USERNAME="your-github-username"
```

## Skills

| Skill | Trigger | What it does |
|-------|---------|-------------|
| **hnh-pr-review** | Share a GitHub PR URL or say "review this PR" | Deep PR review: fetches PR metadata + linked Jira/esa tickets, verifies the build locally, runs 5 parallel review agents (document context, build, architecture, clean code, discussion history), and delivers a categorized report (Critical / Warning / Suggestion / Clean Code / Nice to Have) with clickable GitHub links. |
| **hnh-backup** | Say "backup" or "sync to GitHub" | Backs up skills, plans, rules, and memory to this repo. Sanitizes credentials, device paths, and work usernames before pushing. |
| **hnh-setup** | Say "setup" on a new machine | Bootstraps the full Claude workspace — clones this repo, creates directory structure, installs skills and rules. Handles both first-time setup and incremental syncs. |
| **hnh-sentry-report** | Share a Sentry issue URL or say "investigate this Sentry error" | Fetches full Sentry context (stacktraces, events, tags, frequency), explores the local codebase to trace the root cause, and delivers a prioritized report (P0-P4) with suggested fixes. Offers to create a Jira ticket with AI-generated content disclaimer. |
| **hnh-plan** | Say "plan this" or "create a plan" | Principal-engineer-level implementation planning from plain text. Challenges the problem, interviews, launches parallel agents (context gatherer + architecture analyst), proposes alternatives, and produces a plan with testing strategy, risk analysis, observability, and deployment steps. |
| **hnh-plan-jira** | Share a Jira ticket URL or ID | Same as hnh-plan but fetches Jira ticket details (description, comments, linked issues) first. |
| **hnh-plan-notion** | Share a Notion page URL | Same as hnh-plan but fetches Notion page content first. |
| **hnh-skill-creator** | Say "create a skill" or "improve this skill" | Guided skill creation with test cases, evaluation viewer, quantitative benchmarks, and iterative improvement. Includes description optimization for better triggering accuracy. |

## Repo structure

```
CLAUDE.md              # Global instructions (generic, public-safe)
skills/                # Custom skills
  hnh-pr-review/       #   PR review with parallel agents
  hnh-sentry-report/   #   Sentry issue investigation & triage
  hnh-plan/            #   Implementation planning (plain text, shared workflow)
  hnh-plan-jira/       #   Implementation planning (from Jira ticket)
  hnh-plan-notion/     #   Implementation planning (from Notion page)
  hnh-backup/          #   Backup to GitHub with sanitization
  hnh-setup/           #   Workspace bootstrapping
  hnh-skill-creator/   #   Skill creation & evaluation
memory/                # Persistent memory (preferences, indexes)
rules/                 # Global rules (git, credentials, workspace)
```

## How skills work

Each skill is a directory under `~/.claude/skills/` with a `SKILL.md` file. The frontmatter (`name`, `description`) controls when Claude triggers the skill. The body contains the instructions Claude follows.

```
my-skill/
  SKILL.md          # Required — frontmatter + instructions
  scripts/          # Optional — helper scripts the skill can call
  references/       # Optional — docs loaded on demand
```

You invoke a skill by typing `/skill-name` in Claude Code, or just describe what you want — Claude matches your request to the skill's description automatically.

For more on building skills, see the [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code).
