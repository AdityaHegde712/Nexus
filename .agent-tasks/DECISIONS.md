# Nexus Technical Decisions & Architectural Ledger

## Immutable Architectural Decisions

### 1. Harness Agnosticism as Core Design Principle
- **Decision**: All skills, subagent definitions, decision profiles, and lifecycle hooks must remain portable across execution harnesses (Antigravity IDE, Claude Code, Codex, Cursor, Roo, OpenCode).
- **Tradeoff**: Standardizes on neutral schemas (Markdown, TOML, Python scripts, JSON hooks) rather than locking into proprietary harness extensions.
- **Rejected Alternatives**: Hardcoding vendor-specific config formats as the sole configuration mechanism.

### 2. Workspace Cleanliness & Legacy Preservation
- **Decision**: All legacy opencode configuration and scripts are isolated inside `deprecated/`, which is ignored in `.gitignore`.
- **Tradeoff**: Keeps the git history clean and prevents confusing legacy scripts with active Nexus tools, while retaining immediate local access to historical implementations.
- **Rejected Alternatives**: Immediate hard deletion before validating migration completeness.

### 3. Deliberate Remote Renaming to 'Nexus'
- **Decision**: Remote repository is renamed to `Nexus` (`https://github.com/AdityaHegde712/Nexus.git`).
- **Rationale**: Elevates the project from a platform-specific setup script (`opencode-setup`) to a central nervous system / hub for personal agentic workflows.

### 4. Zero-Context Continuity Protocol
- **Decision**: Continuous persistence to `.agent-tasks/PLAN.md`, `.agent-tasks/DECISIONS.md`, and `.agent-tasks/TASKS.md` after each meaningful step.
- **Rationale**: Guarantees zero context loss across remote session migrations, Antigravity 2.0 transitions, and agent tier switching.

### 5. Deterministic Execution via PEP 723 & `uv`
- **Decision**: All standalone lifecycle scripts (`hooks/`, `scripts/`) declare inline metadata (`# /// script`) and run via `uv run --script`.
- **Rationale**: Guarantees hermetic, reproducible execution without relying on ambient system Python or manually activated virtualenvs.

### 6. Repository Self-Verification CI/Test Harness
- **Decision**: Repository includes a dedicated `tests/` suite using `pytest` validating hook payloads, agent TOML structure, and skill markdown link integrity.
- **Rationale**: Prevents silent drift, syntax breaks, or broken cross-references before deployment.

### 7. Multi-Harness Sync & Translation Layer
- **Decision**: Automated sync CLI (`scripts/sync_harness.py`) translates neutral agent/skill definitions to Codex, Claude Code, and Antigravity, using tilde notation for cross-platform consistency.
- **Rationale**: Provides push-button deployment to any harness without manual copy-pasting or proprietary lock-in.

## Operational Constraints
- Subprocess execution on Windows: Avoid `asyncio.create_subprocess_exec`; use `subprocess.run` wrapped in threads.
- Test and assertion immutability: Behavioral contracts must remain locked.
- UTF-8 with LF line endings across all written markdown, scripts, and config files.
