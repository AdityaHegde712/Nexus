# Nexus: Harness-Agnostic Agentic Tooling Ecosystem

Nexus is a portable, harness-agnostic personal agent operating ecosystem designed to unify workflows across **OpenAI Codex**, **Anthropic Claude Code**, and **Google Antigravity**.

Instead of coupling workflows to proprietary platform formats, Nexus standardizes tools, skills, subagent roles, lifecycle hooks, and cognitive profiles into neutral schemas (Markdown, TOML, and PEP 723 Python scripts).

---

## Key Architectural Principles

1. **Harness Agnosticism**: Write skills and agent instructions once; deploy seamlessly across multiple coding agent harnesses via automated translation.
2. **Adversarial Role Separation**: Strictly decouples implementation authoring (`developer`) from security, architectural, and empirical critique (`adversary`).
3. **Stateless Handoff & Session Continuity**: Uses the `.agent-tasks/` protocol (`PLAN.md`, `DECISIONS.md`, `TASKS.md`) for zero-context resumption across context wipes and model transitions.
4. **Hermetic Execution via `uv`**: Standalone lifecycle scripts declare inline PEP 723 metadata (`# /// script`) and execute deterministically via `uv run --script`.
5. **Automated Self-Verification**: Full automated test suite verifying hook schemas, agent TOML structure, and skill documentation cross-references.

---

## Directory Structure

```text
Nexus/
├── .agent-tasks/              # Stateless session handoff ledger
│   ├── DECISIONS.md           # Immutable architectural decisions & constraints
│   ├── PLAN.md                # Multi-phase execution plan & affected paths
│   └── TASKS.md               # Atomic task checklist & blocker tracking
├── agents/                    # Subagent role definitions
│   ├── adversary.toml         # Adversarial auditor (security, logic, empirical rigor)
│   └── developer.toml         # Lead implementation developer (production standards)
├── hooks/                     # Deterministic lifecycle hooks
│   ├── bedtime_reminder.py    # Late-night work guard & tool soft lock
│   └── inject_user_profile.py # Session-start decision profile injection
├── scripts/                   # Tooling and synchronization
│   └── sync_harness.py        # Multi-harness translator & synchronizer
├── skills/                    # 20 curated engineering and domain skills
│   ├── architect/             # System design, RFCs, ADRs, trade-off analysis
│   ├── backend-engineering/   # Clean/hexagonal architecture, REST, ACID transactions
│   ├── clean-code/            # SOLID, DRY, KISS, guard clauses, type annotations
│   ├── codebase-curator/      # Authoritative CODEBASE.md and architecture diagrams
│   ├── data-engineer/         # Pipelines, profiling, DuckDB/Parquet storage
│   ├── devops-iac/            # Terraform, Docker multi-stage builds, cloud infra
│   ├── frontend-engineering/  # Component-driven design, state separation, dark minimal UI
│   ├── gdoc-publisher/        # Markdown to styled Google Docs publisher
│   ├── git-workflow/          # Feature branches, rebasing, conventional commits
│   ├── humanize-report/       # Technical prose refinement & AI de-troping
│   ├── jupytext-notebooks/    # Clean Python pair-sync for Jupyter notebooks
│   ├── ml-engineer/           # Model training, ONNX/vLLM optimization, smoke testing
│   ├── production-readiness-review/ # Multi-vector production hardening audit
│   ├── research/              # Evidence-grounded technical research & source verification
│   ├── slide-deck/            # HTML-first visual slide prototyping
│   ├── terraform-test-writer/ # Unit and integration testing for Terraform modules
│   ├── tester/                # TDD cycle (Red-Green-Refactor) and immutable assertions
│   ├── token-compressor/      # High-density instruction & prompt compression
│   ├── ui-ux/                 # Interface governance, visual rhythm, interaction flows
│   └── webapp-testing/        # Playwright browser testing and verification
├── tests/                     # Repository self-verification test suite
│   ├── test_agents.py         # TOML schema and field validation
│   ├── test_hooks.py          # Mock payload execution and stderr logging
│   ├── test_skills.py         # Inventory check and relative link validation
│   └── test_sync_harness.py   # Multi-harness translation validation
├── AGENTS.md                  # Routing table, ADHD communication rules, directives
├── hooks.json                 # Workspace-level hook configuration
├── pyproject.toml             # Pytest configuration & environment settings
└── USER_DECISION_PROFILE.md   # Personal technical preferences and heuristics
```

---

## Multi-Harness Synchronization

Nexus includes an automated synchronization tool (`scripts/sync_harness.py`) that deploys your skills, agents, and configurations to target harness environments using standard tilde (`~`) paths:

### Deployment Commands

```bash
# Preview changes without modifying files
uv run --script scripts/sync_harness.py --dry-run

# Synchronize all supported harnesses (Codex, Claude Code, Antigravity)
uv run --script scripts/sync_harness.py --target all

# Synchronize specific harness
uv run --script scripts/sync_harness.py --target codex
uv run --script scripts/sync_harness.py --target claude
uv run --script scripts/sync_harness.py --target antigravity
```

### Supported Harness Targets & Translations

| Harness | Target Directory | Translation Behavior |
| :--- | :--- | :--- |
| **OpenAI Codex** | `~/.codex` | Direct sync of skills, `agents/*.toml`, `hooks/*.py`, and `hooks.json`. |
| **Claude Code** | `~/.claude` | Syncs skills; translates `agents/*.toml` into Markdown agent prompts in `agents/`; synthesizes `CLAUDE.md` from decision profile and rules. |
| **Antigravity** | `~/.gemini/antigravity` | Syncs skills; translates agents into Antigravity subagent Markdown prompts; syncs rules to `~/.gemini/config/rules/AGENTS.md`. |

---

## Lifecycle Hooks & Cognitive Guardrails

Nexus hooks enforce discipline and cognitive safety without impeding developer velocity:

1. **Late-Night Work Guard (`hooks/bedtime_reminder.py`)**:
   - Triggers on `PreToolUse` and `UserPromptSubmit`.
   - Between 1:00 AM and 8:00 AM local time, issues a soft lock prompting the user to wrap up or explicitly confirm tool execution.
2. **Context Injection (`hooks/inject_user_profile.py`)**:
   - Triggers on `SessionStart` (startup, resume, compact).
   - Injects the path to `USER_DECISION_PROFILE.md` relative to repository root into the agent's context window.

Both hooks feature structured `sys.stderr` diagnostics enabled by setting `DEBUG=1` or `NEXUS_DEBUG=1`.

---

## Running Repository Tests

Nexus maintains high internal engineering standards via an automated self-verification test suite:

```bash
uv run --with pytest pytest
```

The test suite validates:
- **Hook execution**: Tests `bedtime_reminder.py` and `inject_user_profile.py` with mock stdin JSON payloads.
- **Agent integrity**: Validates that all `agents/*.toml` files parse correctly and contain required fields.
- **Documentation links**: Parses all 20 `SKILL.md` files and asserts that all relative markdown links resolve to existing files on disk.
- **Translation integrity**: Verifies that the multi-harness translation logic produces valid Claude and Antigravity artifacts.

---

## Author & License

Maintained by **Aditya Hegde** ([@AdityaHegde712](https://github.com/AdityaHegde712)).
Licensed under the MIT License.
