import json
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_inject_user_profile_normal():
    script_path = REPO_ROOT / "hooks" / "inject_user_profile.py"
    res = subprocess.run(
        [sys.executable, str(script_path)],
        input=b"{}",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(REPO_ROOT),
    )
    assert res.returncode == 0
    data = json.loads(res.stdout.decode("utf-8"))
    assert "hookSpecificOutput" in data
    assert data["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "USER_DECISION_PROFILE.md" in data["hookSpecificOutput"]["additionalContext"]


def test_bedtime_reminder_daytime():
    script_path = REPO_ROOT / "hooks" / "bedtime_reminder.py"
    payload = json.dumps({"hook_event_name": "UserPromptSubmit"}).encode("utf-8")
    res = subprocess.run(
        [sys.executable, str(script_path)],
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(REPO_ROOT),
    )
    assert res.returncode == 0
