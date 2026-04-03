#!/usr/bin/env python3
"""
pipe_session.py

Spawns a Claude CLI session inside a pseudo-terminal (PTY), multiplexing
keyboard↔Claude exactly as if you ran `claude` directly.

PTY is required because Claude CLI checks whether stdin is a TTY. When
stdin is a plain pipe, it assumes --print mode and refuses to start
interactively. pty.spawn() creates a real TTY so Claude behaves normally.

For future SessionManagerNode integration (programmatic stdin/stdout
injection), replace pty.spawn() with a master/slave PTY pair:
    master_fd, slave_fd = pty.openpty()
    proc = subprocess.Popen(cmd, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd)
    os.close(slave_fd)
    # read/write master_fd to multiplex programmatic and keyboard I/O

Usage:
    python3 tools/pipe_session.py                    # new session
    python3 tools/pipe_session.py --resume <id>      # resume session
"""

import pty
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="Claude PTY session wrapper")
    parser.add_argument("--resume", metavar="SESSION_ID", help="Resume existing session")
    args = parser.parse_args()

    cmd = ["/home/lynnkse/.npm-global/bin/claude"]
    if args.resume:
        cmd += ["--resume", args.resume]

    # pty.spawn() forks the process under a PTY and handles all I/O
    # multiplexing between the real terminal and Claude. Exit code is
    # returned as the low byte of the waitpid status.
    status = pty.spawn(cmd)
    sys.exit(status & 0xFF)


if __name__ == "__main__":
    main()
