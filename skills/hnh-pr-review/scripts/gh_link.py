#!/usr/bin/env python3
"""
Generate GitHub PR file-view links with correct diff anchors.

Usage:
    python3 gh_link.py <owner> <repo> <pr_number> <filepath> <line>
    python3 gh_link.py owner repo 1234 path/to/file.go 42

Output:
    https://github.com/owner/repo/pull/1234/files#diff-<sha256>R42
"""

import hashlib
import sys


def pr_file_link(owner: str, repo: str, pr_number: int, filepath: str, line: int) -> str:
    anchor = hashlib.sha256(filepath.encode()).hexdigest()
    return f"https://github.com/{owner}/{repo}/pull/{pr_number}/files#diff-{anchor}R{line}"


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(f"Usage: {sys.argv[0]} <owner> <repo> <pr_number> <filepath> <line>")
        sys.exit(1)

    owner, repo, pr_number, filepath, line = sys.argv[1:]
    print(pr_file_link(owner, repo, int(pr_number), filepath, int(line)))
