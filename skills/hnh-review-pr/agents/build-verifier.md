# Agent B: Build Verifier

Verify that the PR branch builds and tests pass locally. Focus on the affected service(s) only — don't build the entire monorepo if only one service changed.

## Steps

1. Check if the repo exists locally at `~/ws/code/github.com/{owner}/{repo}/`
2. If not, clone it: `gh repo clone {owner}/{repo} ~/ws/code/github.com/{owner}/{repo}/`
3. Fetch and checkout the PR branch. If the PR is already merged and the branch is deleted, checkout the merge commit instead:
   ```bash
   gh pr view {pr_number} --repo {owner}/{repo} --json mergeCommit
   ```
4. Identify the build system by looking for: `Makefile`, `docker-compose.yml`, `package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`, etc.
5. Build the affected service(s):
   - Go: `go build ./...`
   - Node: `npm install && npm run build`
   - Python: `pip install -e . && python -m pytest`
   - Rust: `cargo build`
6. Run tests for the affected service(s) with a 5-minute timeout
7. If build or test commands require Docker or external services that aren't available, note that and report what you could verify

## Output

Report:
- **Build**: PASS or FAIL (with error details)
- **Unit tests**: PASS or FAIL (with failure details)
- **Integration tests**: PASS, FAIL, or SKIPPED (note if skipped due to missing infrastructure)
- **Warnings**: any compiler/linter warnings
