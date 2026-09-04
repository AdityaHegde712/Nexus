---
name: codebase-curator
description: >-
  Generate comprehensive, high-signal CODEBASE.md files, architecture overviews, Excalidraw
  JSON diagrams, and technical documentation. Use whenever a user asks to document, map, or
  explain a codebase, onboard new developers or AI agents, generate architecture blueprints,
  perform post-reorganization reference audits, or synthesize bulk code into structured context.
  Output is structured for both human engineers and AI coding agents.
---

# Codebase Curator Skill

Produces authoritative, high-signal documentation (`CODEBASE.md`, `ARCHITECTURE.md`, or architecture diagrams) at the repository root or docs directory. Documentation serves two audiences simultaneously: human engineers onboarding to the system and AI coding agents requiring persistent, high-density context between sessions.

Read [references/sections.md](references/sections.md) for the section-by-section authoring blueprint.
Read [references/quality.md](references/quality.md) before finalizing output.
Read [references/diagrams.md](references/diagrams.md) when generating Mermaid or Excalidraw JSON diagrams.

---

## Workflow

### Step 1 — Gather Facts Before Writing

Execute factual discovery commands from the repository root. Never author a section based on assumptions; inspect actual repository files and configurations first.

#### Cross-Platform / PowerShell Discovery Commands

```powershell
# 1. Directory Tree (Top 2-3 levels, excluding noise)
Get-ChildItem -Directory -Depth 2 | Where-Object { $_.FullName -notmatch '[\\/](\.git|node_modules|__pycache__|dist|build|\.venv|\.tox|coverage)[\\/]' } | Select-Object -ExpandProperty FullName

# 2. Language & Framework Fingerprints
Get-ChildItem -Path . -Include package.json,pyproject.toml,Cargo.toml,go.mod,pom.xml,build.gradle,requirements.txt,setup.py,Makefile,Dockerfile,docker-compose.yml -File -Recurse -Depth 2 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName

# 3. Entry Points & Main Scripts
Get-ChildItem -Path . -Recurse -Include *.py,*.ts,*.js,*.go,*.rs -Depth 3 | Select-String -Pattern '(if __name__ == .__main__.|"main"|bootstrap|createServer|app\.listen)' -List | Select-Object -ExpandProperty Path -Unique | Select-Object -First 10

# 4. Dependency Manifests & Scripts
Get-Content package.json -ErrorAction SilentlyContinue | ConvertFrom-Json | Select-Object -ExpandProperty scripts
Get-Content package.json -ErrorAction SilentlyContinue | ConvertFrom-Json | Select-Object -ExpandProperty dependencies
Get-Content pyproject.toml -ErrorAction SilentlyContinue | Select-String -Pattern '(\[project\.dependencies\]|\[tool\.poetry\.dependencies\])' -Context 0,20

# 5. Test Suites & Fixtures
Get-ChildItem -Path . -Recurse -Include *test*,*spec*,conftest.py -Depth 3 | Where-Object { $_.FullName -notmatch '[\\/](\.git|node_modules)[\\/]' } | Select-Object -ExpandProperty FullName -First 15

# 6. CI/CD & Existing Docs
Get-ChildItem -Path .github/workflows,docs,README.md,CONTRIBUTING.md,ARCHITECTURE.md,AGENTS.md -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
```

#### Mandatory Direct File Inspections
Inspect the following files directly if present:
- `README.md` — project intent and public description.
- `AGENTS.md` / `CLAUDE.md` — active agent directives (do not duplicate rules; reference them).
- `docker-compose.yml` / infrastructure manifests — service relationships, backing databases, ports.
- Top 5–10 internal imports (e.g. `from . import`, `require('../')`, `import { ... } from '@/...'`).

---

### Step 2 — Classify the Codebase

Determine the operational profile before drafting:

| Dimension | Classification Options | Impact on Documentation |
| :--- | :--- | :--- |
| **Architecture Style** | Monolith / Modular Monolith / Microservices / CLI / Library / Serverless | Framing & component boundaries |
| **Runtime & Core Language** | Python 3.12, Node 22/TS, Go 1.22, Rust 2021 | Tech stack constraints and syntax conventions |
| **Persistence & Messaging** | Postgres, SQLite, Redis, Kafka, RabbitMQ, None | Data layer, transactions, async boundaries |
| **Test & CI Rigor** | Unit, integration, E2E (Playwright/Cypress), GitHub Actions | Development workflow and quality gates |
| **Target Audience** | Core maintainers, open-source contributors, AI subagents | Depth, warning explicitness, and tone |

*If the repository is a monorepo, consult the Monorepo Addendum in `references/sections.md`.*

---

### Step 3 — Author High-Signal Documentation

Follow the 12-section standard defined in [references/sections.md](references/sections.md).

#### Signal-to-Noise Directives
- **Zero Filler**: Eliminate generic claims (e.g., "built using modern best practices").
- **Explicit Constraints**: Document non-obvious tripwires, async deadlocks, soft-delete policies, and lifecycle hooks.
- **Traceable File Paths**: Every cited module or file must use exact project-relative paths.
- **Length Targets**:
  - Small libraries / CLIs: 100–200 lines.
  - Single-service backends / SPAs: 200–350 lines.
  - Multi-service full-stack apps: 300–500 lines.
  - Monorepos: 400–600 lines (with linked sub-docs).

---

### Step 4 — Author Architectural Diagrams

Select the appropriate visual format per [references/diagrams.md](references/diagrams.md):
- **Mermaid Diagrams (`graph LR` / `sequenceDiagram`)**: Inline in markdown for request flows and component topologies (capped at ≤12 nodes).
- **Excalidraw JSON Diagrams**: When structured, editable, multi-layered visual architecture files (`.excalidraw`) are required for persistent system design reviews.

---

### Step 5 — Run Quality Checklist & Link Audit

Before saving:
1. Run all pass/fail checks in [references/quality.md](references/quality.md).
2. **Reference Auditing**: Verify that every referenced path, script command, and environment variable accurately exists in the repository.
3. If renaming or moving files, update all inbound links across documentation.

---

### Step 6 — Save and Report

Write the output file (e.g., `CODEBASE.md` at the repo root or `docs/architecture/ARCHITECTURE.md`).
Report to the user:
- Exact path of generated documentation.
- Included sections summary.
- Deliberately skipped sections and technical rationale.
- Staleness risk items requiring human review during future refactors.

---

## Anti-Patterns to Avoid

- **Directory Tree as Content**: Never dump raw `tree` or directory listings into documentation.
- **Auto-Generated Fluff**: Cut vacuous statements that convey no concrete constraints.
- **Stale Path Bloat**: Only reference stable, load-bearing paths; describe dynamic subsystems functionally.
- **Duplicating README**: Complement `README.md` with internal architectural realities, never mirror it.
- **Vague Warnings**: Always state explicit consequences (e.g., "Never call sync DB queries in handlers—causes event loop deadlock").
