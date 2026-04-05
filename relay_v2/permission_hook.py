#!/usr/bin/env python3
"""
PermissionRequest hook for Relay v2.

Claude Code calls this script when a tool needs permission.
We forward the request to SessionManagerNode via permission.sock,
wait for the user's decision (from Telegram or CLI), and return it.

Claude Code protocol:
  stdin  — JSON with tool_name, tool_input, session_id, etc.
  stdout — JSON with hookSpecificOutput.decision.behavior = "allow"|"deny"
  exit 0 always (non-zero = error, Claude Code falls back to TUI)

Timeout: if SessionManagerNode is not running or user doesn't respond
within TIMEOUT seconds, we fall through by exiting non-zero so Claude
Code shows its normal TUI dialog.
"""

import json
import socket
import sys
import time

# Must match config.py
PERMISSION_SOCK = "/tmp/cognitive-hq/permission.sock"
TIMEOUT = 120  # seconds to wait for user decision


def _allow() -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {"behavior": "allow"},
        }
    }


def _deny(message: str = "Denied via Telegram relay.") -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {"behavior": "deny", "message": message},
        }
    }


def main():
    try:
        raw = sys.stdin.read()
        request = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"permission_hook: failed to read stdin: {e}\n")
        sys.exit(1)  # fall through to TUI

    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(PERMISSION_SOCK)
    except Exception as e:
        sys.stderr.write(f"permission_hook: SessionManagerNode not reachable: {e}\n")
        sys.exit(1)  # fall through to TUI

    try:
        payload = (json.dumps(request) + "\n").encode()
        sock.sendall(payload)

        # Wait for decision
        sock.settimeout(TIMEOUT)
        buf = b""
        while b"\n" not in buf:
            chunk = sock.recv(256)
            if not chunk:
                break
            buf += chunk

        sock.close()

        line = buf.split(b"\n")[0].strip()
        response = json.loads(line)
        decision = response.get("decision", "deny")

        if decision == "allow":
            print(json.dumps(_allow()))
        else:
            print(json.dumps(_deny(response.get("message", "Denied via Telegram relay."))))

        sys.exit(0)

    except Exception as e:
        sys.stderr.write(f"permission_hook: error waiting for decision: {e}\n")
        try:
            sock.close()
        except Exception:
            pass
        sys.exit(1)  # fall through to TUI


if __name__ == "__main__":
    main()
