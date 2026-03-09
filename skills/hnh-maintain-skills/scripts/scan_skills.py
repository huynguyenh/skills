#!/usr/bin/env python3
"""
Scan all custom skills and detect improvement opportunities.

Checks for:
1. Raw API calls that a dedicated skill already wraps (e.g., curl to Notion when hnh-notion exists)
2. Stale file references (paths that don't exist)
3. Cross-skill dependency opportunities
4. Inconsistent credential handling patterns

Usage:
    python3 scan_skills.py [--skills-dir ~/.claude/skills] [--verbose]

Output: JSON report to stdout with categorized findings.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def strip_code_blocks(text):
    """Remove content inside markdown fenced code blocks (``` ... ```)."""
    return re.sub(r"```[\s\S]*?```", "[CODE_BLOCK]", text)


def find_custom_skills(skills_dir):
    """Find all hnh-* skill directories."""
    skills = {}
    for entry in sorted(Path(skills_dir).iterdir()):
        if entry.is_dir() and entry.name.startswith("hnh-"):
            skills[entry.name] = entry
    return skills


def read_skill_files(skill_path):
    """Read SKILL.md and all script/agent files for a skill."""
    files = {}
    for root, _, filenames in os.walk(skill_path):
        for fname in filenames:
            fpath = Path(root) / fname
            rel = str(fpath.relative_to(skill_path))
            try:
                files[rel] = fpath.read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass
    return files


def build_capability_registry(all_skills):
    """Build a map of what API/service each skill wraps."""
    registry = {}

    # Known API wrappers — skill name -> patterns it handles
    api_wrappers = {
        "hnh-notion": {
            "service": "Notion API",
            "cli_tool": "~/.claude/skills/hnh-notion/scripts/notion.py",
            "api_patterns": [
                r"curl\s+.*api\.notion\.com",
                r"https?://api\.notion\.com",
                r"Notion-Version:\s*\d{4}",
            ],
            "capabilities": [
                "read pages", "create pages", "update pages", "append content",
                "query databases", "schema", "search", "create-record", "update-record",
            ],
        },
        "hnh-gg-sheets": {
            "service": "Google Sheets & Drive API",
            "cli_tool": "~/.claude/skills/hnh-gg-sheets/scripts/sheets.py",
            "api_patterns": [
                r"curl\s+.*googleapis\.com/.*sheets",
                r"curl\s+.*googleapis\.com/.*drive",
                r"sheets\.googleapis\.com",
                r"drive\.googleapis\.com",
            ],
            "capabilities": [
                "create spreadsheet", "read spreadsheet", "write spreadsheet",
                "format cells", "share", "search sheets",
            ],
        },
    }

    for skill_name, info in api_wrappers.items():
        if skill_name in all_skills:
            registry[skill_name] = info

    return registry


def detect_raw_api_calls(skill_name, skill_files, registry):
    """Find raw API calls in a skill that a dedicated wrapper skill already handles."""
    findings = []

    # Skip the maintain-skills skill itself (it contains examples of what it detects)
    if skill_name == "hnh-maintain-skills":
        return findings

    for wrapper_skill, info in registry.items():
        if skill_name == wrapper_skill:
            continue  # Don't flag the wrapper skill itself

        for rel_path, content in skill_files.items():
            # For raw API call detection, scan everything including code blocks.
            # In SKILL.md files, code blocks contain the actual commands Claude will run —
            # that's exactly where we want to catch raw curl calls to wrapped APIs.
            scan_content = content
            seen_lines = set()
            for pattern in info["api_patterns"]:
                matches = re.finditer(pattern, scan_content, re.IGNORECASE)
                for match in matches:
                    # Find approximate line number
                    line_num = content[:content.find(match.group(0))].count("\n") + 1
                    if line_num in seen_lines:
                        continue
                    seen_lines.add(line_num)
                    line_text = content.split("\n")[line_num - 1].strip()

                    findings.append({
                        "type": "raw_api_call",
                        "severity": "high",
                        "skill": skill_name,
                        "file": rel_path,
                        "line": line_num,
                        "line_text": line_text[:120],
                        "message": (
                            f"Raw {info['service']} call found — "
                            f"consider using {wrapper_skill}'s CLI tool "
                            f"({info['cli_tool']}) instead"
                        ),
                        "wrapper_skill": wrapper_skill,
                    })

    return findings


def detect_stale_references(skill_name, skill_files):
    """Find file path references that don't exist on disk."""
    findings = []

    # Pattern: ~/.claude/... paths or relative paths to other skills
    path_pattern = re.compile(r"~/.claude/[\w/\-\.]+(?:\.md|\.py|\.sh|\.json)")

    for rel_path, content in skill_files.items():
        for match in path_pattern.finditer(content):
            ref_path = match.group(0)
            expanded = os.path.expanduser(ref_path)

            if not os.path.exists(expanded):
                line_num = content[:match.start()].count("\n") + 1

                # Skip if it's inside a code example with placeholder
                line_text = content.split("\n")[line_num - 1].strip()
                if any(ph in line_text for ph in ["<script>", "<path", "example", "PARENT_ID", "PAGE_ID"]):
                    continue

                findings.append({
                    "type": "stale_reference",
                    "severity": "medium",
                    "skill": skill_name,
                    "file": rel_path,
                    "line": line_num,
                    "line_text": line_text[:120],
                    "message": f"Referenced path does not exist: {ref_path}",
                    "missing_path": ref_path,
                })

    return findings


def detect_credential_patterns(skill_name, skill_files):
    """Find inconsistent credential handling."""
    findings = []

    # Skip the maintain-skills skill (contains examples)
    if skill_name == "hnh-maintain-skills":
        return findings

    bad_patterns = [
        (r"source\s+~/\.zshrc", "Uses 'source ~/.zshrc' which doesn't persist in subshells"),
    ]

    for rel_path, content in skill_files.items():
        # Only check SKILL.md and agent files, not scripts
        if not rel_path.endswith(".md"):
            continue

        # Strip code blocks — $TOKEN in code examples is documentation, not a problem
        scan_content = strip_code_blocks(content)

        for pattern, message in bad_patterns:
            for match in re.finditer(pattern, scan_content):
                line_num = scan_content[:match.start()].count("\n") + 1
                line_text = content.split("\n")[min(line_num - 1, len(content.split("\n")) - 1)].strip()

                # Skip if it's in a "don't do this" context
                nearby = scan_content[max(0, match.start()-100):match.start()].lower()
                if any(w in nearby for w in ["don't", "do not", "never", "avoid", "not to", "wrong"]):
                    continue

                findings.append({
                    "type": "credential_pattern",
                    "severity": "low",
                    "skill": skill_name,
                    "file": rel_path,
                    "line": line_num,
                    "line_text": line_text[:120],
                    "message": message,
                })

    return findings


def detect_cross_skill_opportunities(skill_name, skill_files, all_skills):
    """Find opportunities for skills to reference each other."""
    findings = []

    # Check if a skill mentions Notion concepts but doesn't reference hnh-notion
    if skill_name != "hnh-notion" and "hnh-notion" in all_skills:
        for rel_path, content in skill_files.items():
            if not rel_path.endswith(".md"):
                continue

            # Does it talk about Notion?
            notion_mentions = len(re.findall(r"\bnotion\b", content, re.IGNORECASE))
            # Does it reference the notion skill?
            refs_notion_skill = bool(re.search(r"hnh-notion|notion\.py", content))

            if notion_mentions >= 3 and not refs_notion_skill:
                findings.append({
                    "type": "missing_cross_reference",
                    "severity": "medium",
                    "skill": skill_name,
                    "file": rel_path,
                    "message": (
                        f"Skill mentions Notion {notion_mentions} times but doesn't reference "
                        f"hnh-notion's CLI tool — consider using notion.py instead of raw API calls"
                    ),
                    "suggested_skill": "hnh-notion",
                })

    # Check if a skill mentions Google Sheets but doesn't reference hnh-gg-sheets
    # Skip hnh-create-skill — it mentions "spreadsheet" generically in eval schemas
    if skill_name not in ("hnh-gg-sheets", "hnh-create-skill") and "hnh-gg-sheets" in all_skills:
        for rel_path, content in skill_files.items():
            if not rel_path.endswith(".md"):
                continue

            sheets_mentions = len(re.findall(r"\b(?:google\s*sheet|spreadsheet|gsheet)\b", content, re.IGNORECASE))
            refs_sheets_skill = bool(re.search(r"hnh-gg-sheets|sheets\.py", content))

            if sheets_mentions >= 2 and not refs_sheets_skill:
                findings.append({
                    "type": "missing_cross_reference",
                    "severity": "medium",
                    "skill": skill_name,
                    "file": rel_path,
                    "message": (
                        f"Skill mentions Google Sheets/spreadsheets {sheets_mentions} times "
                        f"but doesn't reference hnh-gg-sheets"
                    ),
                    "suggested_skill": "hnh-gg-sheets",
                })

    return findings


def detect_duplicated_logic(all_skills, all_files):
    """Find patterns duplicated across multiple skills."""
    findings = []

    # Check for duplicate inline scripts or helpers
    # (e.g., multiple skills implementing the same JSON parsing logic)

    # Check for skills that could share agent files
    agent_patterns = {}
    for skill_name, files in all_files.items():
        for rel_path, content in files.items():
            if "/agents/" in rel_path and rel_path.endswith(".md"):
                # Hash the first 200 chars as a rough similarity check
                sig = content[:200].strip()
                if sig in agent_patterns:
                    findings.append({
                        "type": "duplicated_agent",
                        "severity": "low",
                        "skill": skill_name,
                        "file": rel_path,
                        "message": (
                            f"Agent file appears similar to "
                            f"{agent_patterns[sig]['skill']}/{agent_patterns[sig]['file']}"
                        ),
                    })
                else:
                    agent_patterns[sig] = {"skill": skill_name, "file": rel_path}

    return findings


def run_scan(skills_dir, verbose=False):
    """Run all checks and produce a report."""
    skills_dir = os.path.expanduser(skills_dir)
    all_skills = find_custom_skills(skills_dir)

    if verbose:
        print(f"Found {len(all_skills)} custom skills: {', '.join(all_skills.keys())}", file=sys.stderr)

    # Read all skill files
    all_files = {}
    for name, path in all_skills.items():
        all_files[name] = read_skill_files(path)

    # Build capability registry
    registry = build_capability_registry(all_skills)

    if verbose:
        print(f"API wrapper skills: {', '.join(registry.keys())}", file=sys.stderr)

    # Run all detectors
    all_findings = []

    for skill_name, files in all_files.items():
        all_findings.extend(detect_raw_api_calls(skill_name, files, registry))
        all_findings.extend(detect_stale_references(skill_name, files))
        all_findings.extend(detect_credential_patterns(skill_name, files))
        all_findings.extend(detect_cross_skill_opportunities(skill_name, files, all_skills))

    all_findings.extend(detect_duplicated_logic(all_skills, all_files))

    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    all_findings.sort(key=lambda f: (severity_order.get(f["severity"], 3), f["skill"]))

    # Build report
    report = {
        "skills_scanned": len(all_skills),
        "skill_names": sorted(all_skills.keys()),
        "api_wrappers": {k: v["service"] for k, v in registry.items()},
        "total_findings": len(all_findings),
        "by_severity": {
            "high": len([f for f in all_findings if f["severity"] == "high"]),
            "medium": len([f for f in all_findings if f["severity"] == "medium"]),
            "low": len([f for f in all_findings if f["severity"] == "low"]),
        },
        "findings": all_findings,
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="Scan skills for improvement opportunities")
    parser.add_argument("--skills-dir", default="~/.claude/skills", help="Skills directory")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    report = run_scan(args.skills_dir, verbose=args.verbose)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
