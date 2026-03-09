#!/usr/bin/env python3
"""
Sanitize backup files by removing credentials and replacing device-specific paths.

Usage:
    python3 sanitize.py <repo_directory>

Replaces:
    - /Users/<actual_username>/ → /Users/hnh/
    - API tokens, secrets, bearer tokens → <REDACTED>
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


# Patterns that indicate a credential value to redact
CREDENTIAL_PATTERNS = [
    # API tokens in key=value or key: value format
    (r'((?:API_TOKEN|AUTH_TOKEN|ACCESS_TOKEN|SECRET_KEY|API_KEY|GH_TOKEN|GITHUB_TOKEN)\s*[=:]\s*)["\']?([A-Za-z0-9_\-/.+=]{20,})["\']?',
     r'\1<REDACTED>'),
    # Bearer tokens
    (r'(Bearer\s+)[A-Za-z0-9_\-/.+=]{20,}',
     r'\1<REDACTED>'),
    # GitHub PATs
    (r'(ghp_|gho_|github_pat_)[A-Za-z0-9_]{20,}',
     r'<REDACTED>'),
    # Generic token= patterns (be conservative — only long values)
    (r'(token["\s]*[=:]["\s]*)[A-Za-z0-9_\-/.+=]{30,}',
     r'\1<REDACTED>'),
    # curl -H "Authorization: ..." headers
    (r'(Authorization:\s*(?:Bearer|token)\s+)[A-Za-z0-9_\-/.+=]{20,}',
     r'\1<REDACTED>'),
]

# File extensions to process (skip binaries)
TEXT_EXTENSIONS = {
    '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.cfg', '.ini',
    '.sh', '.bash', '.zsh', '.py', '.rb', '.js', '.ts', '.go',
    '.env', '.conf', '.xml', '.html', '.css', ''
}

# Files to skip entirely
SKIP_FILES = {
    '.git', '.DS_Store', 'node_modules', '__pycache__',
}


def is_text_file(path: Path) -> bool:
    """Check if a file should be processed as text."""
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    # No extension — check if it looks like text
    if path.suffix == '':
        try:
            with open(path, 'rb') as f:
                chunk = f.read(512)
                return b'\x00' not in chunk  # binary files usually have null bytes
        except (IOError, OSError):
            return False
    return False


def sanitize_content(content: str, username: str) -> tuple[str, list[str]]:
    """
    Sanitize file content. Returns (sanitized_content, list_of_changes).
    """
    changes = []
    result = content

    # Replace username in paths
    user_path = f"/Users/hnh/"
    if user_path in result:
        count = result.count(user_path)
        result = result.replace(user_path, "/Users/hnh/")
        changes.append(f"Replaced {count} path(s): /Users/hnh/ → /Users/{hnh}/")

    # Also catch ~ expansions that resolved to the full path
    home_dir = os.path.expanduser("~")
    if home_dir + "/" in result and home_dir != f"/Users/hnh":
        count = result.count(home_dir + "/")
        result = result.replace(home_dir + "/", "/Users/hnh/")
        changes.append(f"Replaced {count} home dir path(s)")

    # Strip work/org GitHub username (read dynamically from ~/.zshrc)
    gh_work_user = get_github_work_username()
    if gh_work_user and gh_work_user in result:
        count = result.count(gh_work_user)
        result = result.replace(gh_work_user, "{github_work_username}")
        changes.append(f"Replaced {count} GitHub work username(s) → {{github_work_username}}")

    # Apply credential patterns
    for pattern, replacement in CREDENTIAL_PATTERNS:
        matches = re.findall(pattern, result)
        if matches:
            result = re.sub(pattern, replacement, result)
            changes.append(f"Redacted credential matching: {pattern[:40]}...")

    return result, changes


def sanitize_repo(repo_dir: str):
    """Walk the repo directory and sanitize all text files."""
    repo_path = Path(repo_dir)
    username = get_username()

    if not repo_path.exists():
        print(f"Error: Directory {repo_dir} does not exist")
        sys.exit(1)

    print(f"Sanitizing {repo_dir}")
    print(f"Username to replace: hnh")
    print()

    total_files = 0
    modified_files = 0
    all_changes = []
    warnings = []

    for root, dirs, files in os.walk(repo_path):
        # Skip .git and other irrelevant dirs
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
                print(f"  Modified: {rel_path}")
                for change in changes:
                    print(f"    - {change}")

    print()
    print(f"Scanned {total_files} files, modified {modified_files}")

    if warnings:
        print()
        print("WARNINGS:")
        for w in warnings:
            print(f"  ! {w}")

    return modified_files, all_changes, warnings


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <repo_directory>")
        sys.exit(1)

    sanitize_repo(sys.argv[1])
