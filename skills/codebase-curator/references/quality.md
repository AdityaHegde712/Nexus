# Quality Checklist & Staleness Risk Reference

Run this evaluation protocol before saving or updating `CODEBASE.md`, `ARCHITECTURE.md`, or architecture diagrams.

---

## 1. Content Quality Verification Checklist

Every item must pass before marking the documentation complete:

| Check | Pass Verification Criteria |
| :--- | :--- |
| **Capability Header** | Describes what the system executes and delivers, not marketing or buzzwords. |
| **Zero Directory Dumps** | Contains no raw directory listings or shallow file lists without contextual annotations. |
| **Load-Bearing Paths** | Every cited file path exists in the repository and represents a high-gravity module. |
| **Non-Obvious Patterns** | Contains ≥3 concrete, counterintuitive rules, error handling models, or concurrency patterns. |
| **Explicit Danger Zones** | High-risk files (auth, middleware, billing, DB triggers) have explicit warning callouts. |
| **Copy-Pasteable Commands** | All setup, test, and lint commands include all necessary flags and are tested against the actual shell environment. |
| **Diagram Constraints** | Mermaid diagrams contain ≤12 nodes; Excalidraw diagrams follow layer standards. |
| **Tech Stack Notes** | Every technology listed includes real constraints and version details in the Notes column. |
| **No README Duplication** | Focuses on internal architecture, state flow, and invariants rather than public marketing summaries. |

---

## 2. Staleness Risk Matrix

Always include a Staleness Risk summary in the final report to flag items prone to drift during active refactoring:

| Risk Category | Drift Trigger | Mitigation / Audit Protocol |
| :--- | :--- | :--- |
| **Specific File Paths** | Renames, extractions, modular refactors | Audit paths with `Get-ChildItem` / ripgrep on each major version. |
| **Database Tables & Schemas** | Migrations, column alterations | Verify against latest ORM models or migration directory. |
| **Port Numbers & Endpoints** | Config file updates, container changes | Cross-reference with `docker-compose.yml` and `.env.example`. |
| **Package Names / Monorepo Layout** | Package splits, workspace restructuring | Verify root `package.json` workspaces or `pnpm-workspace.yaml`. |
| **CI Workflow Names** | GitHub Actions YAML renames | Inspect `.github/workflows/` directory directly. |

---

## 3. Length Calibration Guidelines

Target strict brevity to ensure documentation fits within AI agent context windows while maximizing information density:

| Project Tier | File Scope | Recommended Length | Strategy if Exceeded |
| :--- | :--- | :--- | :--- |
| **Tier 1: Library / CLI** | < 25 files | 100–200 lines | Trim glossary; keep public API & workflow |
| **Tier 2: Single Service** | 25–100 files | 200–350 lines | Trim ADRs; prioritize Non-Obvious Patterns & Key Modules |
| **Tier 3: Multi-Service App** | 100–300 files | 300–500 lines | Compress tech stack; link sub-docs for edge features |
| **Tier 4: Enterprise Monorepo** | > 300 files | 400–600 lines | Use top-level overview + per-package `docs/` |

---

## 4. Agent-Readiness Verification

AI coding agents consume documentation differently from humans. Ensure compliance with these machine-readability checks:

1. **Self-Contained Patterns**: Each entry in "Non-Obvious Patterns" must be understandable without relying on cross-references from preceding sections.
2. **Deterministic Commands**: Never omit flags or rely on interactive prompts in scripts.
3. **Explicit Negative Constraints**: State what NOT to do explicitly (e.g., "Do not invoke blocking database calls inside route handlers").
4. **Exact Version Modifiers**: Specify version constraints where API behavior changed significantly (e.g., "Pydantic v2", "SQLAlchemy 2.0 async").

---

## 5. Final Quality Gate (The 3-Question Test)

Before shipping, verify:
1. **Would an engineer reading this documentation produce higher-quality code than one relying solely on source exploration?**
2. **Would an AI coding subagent make fewer architectural errors and hallucinations after reading this document?**
3. **Is every sentence conveying information that would be painful or time-consuming to discover by manual source code inspection?**

*If all three answers are YES, finalize and save the artifact.*
