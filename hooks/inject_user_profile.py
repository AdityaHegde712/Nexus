# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
import json
import os
from pathlib import Path
import sys


def main() -> None:
    try:
        base_dir = Path(__file__).resolve().parent.parent
        profile_path = base_dir / "USER_DECISION_PROFILE.md"
        if not profile_path.is_file():
            profile_path = Path.home() / ".codex" / "USER_DECISION_PROFILE.md"

        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": (
                            "For high-level design choices, consult the active User Decision "
                            "Profile at %s when it exists and is permitted to read. Keep planning "
                            "separate from execution; delegate independent implementation and review "
                            "work when it materially helps."
                            % profile_path
                        ),
                    }
                }
            )
        )
    except Exception as exc:
        if os.environ.get("DEBUG") or os.environ.get("NEXUS_DEBUG"):
            sys.stderr.write(f"[inject_user_profile] Error: {exc}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    main()
