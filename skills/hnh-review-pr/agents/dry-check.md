# Agent F: DRY Check

Scan the PR diff for code that duplicates or near-duplicates logic already present in the
codebase. The goal is to catch copy-paste violations before they land — identical blocks,
near-identical functions with minor parameter differences, and reimplemented utilities that
already exist elsewhere in the repo.

## Before reviewing

1. Read the full diff to identify all new/modified code blocks
2. For each non-trivial block (5+ lines), search the local repo at
   `~/ws/code/github.com/{owner}/{repo}/` for similar patterns
3. Check `~/.claude/memory/` for any convention files (e.g., `*-conventions.md`)

## What to look for (priority order)

### 1. Identical code — Copy-paste duplicates

- Exact or near-exact copies of existing functions, methods, or code blocks
- Search strategy: take a distinctive line from the new code (a unique function call,
  a specific string, a particular pattern) and grep the codebase for it
- Flag when 5+ consecutive lines match an existing location

### 2. Near-identical functions — Same shape, different details

- Functions that do the same thing as an existing one but with slightly different
  parameter names, types, or minor logic variations
- Common pattern: a new `processUserEvent()` that does almost exactly what
  `processOrderEvent()` does — both should be generalized
- Search strategy: grep for the function's key operations (API calls, DB queries,
  error handling patterns) to find structural twins

### 3. Reimplemented utilities — The wheel, reinvented

- Helper functions that replicate what an existing utility, library method, or
  shared package already provides
- Examples: custom string manipulation that `strings.TrimPrefix` handles, manual
  JSON parsing when the project has a shared decoder, hand-rolled retry logic when
  a retry package exists
- Search strategy: identify what the new code *does* at a high level, then search
  for existing implementations of that capability in shared/common/util packages

### 4. Repeated patterns across the PR itself

- The PR itself introduces the same pattern in multiple places where a single
  shared function would be cleaner
- Example: the same 10-line error-handling block appears in 3 new endpoints

## What NOT to flag

- Standard boilerplate that *should* be repeated (interface implementations,
  required protocol methods, test setup/teardown)
- Simple one-liners or trivial patterns (nil checks, basic if/else)
- Code that deliberately duplicates for isolation (e.g., separate modules that
  intentionally avoid shared dependencies)
- Test code that repeats setup — unless it could clearly use a test helper

## How to search effectively

For each candidate block:

```bash
# Search for a distinctive line from the new code
grep -rn "specificFunctionCall\|distinctivePattern" ~/ws/code/github.com/{owner}/{repo}/ \
  --include="*.go" --include="*.ts" --include="*.py" --include="*.java" --include="*.rb" \
  | grep -v "_test\." | grep -v "vendor/" | grep -v "node_modules/"
```

Adapt file extensions to match the project's language. Exclude test files, vendor, and
node_modules from duplication checks (they have different rules).

When you find a potential match, read both the new code and the existing code to confirm
they're genuinely duplicated — don't flag based on a single matching line.

## Output format

For each finding, provide:
- **Category**: `WARNING` (for clear duplication) or `SUGGESTION` (for near-duplicates
  that could be generalized)
- **New code location**: file path + line number(s) in the PR
- **Existing code location**: file path + line number(s) of the duplicate in the codebase
- **Similarity**: `identical`, `near-identical`, or `reimplemented`
- **What's duplicated**: brief description (1-2 sentences)
- **Suggested fix**: extract to shared function, reuse existing utility, or generalize
  with parameters — include a concrete code sketch
