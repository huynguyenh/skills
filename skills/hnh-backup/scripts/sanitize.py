#!/usr/bin/env python3
"""
Sanitize backup files by removing credentials and replacing device-specific paths.

Usage:
    python3 sanitize.py <repo_directory>

Replaces:
    - /Users/<actual_username>/ → /Users/hnh/
    - API tokens, secrets, bearer tokens → <REDACTED>
    - Email addresses → <email>
    - Company/org-specific identifiers → generic placeholders
    - Strips entire sections from MEMORY.md that contain sensitive info
"""

import os
import re
import sys
from pathlib import Path


def get_username():
    return os.environ.get("USER", os.environ.get("USERNAME", "unknown"))


def get_github_work_username():
    """Read GITHUB_WORK_USERNAME from ~/.zshrc so it's not hardcoded here."""
    zshrc = Path.home() / ".zshrc"
    if zshrc.exists():
        for line in zshrc.read_text().splitlines():
            m = re.match(r'export\s+GITHUB_WORK_USERNAME\s*=\s*["\']?([^"\'#\s]+)', line)
            if m:
                return m.group(1)
    return None


# Sections in MEMORY.md that contain company/credential info and should be stripped.
MEMORY_STRIP_SECTIONS = [
    "API Credentials",
    "Sentry",
    "Google Drive",
    "Service Mapping",
    "Rules & Conventions",
]

# Company/org-specific identifiers to redact across all files
ORG_REDACT_PATTERNS = [
    (re.compile(r'[a-z0-9-]+\.sentry\.io'), '<sentry-url>'),
    (re.compile(r'SENTRY_ORG=<redacted>'), 'SENTRY_ORG=<redacted>'),
    (re.compile(r'i-destiny-\d+'), '<gcp-project>'),
    (re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'), '<email>'),
]

# Patterns that indicate a credential value to redact
CREDENTIAL_PATTERNS = [
    (r'((?:API_TOKEN|AUTH_TOKEN|ACCESS_TOKEN|SECRET_KEY|API_KEY|GH_TOKEN|GITHUB_TOKEN)\s*[=:]\s*)["\']?([A-Za-z0-9_\-/.+=]{20,})["\']?',
     r'\1<REDACTED>'),
    (r'(Bearer\s+)[A-Za-z0-9_\-/.+=]{20,}',
     r'\1<REDACTED>'),
    (r'(ghp_|gho_|github_pat_)[A-Za-z0-9_]{20,}',
     r'<REDACTED>'),
    (r'(token["\s]*[=:]["\s]*)[A-Za-z0-9_\-/.+=]{30,}',
     r'\1<REDACTED>'),
    (r'(Authorization:\s*(?:Bearer|token)\s+)[A-Za-z0-9_\-/.+=]{20,}',
     r'\1<REDACTED>'),
]

TEXT_EXTENSIONS = {
    '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.cfg', '.ini',
    '.sh', '.bash', '.zsh', '.py', '.rb', '.js', '.ts', '.go',
    '.env', '.conf', '.xml', '.html', '.css', ''
}

SKIP_FILES = {
    '.git', '.DS_Store', 'node_modules', '__pycache__',
}


def is_text_file(path):
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    if path.suffix == '':
        try:
            with open(path, 'rb') as f:
                chunk = f.read(512)
                return b'\x00' not in chunk
        except (IOError, OSError):
            return False
    return False


def strip_memory_sections(content):
    """Strip entire sections from MEMORY.md that contain sensitive info."""
    changes = []
    lines = content.split('\n')
    result_lines = []
    skip_until_level = None

    for line in lines:
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()

            if skip_until_level is not None and level <= skip_until_level:
                skip_until_level = None

            if any(section.lower() in title.lower() for section in MEMORY_STRIP_SECTIONS):
                skip_until_level = level
                changes.append("Stripped section: '{}'".format(title))
                continue

        if skip_until_level is not None:
            continue

        result_lines.append(line)

    cleaned = re.sub(r'\n{3,}', '\n\n', '\n'.join(result_lines))
    return cleaned, changes


def sanitize_content(content, username):
    changes = []
    result = content

    user_path = "/Users/{}/".format(username)
    if user_path in result and username != "hnh":
        count = result.count(user_path)
        result = result.replace(user_path, "/Users/hnh/")
        changes.append("Replaced {} path(s): /Users/{}/ -> /Users/hnh/".format(count, username))

    home_dir = os.path.expanduser("~")
    if home_dir + "/" in result and home_dir != "/Users/hnh":
        count = result.count(home_dir + "/")
        result = result.replace(home_dir + "/", "/Users/hnh/")
        changes.append("Replaced {} home dir path(s)".format(count))

    gh_work_user = get_github_work_username()
    if gh_work_user and gh_work_user in result:
        count = result.count(gh_work_user)
        result = result.replace(gh_work_user, "{github_work_username}")
        changes.append("Replaced {} GitHub work username(s)".format(count))

    for pattern, replacement in ORG_REDACT_PATTERNS:
        matches = pattern.findall(result)
        if matches:
            result = pattern.sub(replacement, result)
            changes.append("Redacted {} org-specific pattern(s): {}".format(len(matches), replacement))

    for pattern, replacement in CREDENTIAL_PATTERNS:
        matches = re.findall(pattern, result)
        if matches:
            result = re.sub(pattern, replacement, result)
            changes.append("Redacted credential matching: {}...".format(pattern[:40]))

    return result, changes


def sanitize_repo(repo_dir):
    repo_path = Path(repo_dir)
    username = get_username()

    if not repo_path.exists():
        print("Error: Directory {} does not exist".format(repo_dir))
        sys.exit(1)

    print("Sanitizing {}".format(repo_dir))
    print("Username to replace: {}".format(username))
    print()

    # Special handling for MEMORY.md — strip sensitive sections first
    memory_path = repo_path / "memory" / "MEMORY.md"
    if memory_path.exists():
        content = memory_path.read_text(encoding='utf-8')
        stripped, strip_changes = strip_memory_sections(content)
        if strip_changes:
            memory_path.write_text(stripped, encoding='utf-8')
            print("  MEMORY.md section stripping:")
            for change in strip_changes:
                print("    - {}".format(change))

    total_files = 0
    modified_files = 0
    all_changes = []
    warnings = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_FILES]

        for filename in files:
            if filename in SKIP_FILES:
                continue

            filepath = Path(root) / filename

            if not is_text_file(filepath):
                continue

            total_files += 1

            try:
                content = filepath.read_text(encoding='utf-8')
            except (UnicodeDecodeError, IOError):
                continue

            sanitized, changes = sanitize_content(content, username)

            if changes:
                filepath.write_text(sanitized, encoding='utf-8')
                modified_files += 1
                rel_path = filepath.relative_to(repo_path)
                all_changes.append((str(rel_path), changes))
                print("  Modified: {}".format(rel_path))
                for change in changes:
                    print("    - {}".format(change))

    print()
    print("Scanned {} files, modified {}".format(total_files, modified_files))

    if warnings:
        print()
        print("WARNINGS:")
        for w in warnings:
            print("  ! {}".format(w))

    return modified_files, all_changes, warnings


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} <repo_directory>".format(sys.argv[0]))
        sys.exit(1)

    sanitize_repo(sys.argv[1])
