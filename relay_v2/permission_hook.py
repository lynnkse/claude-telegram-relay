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
import os
import socket
import sys
import time
from datetime import datetime

# Must match config.py
PERMISSION_SOCK = "/tmp/cognitive-hq/permission.sock"
TIMEOUT = 120  # seconds to wait for user decision
LOG_FILE = "/tmp/permission_hook.log"


def _log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    line = f"{ts} {msg}\n"
    sys.stderr.write(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line)
    except Exception:
        pass


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
    # Only intercept permissions for the relay's own Claude session.
    # Other Claude Code sessions on this machine exit immediately so their
    # normal TUI dialog is shown instead.
    if not os.environ.get("CLAUDE_RELAY_SESSION"):
        sys.exit(1)

    _log("=== permission_hook started ===")

    try:
        raw = sys.stdin.read()
        request = json.loads(raw)
        _log(f"stdin: tool={request.get('tool_name')} input={str(request.get('tool_input',''))[:80]}")
    except Exception as e:
        _log(f"ERROR reading stdin: {e}")
        sys.exit(1)  # fall through to TUI

    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(PERMISSION_SOCK)
        _log("connected to permission.sock")
    except Exception as e:
        _log(f"ERROR connecting to permission.sock: {e} — falling through to TUI")
        sys.exit(1)  # fall through to TUI

    try:
        payload = (json.dumps(request) + "\n").encode()
        sock.sendall(payload)
        _log("request sent, waiting for decision...")

        # Wait for decision
        sock.settimeout(TIMEOUT)
        buf = b""
        while b"\n" not in buf:
            chunk = sock.recv(256)
            if not chunk:
                _log("socket closed by server before decision")
                break
            buf += chunk

        sock.close()

        if not buf.strip():
            _log("ERROR: empty response from server — falling through to TUI")
            sys.exit(1)

        line = buf.split(b"\n")[0].strip()
        _log(f"received: {line.decode()}")
        response = json.loads(line)
        decision = response.get("decision", "deny")
        _log(f"decision: {decision}")

        if decision == "allow":
            output = json.dumps(_allow())
        else:
            output = json.dumps(_deny(response.get("message", "Denied via Telegram relay.")))

        _log(f"stdout: {output}")
        print(output)
        sys.stdout.flush()
        _log("=== permission_hook done (exit 0) ===")
        sys.exit(0)

    except Exception as e:
        _log(f"ERROR in decision loop: {e}")
        try:
            sock.close()
        except Exception:
            pass
        sys.exit(1)  # fall through to TUI


if __name__ == "__main__":
    main()
