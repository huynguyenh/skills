# Claude Code Skills & Config

My personal [Claude Code](https://docs.anthropic.com/en/docs/claude-code) workspace — custom skills, global rules, and memory files. This is a living backup that syncs across machines.

> **This is a personal setup.** The skills reference my specific tools (GitHub orgs, Jira, esa.io) and workflows. They won't work out of the box for everyone, but they're a good starting point if you want to build your own.

## Setup

### Quick start (recommended)

If you just want one skill, copy it directly:

```bash
# Copy the skill into your Claude Code skills directory
cp -r skills/hnh-review-pr ~/.claude/skills/
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
export JIRA_EMAIL="<email>"
export JIRA_API_TOKEN="your-token"
export ESA_ACCESS_TOKEN="your-token"
export NOTION_API_TOKEN="your-notion-token"
export GITHUB_WORK_USERNAME="your-github-username"
```

## Skills

| Skill | Trigger | What it does |
|-------|---------|-------------|
| **hnh-review-pr** | Share a GitHub PR URL or say "review this PR" | Deep PR review: fetches PR metadata + linked Jira/esa tickets, verifies the build locally, runs 5 parallel review agents (document context, build, architecture, clean code, discussion history), then 3 verification agents (fact checker, logic verifier, pattern verifier) to eliminate false positives, and delivers a categorized report with clickable GitHub links. |
| **hnh-report-sentry** | Share a Sentry issue URL or say "investigate this Sentry error" | Fetches full Sentry context (stacktraces, events, tags, frequency), explores the local codebase to trace the root cause, and delivers a prioritized report (P0-P4) with suggested fixes. Offers to create a Jira ticket with AI-generated content disclaimer. |
| **hnh-backup** | Say "backup" or "sync to GitHub" | Backs up skills, plans, rules, and memory to this repo. Sanitizes credentials, device paths, and work usernames before pushing. |
| **hnh-setup** | Say "setup" on a new machine | Bootstraps the full Claude workspace — clones this repo, creates directory structure, installs skills and rules. Handles both first-time setup and incremental syncs. |
| **hnh-plan** | Say "plan this" or "create a plan" | Principal-engineer-level implementation planning from plain text. Challenges the problem, interviews, launches parallel agents (context gatherer + architecture analyst), proposes alternatives, and produces a plan with testing strategy, risk analysis, observability, and deployment steps. |
| **hnh-plan-jira** | Share a Jira ticket URL or ID | Same as hnh-plan but fetches Jira ticket details (description, comments, linked issues) first. |
| **hnh-plan-notion** | Share a Notion page URL | Same as hnh-plan but fetches Notion page content first. |
| **hnh-create-skill** | Say "create a skill" or "improve this skill" | Guided skill creation with test cases, evaluation viewer, quantitative benchmarks, and iterative improvement. Includes description optimization for better triggering accuracy. |
| **hnh-add-knowledge** | Share a fact, tip, or insight to remember | Capture and organize personal knowledge into a structured, searchable knowledge base by scope (global/work/personal) and domain. |
| **hnh-gg-sheets** | Say "create a sheet", share a Google Sheets URL, or mention "gsheet" | Interact with Google Sheets via Sheets & Drive APIs — create, read, write, format, share, and search spreadsheets. Defaults to ZenLabs Drive conventions when no project is specified. |
| **hnh-gg-drive** | Say "upload to Drive", "download from Drive", or mention Google Drive files/folders | Interact with Google Drive — list, search, upload, download, move, copy, rename, trash, and organize files and folders via the Drive API. |
| **hnh-notion** | Say "in Notion", "with Notion", share a Notion URL, or mention databases/records in a Notion context | Interact with Notion — read pages, create pages, update properties, append content, query databases, manage records, get database schemas, and search across the workspace. Uses the Notion REST API via a Python CLI tool. |
| **hnh-design-guideline** | Generating any visual output (PDFs, presentations, HTML, spreadsheets) or mention "brand", "our colors", "our fonts" | ZenLabs brand design system — colors (Emerald, Firefly, Ecru palettes), typography (Rubik/Inter), spacing, and logo usage rules for all generated visual outputs. Consulted automatically before choosing colors/fonts for any ZenLabs deliverable. |
| **hnh-dify** | Say "in Dify", "run my Dify workflow", "check Dify logs", or mention Dify apps | Interact with Dify.ai — run workflows, chat with apps, manage knowledge bases, view logs, upload files, and manage conversations via the Dify Service API. |
| **hnh-discord** | Say "in Discord", "on Discord", "post to Discord", or share a Discord link | Interact with Discord — read/send messages, search, react, pin, manage threads, browse channels and members via the Discord Bot API. |
| **hnh-facebook-manual** | Share a facebook.com URL, say "FB", "check this post", "get comments", or ask about reactions/shares | Interact with Facebook via browser automation — fetch comments, reactions, shares, post content, and perform actions like liking and commenting using the Chrome Claude Extension. |
| **hnh-gg-docs** | Say "Google Doc", share a docs.google.com URL, or mention creating/reading docs in Google Drive | Interact with Google Docs — read content, create documents, append text, find-and-replace, and get document metadata via the Google Docs API. |
| **hnh-maintain-skills** | Say "maintain skills", "skill audit", or "review skills" | Scans all custom skills for improvement opportunities — detects raw API calls replaceable by wrapper skills, stale file references, credential anti-patterns, missing cross-references, and duplicated logic. |
| **hnh-wbs** | Say "WBS", "scope this project", "break this down", or share a project brief | CTO-level Work Breakdown Structure generator — evaluates multiple technical approaches across the full SDLC, recommends the best option, and produces a branded PDF. Supports scope mode (no estimates) and estimate mode (AI-augmented man-day estimates). |
| **hnh-get-report** | Say "report", "status update", "how's [project] going?" | CEO-level project status report — scans backlog spreadsheets, GitHub repos, Google Drive, and Notion in parallel. Computes pipeline metrics, tracks UC movement, and highlights changes since the last report. |
| **hnh-record-screen** | Say "record", "screen capture", "demo video", or "screencast" | Record screen demos and optimize video output — capture walkthroughs, produce screencasts, compress large video files (MOV, MP4). |
| **hnh-aws** | Say "check S3", "show ECR images", "RDS status", "CloudWatch logs", or any AWS operation | Interact with AWS infrastructure — S3 buckets, ECR container registries, RDS databases, CloudWatch logs/metrics, and IAM users/roles via the AWS CLI. |
| **hnh-k8s** | Say "check pods", "show me logs", "why is it crashing", or any Kubernetes/EKS operation | Debug and monitor Kubernetes (EKS) clusters — check pod status, read logs, inspect events, troubleshoot crashes, and view resource usage via kubectl. |
| **hnh-document-demo** | Say "wrap this up", "document this demo", "demo-1", or mention build-with-ai repo | Package a build session into a shareable "Build with AI" markdown doc with screenshots, push to zenlbs/build-with-ai GitHub repo. Focuses on technical process (skills, prompting, feedback loop), not just features. |
| **hnh-zenlabs-infras** | Say "how's our infra", "infra report", "check the cluster", or ask about CPU/memory/disk | Real-time infrastructure health report — EKS cluster (nodes, pods, deployments, resource usage), AWS services (EC2, RDS, S3, CloudWatch), and application-level health (Sentry error rates, endpoint checks). |
| **hnh-zenlabs-release** | Say "deploy this", "release this", "set up CI/CD", or mention ArgoCD/ECR/Helm | Full CI/CD pipeline setup and deployment — GitHub Actions, Dockerfile, ECR, Helm values, ArgoCD, GitHub secrets, DNS (Route53). Handles both new service setup and subsequent releases. |
| **hnh-create-pr** | Say "create a PR", "wrap this up", or "open a pull request" | Wrap up a coding session into a PR — commit changes, create branch, push, open PR with description, self-review with /hnh-review-pr, fix findings, and post outcome. |
| **hnh-evolve-skill** | Give feedback about skill behavior, say "remember to always do X" | Evolve existing skills based on session feedback — parse corrections, find target skill, propose and apply changes. |
| **hnh-excalidraw** | Say "draw a diagram", "excalidraw", or ask for architecture/system diagrams | Programmatic Excalidraw canvas toolkit — create, edit, refine diagrams via MCP tools or REST API with real-time canvas sync. Supports ZenLabs branded diagram style (monochrome + green accent). |
| **hnh-score-sgs** | Say "score sgs", mention Sangousha, or share game scores | Calculate Sangousha (SGS) game session payment splits based on player scores and a total pot. |

## Repo structure

```
CLAUDE.md              # Global instructions (generic, public-safe)
skills/                # Custom skills
  hnh-add-knowledge/   #   Knowledge base manager
  hnh-backup/          #   Backup to GitHub with sanitization
  hnh-create-skill/    #   Skill creation & evaluation
  hnh-design-guideline/ #  ZenLabs brand design system (colors, fonts, logos)
  hnh-dify/            #   Dify.ai workflow & knowledge base interaction
  hnh-discord/         #   Discord interaction via Bot API
  hnh-facebook-manual/ #   Facebook browser automation via Chrome Claude Extension
  hnh-gg-docs/         #   Google Docs interaction via API
  hnh-gg-drive/        #   Google Drive file management via API
  hnh-gg-sheets/       #   Google Sheets interaction via API
  hnh-maintain-skills/ #   Skill ecosystem scanner & fixer
  hnh-notion/          #   Notion workspace interaction via API
  hnh-plan/            #   Implementation planning (plain text, shared workflow)
  hnh-plan-jira/       #   Implementation planning (from Jira ticket)
  hnh-plan-notion/     #   Implementation planning (from Notion page)
  hnh-report-sentry/   #   Sentry issue investigation & triage
  hnh-review-pr/       #   PR review with parallel agents
  hnh-setup/           #   Workspace bootstrapping
  hnh-wbs/             #   CTO-level WBS generator with branded PDF
  hnh-get-report/      #   CEO-level project status report generator
  hnh-record-screen/   #   Screen recording & video optimization
  hnh-aws/             #   AWS infrastructure (S3, ECR, RDS, CloudWatch, IAM)
  hnh-k8s/             #   Kubernetes/EKS debugging & monitoring
  hnh-document-demo/   #   Build session → shareable demo document
  hnh-zenlabs-infras/  #   Real-time infrastructure health report
  hnh-zenlabs-release/ #   CI/CD pipeline setup & deployment
  hnh-create-pr/       #   Session → PR with self-review
  hnh-evolve-skill/    #   Evolve skills from feedback
  hnh-excalidraw/      #   Excalidraw diagram toolkit (MCP + REST)
  hnh-score-sgs/       #   Sangousha game score calculator
memory/                # Persistent memory (preferences, indexes)
config/                # Portable config files (statusline)
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
