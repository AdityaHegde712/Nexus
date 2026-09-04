# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
from datetime import datetime
import json
import os
import sys


def late_night() -> bool:
    return 1 <= datetime.now().hour < 8


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        event = payload.get("hook_event_name")
        if not late_night():
            return

        time_str = datetime.now().strftime("%I:%M %p")
        if event == "PreToolUse":
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": (
                                "Late-night soft lock: it is %s. Ask the user whether to "
                                "continue or wrap up before running this tool." % time_str
                            ),
                        }
                    }
                )
            )
        elif event == "UserPromptSubmit":
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "UserPromptSubmit",
                            "additionalContext": (
                                "It is past 1:00 AM locally (currently %s). Help the user "
                                "save work and wrap up; keep the reminder helpful and firm."
                                % time_str
                            ),
                        }
                    }
                )
            )
    except Exception as exc:
        if os.environ.get("DEBUG") or os.environ.get("NEXUS_DEBUG"):
            sys.stderr.write(f"[bedtime_reminder] Error: {exc}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    main()
