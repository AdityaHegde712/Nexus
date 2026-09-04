from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import sync_harness


def test_translate_agent_to_markdown():
    dev_toml = REPO_ROOT / "agents" / "developer.toml"
    assert dev_toml.is_file()
    md = sync_harness.translate_agent_to_markdown(dev_toml)
    assert "# Agent: developer" in md
    assert "gpt-5.6-terra" in md
    assert "Lead Implementation Developer" in md


def test_sync_dry_run():
    # Verify dry-run doesn't crash
    sync_harness.sync_to_codex(target_tilde="~/.codex_test_dry", dry_run=True)
    sync_harness.sync_to_claude(target_tilde="~/.claude_test_dry", dry_run=True)
    sync_harness.sync_to_antigravity(target_tilde="~/.gemini_test_dry", dry_run=True)


def test_sync_to_temp_directory(tmp_path):
    # Test real file emission into a temp directory using a tilde override
    target_tilde = str(tmp_path)
    sync_harness.sync_to_claude(target_tilde=target_tilde, dry_run=False)

    claude_md = tmp_path / "CLAUDE.md"
    assert claude_md.is_file()
    assert "Claude Code Guidelines" in claude_md.read_text(encoding="utf-8")

    agents_dir = tmp_path / "agents"
    assert agents_dir.is_dir()
    assert (agents_dir / "developer.md").is_file()
    assert (agents_dir / "adversary.md").is_file()
