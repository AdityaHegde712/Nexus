# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Harness Sync & Translation Tool for Nexus.

Synchronizes and translates Nexus skills, agents, hooks, and decision profiles
across disparate agent harnesses: Codex, Claude Code, and Antigravity.
Config directories are defined and logged using tilde (~) notation.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tomllib
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parent.parent

# Default target directories using tilde notation
DEFAULT_TARGETS: Dict[str, str] = {
    "codex": "~/.codex",
    "claude": "~/.claude",
    "antigravity": "~/.gemini/antigravity",
}


def resolve_tilde(tilde_path: str) -> Path:
    """Expand tilde path to absolute Path."""
    return Path(os.path.expanduser(tilde_path)).resolve()


def copy_or_link_tree(src: Path, dst: Path, dry_run: bool = False) -> int:
    """Recursively copy directory tree, creating dst if needed."""
    if not src.is_dir():
        return 0
    count = 0
    for root, dirs, files in os.walk(src):
        rel_root = Path(root).relative_to(src)
        target_dir = dst / rel_root
        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            if f.endswith(".pyc") or f == "__pycache__":
                continue
            src_file = Path(root) / f
            dst_file = target_dir / f
            if not dry_run:
                shutil.copy2(src_file, dst_file)
            count += 1
    return count


def translate_agent_to_markdown(toml_path: Path) -> str:
    """Translate a Codex agent TOML definition into a harness-neutral markdown prompt."""
    with open(toml_path, "rb") as f:
        data: Dict[str, Any] = tomllib.load(f)

    name = data.get("name", toml_path.stem)
    desc = data.get("description", "")
    model = data.get("model", "")
    reasoning = data.get("model_reasoning_effort", "")
    instructions = data.get("developer_instructions", "").strip()

    md = [
        f"# Agent: {name}",
        "",
        desc,
        "",
        "## Configuration",
        f"- **Model**: {model}",
    ]
    if reasoning:
        md.append(f"- **Reasoning Effort**: {reasoning}")
    if data.get("sandbox_mode"):
        md.append(f"- **Sandbox Mode**: {data.get('sandbox_mode')}")
    md.extend([
        "",
        "## System Instructions",
        "",
        instructions,
        "",
    ])
    return "\n".join(md)


def sync_to_codex(target_tilde: str = "~/.codex", dry_run: bool = False) -> None:
    """Sync assets to Codex config directory."""
    dst = resolve_tilde(target_tilde)
    print(f"[*] Syncing Nexus to Codex target: {target_tilde} ({dst})")

    # 1. Skills
    skills_copied = copy_or_link_tree(REPO_ROOT / "skills", dst / "skills", dry_run=dry_run)
    print(f"    - Skills: {skills_copied} files copied to {target_tilde}/skills")

    # 2. Agents
    agents_dst = dst / "agents"
    if not dry_run:
        agents_dst.mkdir(parents=True, exist_ok=True)
    agent_count = 0
    for agent_file in (REPO_ROOT / "agents").glob("*.toml"):
        if not dry_run:
            shutil.copy2(agent_file, agents_dst / agent_file.name)
        agent_count += 1
    print(f"    - Agents: {agent_count} TOML profiles synced to {target_tilde}/agents")

    # 3. Hooks
    hooks_dst = dst / "hooks"
    if not dry_run:
        hooks_dst.mkdir(parents=True, exist_ok=True)
    hook_count = 0
    for hook_file in (REPO_ROOT / "hooks").glob("*.py"):
        if not dry_run:
            shutil.copy2(hook_file, hooks_dst / hook_file.name)
        hook_count += 1
    print(f"    - Hooks: {hook_count} scripts synced to {target_tilde}/hooks")

    # 4. hooks.json & USER_DECISION_PROFILE.md
    for filename in ["hooks.json", "USER_DECISION_PROFILE.md"]:
        src_file = REPO_ROOT / filename
        if src_file.is_file() and not dry_run:
            shutil.copy2(src_file, dst / filename)
    print(f"    - Config: hooks.json and USER_DECISION_PROFILE.md synced to {target_tilde}")


def sync_to_claude(target_tilde: str = "~/.claude", dry_run: bool = False) -> None:
    """Translate and sync assets to Claude Code config directory."""
    dst = resolve_tilde(target_tilde)
    print(f"[*] Syncing & translating Nexus to Claude Code target: {target_tilde} ({dst})")

    # 1. Skills
    skills_copied = copy_or_link_tree(REPO_ROOT / "skills", dst / "skills", dry_run=dry_run)
    print(f"    - Skills: {skills_copied} files copied to {target_tilde}/skills")

    # 2. Translate Agents from TOML to Markdown
    agents_dst = dst / "agents"
    if not dry_run:
        agents_dst.mkdir(parents=True, exist_ok=True)
    agent_count = 0
    for agent_file in (REPO_ROOT / "agents").glob("*.toml"):
        md_content = translate_agent_to_markdown(agent_file)
        dst_md = agents_dst / f"{agent_file.stem}.md"
        if not dry_run:
            dst_md.write_text(md_content, encoding="utf-8")
        agent_count += 1
    print(f"    - Agents: Translated {agent_count} TOML agents to Markdown in {target_tilde}/agents")

    # 3. Translate rules & user profile into CLAUDE.md guidelines
    claude_md_path = dst / "CLAUDE.md"
    profile_path = REPO_ROOT / "USER_DECISION_PROFILE.md"
    agents_path = REPO_ROOT / "AGENTS.md"

    combined = ["# Claude Code Guidelines (Generated from Nexus)", ""]
    if profile_path.is_file():
        combined.append(profile_path.read_text(encoding="utf-8"))
        combined.append("")
    if agents_path.is_file():
        combined.append(agents_path.read_text(encoding="utf-8"))
        combined.append("")

    if not dry_run:
        claude_md_path.write_text("\n".join(combined), encoding="utf-8")
    print(f"    - Directives: Generated {target_tilde}/CLAUDE.md from decision profile and AGENTS.md")


def sync_to_antigravity(target_tilde: str = "~/.gemini/antigravity", dry_run: bool = False) -> None:
    """Translate and sync assets to Antigravity directory."""
    dst = resolve_tilde(target_tilde)
    print(f"[*] Syncing & translating Nexus to Antigravity target: {target_tilde} ({dst})")

    # 1. Skills
    skills_copied = copy_or_link_tree(REPO_ROOT / "skills", dst / "skills", dry_run=dry_run)
    print(f"    - Skills: {skills_copied} files copied to {target_tilde}/skills")

    # 2. Translate Agents to Antigravity subagent Markdown
    agents_dst = dst / "agents"
    if not dry_run:
        agents_dst.mkdir(parents=True, exist_ok=True)
    agent_count = 0
    for agent_file in (REPO_ROOT / "agents").glob("*.toml"):
        md_content = translate_agent_to_markdown(agent_file)
        dst_md = agents_dst / f"{agent_file.stem}.md"
        if not dry_run:
            dst_md.write_text(md_content, encoding="utf-8")
        agent_count += 1
    print(f"    - Agents: Translated {agent_count} agents to Markdown in {target_tilde}/agents")

    # 3. Decision Profile
    profile_file = REPO_ROOT / "USER_DECISION_PROFILE.md"
    if profile_file.is_file() and not dry_run:
        shutil.copy2(profile_file, dst / "USER_DECISION_PROFILE.md")
    print(f"    - Decision Profile: USER_DECISION_PROFILE.md copied to {target_tilde}")

    # 4. Rules in ~/.gemini/config/rules/AGENTS.md
    gemini_rules = resolve_tilde("~/.gemini/config/rules")
    agents_file = REPO_ROOT / "AGENTS.md"
    if agents_file.is_file() and not dry_run:
        gemini_rules.mkdir(parents=True, exist_ok=True)
        shutil.copy2(agents_file, gemini_rules / "AGENTS.md")
    print(f"    - Rules: AGENTS.md synced to ~/.gemini/config/rules/AGENTS.md")


def main() -> None:
    parser = argparse.ArgumentParser(description="Nexus Harness Sync & Translation Tool")
    parser.add_argument(
        "--target",
        "-t",
        choices=["codex", "claude", "antigravity", "all"],
        default="all",
        help="Target agent harness to synchronize (default: all)",
    )
    parser.add_argument(
        "--codex-dir",
        default=DEFAULT_TARGETS["codex"],
        help=f"Target directory for Codex (default: {DEFAULT_TARGETS['codex']})",
    )
    parser.add_argument(
        "--claude-dir",
        default=DEFAULT_TARGETS["claude"],
        help=f"Target directory for Claude Code (default: {DEFAULT_TARGETS['claude']})",
    )
    parser.add_argument(
        "--antigravity-dir",
        default=DEFAULT_TARGETS["antigravity"],
        help=f"Target directory for Antigravity (default: {DEFAULT_TARGETS['antigravity']})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without modifying filesystem",
    )

    args = parser.parse_args()

    print("=== Nexus Multi-Harness Synchronizer ===")
    if args.dry_run:
        print("[!] Running in DRY RUN mode. No files will be written.\n")

    if args.target in ("codex", "all"):
        sync_to_codex(target_tilde=args.codex_dir, dry_run=args.dry_run)
    if args.target in ("claude", "all"):
        sync_to_claude(target_tilde=args.claude_dir, dry_run=args.dry_run)
    if args.target in ("antigravity", "all"):
        sync_to_antigravity(target_tilde=args.antigravity_dir, dry_run=args.dry_run)

    print("\n[OK] Synchronization complete.")


if __name__ == "__main__":
    main()
