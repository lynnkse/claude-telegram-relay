#!/usr/bin/env python3
"""
pipe_session.py

Spawns a Claude CLI session with stdin/stdout connected via pipes,
then multiplexes keyboard↔Claude stdin and Claude stdout↔terminal.

Experience is identical to running `claude` directly, but pipes are
exposed for future integration with SessionManagerNode.

Usage:
    python3 tools/pipe_session.py                    # new session
    python3 tools/pipe_session.py --resume <id>      # resume session
"""

import subprocess
import threading
import sys
import argparse


def keyboard_to_claude(proc):
    """Forward keyboard input to Claude stdin. Blocks until EOF (Ctrl+D)."""
    try:
        for line in sys.stdin:
            proc.stdin.write(line.encode())
            proc.stdin.flush()
    except (BrokenPipeError, OSError):
        pass  # Claude process exited


def claude_to_terminal(proc):
    """Forward Claude stdout to terminal. Blocks until Claude exits."""
    try:
        for line in proc.stdout:
            sys.stdout.buffer.write(line)
            sys.stdout.buffer.flush()
    except (BrokenPipeError, OSError):
        pass


def stderr_to_terminal(proc):
    """Forward Claude stderr to terminal stderr. Blocks until Claude exits."""
    try:
        for line in proc.stderr:
            sys.stderr.buffer.write(line)
            sys.stderr.buffer.flush()
    except (BrokenPipeError, OSError):
        pass


def main():
    parser = argparse.ArgumentParser(description="Claude pipe session wrapper")
    parser.add_argument("--resume", metavar="SESSION_ID", help="Resume existing session")
    args = parser.parse_args()

    cmd = ["/home/lynnkse/.npm-global/bin/claude"]
    if args.resume:
        cmd += ["--resume", args.resume]

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    t1 = threading.Thread(target=keyboard_to_claude, args=(proc,), daemon=True)
    t2 = threading.Thread(target=claude_to_terminal, args=(proc,), daemon=True)
    t3 = threading.Thread(target=stderr_to_terminal, args=(proc,), daemon=True)

    t1.start()
    t2.start()
    t3.start()

    proc.wait()


if __name__ == "__main__":
    main()
