# User Decision Profile & Confidence Matrix

## General Development Heuristics

### 1. System Design & Architecture
- **Directory Organization**: Research outputs/artifacts belong in designated subdirectories (`.agent-tasks/<topic>/` or `_internal/`), not project root. Root contains only essential reference/blueprint documents.
- **Simplicity & Frameworks**: Prefer minimal viable solutions. Use standard frameworks (React, Vite, Conda, etc.) only when codebase exceeds 500 lines total code; prefer raw vanilla code/scripts for smaller sizes.
- **Foundation Finality**: Once core architectural/foundational modules pass development, adapt via layers/bridges/shims rather than rebuilds for downstream issues unless exhaustively proven unsolvable.
- **Reference Grounding & Authority**: Treat user domain specs as authoritative. Cite published sources, established libraries, or known patterns for all architectural/methodological claims; avoid inventing novel mechanisms ad-hoc.
- **Interaction-First Architecture**: Present multi-component systems by detailing interaction/feedback loops first, never static component inventories.
- **Explicit Scope & Determinism**: Articulate in-scope vs. out-of-scope boundaries with rationale. Resolve implementation options to a single concrete path before seeking approval.
- **Scale Stratification & Offloading**: Stratify models/modules per scale range when system behavior scales nonlinearly. Offload resource-intensive workloads (e.g., deep learning training) to external environments (Colab, cloud VMs) rather than running locally.
- **Independent Artifacts**: Ensure research prototypes and code artifacts are self-contained and reproducible without dependencies on private or environment-specific toolchains.
- **Diagram Formats**: Prefer Excalidraw JSON over draw.io XML (easier editing and parsing by agents).
- **Deterministic LLM Output**: Prefer delimiter-friendly plaintext output (section headers, `##` labels, separators) parsed via deterministic string manipulation over JSON/SSE retry chains. Unparseable output is a FATAL phase-named error; never silently re-parse or fall back.
- **Single-Pass Pipelines**: Use one LLM call per generation pipeline; avoid streaming (SSE) and multi-call retry chains unless required.
- **Stable-Key Resolution over Names**: When LLM output may rename/paraphrase entities (e.g., JD suitability), anchor references to source-stable keys (numbered index from input catalog) via side map files; fuzzy name matching is defense-in-depth only.
- **Prompt Token Hygiene**: Keep URLs and large reference data out of prompts; resolve through side lookup files to avoid token waste.
- **Phase Failure Semantics**: Distinguish fatal vs non-fatal pipeline phases. Non-fatal phases (e.g., PDF compile) persist artifacts and surface a flag (e.g., `pdf_error`) instead of aborting.
- **Windows Subprocess Calls**: Never use `asyncio.create_subprocess_exec` on Windows (ProactorEventLoop `NotImplementedError`); run blocking subprocesses via `subprocess.run` inside `asyncio.to_thread`.
- **Tool Path Resolution Chains**: Resolve tool binaries: env var → known default install path → PATH fallback.

### 2. Operations & TDD Execution
- **Surgical Modifications**: Favor surgical minimal diffs over wide refactoring of surrounding code unless explicitly requested.
- **Utility Discovery & Minimal Dependencies**: Reuse existing project utilities over new ad-hoc scripts. Prefer language standard library (e.g., Python stdlib) for simple utilities to maintain zero-dependency footprint.
- **TDD & Permission Boundaries**: Strict TDD: batch-write locked test assertions first, verify failure, then implement. Tests are immutable contracts; implementation agents run but must not modify tests (test-writing agents must not refactor implementation).
- **Write Tool Integrity**: If file write/edit tools fail due to permissions or errors, never bypass via shell/terminal commands (`echo`, `cat`, redirects); immediately report to user.
- **Git & Documentation Lifecycle**: Batch doc updates and git commits at the end of every project phase (from Architect's plan), not continuously.
- **Sub-Agent Context & Execution**: Planning-only agents must not edit code; delegate to orchestrators/executors. Pass absolute paths and working directories explicitly to avoid context drift.
- **Branch Merging & Pull Requests**: Never merge branches locally or initiate PRs via agents. Direct user on branch targets and rebases; user merges manually.
- **Permanent Resurfacing Fixes**: If an issue recurs upon rebuild/recreation, implement permanent code fixes rather than temporary skips or patches.
- **API Provider Integrations**: Always include integration/connectivity validation scripts when adding or changing external API providers.
- **Bulk File Assessment via Technical Writer**: To assess many files without context bloat, delegate reading to a sub-agent with the routed skill instead of reading directly.
- **Frozen vs Mutable Tests**: Contract tests (`tests/spec/`, frozen, define behavior); integration tests (`tests/integration/`, mutable). Reuse single golden fixture across modules sharing data formats.
- **Live Owner-Owned Files**: Owner edits authoritative files (prompts, configs, YAML maps) directly between turns. Re-verify ground truth before finalizing dependent plans/code.
- **Planning-Only Sessions**: Keep architect/planning sessions free of implementation; Owner launches execution in separate session. Write plans and await approval; never implement in planning sessions.
- **Mandatory Reduced-Size E2E Smoke for Multi-Hour Operations**: Multi-hour operations (data prep, generation, training) MUST complete a full E2E reduced-size smoke test (same pipeline, `--limit N` / reduced epochs / small subset through every stage to final artifact) BEFORE full run launch. Full run launches only after smoke produces verified final artifact and Owner approves. (Context: 2026-08-07 T2.2 full run burned 4h at jobs=4 with ZERO output because jobs>1 worker pickled df slices path lacked E2E smoke; jobs=1 smoke did not cover it).

### 2A. Execution & Evidence
- **Pre-Action Transparency**: State intended action, scope, and expected outcome concisely before any tool call, file read, edit, external request, or state change.
- **Screenshot-Led UI Debugging**: For visual defects, reproduce in isolated browser context at target viewport, inspect rendered screenshot and measured layout geometry, then apply smallest targeted change.
- **Separate Evidence Gates**: Automated tests, live/manual verification, and release packaging are separate gates. Do not infer live integration success from mocks or release readiness from tests alone; record evidence per gate independently.
- **Zero-Context State Synchronization**: At meaningful phase boundaries, update plan, decisions, and task ledger with status, evidence, blockers, and one concrete next action for zero-history handoff.
- **Release Integrity Before Cleanup**: Before deleting branches or publishing artifacts, verify commit reachability from target branch, confirm remote state, and record artifact metadata (version, size, checksum).

### 3. Local UI, WebViews & Web Compatibility
- **Mobile File Compatibility**: Single self-contained HTML file for WebViews launched via local file managers (`content://` or `file://` URIs) to prevent relative path breakage.
- **Asynchronous CDN Loading**: Dynamically inject external library scripts to prevent blocking page loads on slow/failed CDNs.
- **IndexedDB for Handles**: Persist structured-cloneable objects (e.g., file handles) in IndexedDB (`localStorage` cannot store them).
- **Form Button Types**: Explicitly set `type="button"` on all non-submit `<button>` tags within `<form>` to prevent accidental submission.
- **Responsive Layouts**: Prefer card-based or label-value layouts over fixed tables on viewports ~360px wide to avoid horizontal overflow.

### 4. CLI & Automation Tools
- **CLI Input Filtering**: Warn and skip unsupported inputs/URLs rather than silently ignoring or throwing fatal errors.
- **Paced Batch Operations**: Paced batching (`--batch-size N`) with interactive confirmation pauses and clean exits (Ctrl+C) for external batch processes.

### 5. Code & Documentation Standards
- **Error Handling**: Raise exceptions early and loudly; avoid soft-failure or silent fallback mechanisms that mask broken behavior.
- **Third-Party Libraries**: For minor features, prefer popular third-party micro-packages (e.g., lodash, date-fns); author custom implementations only when packages do not fit.
- **In-Code Documentation**: Concise, type-hinted, modular with Google-style docstrings/JSDoc.
- **Plans/Design**: High granularity, technical/mathematical/mechanistic precision, and explicit failure-mode analysis over qualitative descriptions.
- **Reference Paths in Reports**: Include explicit file paths to source data in reports and summaries for direct navigation.
- **Post-Reorganization Reference Audit**: Audit and update all documentation referencing old paths after file move, rename, or delete operations.
- **LLM Text Escaping**: Escape all LLM-derived text before embedding into templates/output formats; LLMs never author raw markup or commands.
- **API Contract Normalization**: Normalize API responses to fixed snake_case key contracts; expose non-fatal phase flags as explicit fields.
- **UTF-8 Encoding Everywhere**: Enforce UTF-8 encoding in all writable artifacts (.sh, .bat, .py, .js, .ts, .jsx, .tsx, .md, .txt, .json/.jsonc, .log); no mangled non-ASCII (em-dashes, emoji, box-drawing, accents). Concrete: export `LANG`/`LC_ALL` to UTF-8 locale in shell scripts; `encoding="utf-8"` on Python file writes; write LF without BOM; verify with byte checks (`od -c` / CR counts / `file`) on Windows.

### 6. Plan Version Labeling & Phasing
- **Version Hygiene**: Do NOT bump full plan versions when adding features to approved plans. Keep approved plan at current version; append new sections labeled "vNext Proposed Additions". Version labels track approved decision points, not cumulative increments.
- **Feature Classification**: Label feature sets with intended release target (e.g., "v1.0 feature" vs "planned for v1.1"). Separate deferred/future features into dedicated sections; never merge into current version sections.

---

## Workspace Preferences
- **Theme**: Dark themes default (`#121212` background, `#e0e0e0` text).
- **Test Placement**: Dedicated isolated test directories (`tests/` at root) strictly preferred over co-locating with source.
- **Formatting & Linting**: Automatically run formatters/linters (Prettier, Black, Ruff, ESLint) on modified files before commit.
- **Git Commits**: Milestone-based auto-commits.
- **Root Cleanliness**: Root limited to essential reference/blueprint documents. Subdirectories for research artifacts, raw data, debug scripts.
- **Per-Dataset Raw/Processed Split**: `data/<dataset>/raw/` for downloads; `data/<dataset>/processed/` for derivatives. Maintain `DATASET_SUMMARY.md` per dataset (schema, stats, quality).
- **Research Artifact Disposability**: Delete raw API results (JSON), throwaway debug scripts (<40 lines), and stale session logs once findings are captured in structured reports.
- **Frontend Style (web apps)**: No Bootstrap. Component libraries with fixed/token themes preferred over hand-rolled CSS. Preferred: Mantine, shadcn/ui, Ant Design; Acceptable: MUI, HeroUI. Dark minimal flat UI with hairline dividers.
- **Archived Context Hygiene**: Archived artifacts (`.agent-tasks/archived/`, `old_code.zip`) stay unread unless explicitly requested; never surface into working context.
