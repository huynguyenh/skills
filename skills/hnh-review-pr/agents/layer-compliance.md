# Agent G: Layer Compliance Check

Verify that new/modified code respects the repository's architectural layering — each layer does its job and nothing else. This catches violations like database calls in handlers, HTTP parsing in controllers, or business logic in repositories.

## Before reviewing

1. **Read `CLAUDE.md`** at the repo root — it defines the project's layers, their responsibilities, and initialization order. This is your source of truth for what each layer is allowed to do.
2. **Read 2-3 existing files** in the same package/directory as each changed file to understand established patterns. If the PR adds a new handler, read an existing handler in the same project. If it adds a new repository method, read the existing methods.
3. **Check `~/.claude/memory/`** for any convention files for this project.

## What to check

### 1. Layer boundary violations (most important)

Each layer has strict boundaries. Flag any code that crosses them:

| Layer | Allowed | NOT allowed |
|-------|---------|-------------|
| **Handler** | Parse HTTP request, call controller, return response | Call repository/DB directly, business logic, data transformation beyond simple mapping |
| **Controller** | Business logic, validation, orchestration, call repository | Parse HTTP (gin.Context), return HTTP responses, raw SQL |
| **Repository** | GORM/SQL queries, ORM ↔ model conversion | Business logic, HTTP awareness, calling external services |
| **Service** | External service calls (email, webhooks, notifications) | Direct DB access, HTTP parsing |
| **Cronjob/CLI** | Wire dependencies, call controller or repository | Inline business logic, direct SQL without going through repository |
| **Models** | Data structures, conversion methods (ToModel/FromModel) | Business logic, DB queries, HTTP |

For each changed file, identify which layer it belongs to and check every function call, import, and dependency against the table above.

### 2. CLAUDE.md convention compliance

Read the project's CLAUDE.md and check:
- Does the code follow the documented initialization order?
- Does it use the documented patterns (constructor injection, interface-based deps)?
- Does it match the documented naming conventions?
- If CLAUDE.md says "use X for Y" (e.g., "use repository.NewDB for DB connections"), does the code comply?

### 3. Reuse vs reinvention

Search the codebase for existing utilities that the PR code could reuse:
- Does the project already have a package/function that does what the new code does?
- Is the PR creating a new helper that duplicates an existing one?
- Is the PR importing a new dependency when the project already has an equivalent?
- If the PR adds a new repository method, does a similar query already exist in another repository?

**How to search:** For each non-trivial function in the PR, grep the codebase for its key operations (DB table names, function signatures, import paths) to find existing implementations.

### 4. Dependency direction

Check that dependencies flow in the correct direction:
- Handler → Controller → Repository (never reversed)
- Concrete types at the edges (handler, main), interfaces in the middle (controller depends on repository interface, not concrete struct)
- No circular imports between packages

## Common violations to watch for

- **`*gorm.DB` in a controller or handler** — DB access belongs in repository
- **`*gin.Context` in a controller** — HTTP belongs in handler
- **`json.Marshal` in a repository** — data transformation belongs in controller or handler
- **Raw SQL in a controller** — queries belong in repository
- **`time.Now()` deep in repository** — business time should be passed as parameter from controller
- **`fmt.Errorf("HTTP 400...")` in a repository** — HTTP status awareness belongs in handler
- **Direct struct construction of ORM models outside repository** — ORM ↔ domain conversion belongs in repository or model's ToModel/FromModel methods
- **Standalone binary (cmd/) with inline business logic** — should call controller or repository, not implement logic directly

## Output format

For each finding:
- **Category**: `CRITICAL` (layer violation), `WARNING` (convention mismatch), `SUGGESTION` (reuse opportunity)
- **File path** from project root
- **Line number(s)**
- **Violation**: which layer rule is broken (e.g., "handler calls DB directly")
- **Evidence**: the specific code that violates the rule
- **Fix**: where the code should live instead, with a concrete suggestion
