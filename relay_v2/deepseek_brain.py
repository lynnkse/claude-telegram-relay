#!/usr/bin/env python3
"""
deepseek_brain.py — DeepSeek-powered brain for relay v2.

Drop-in replacement for session_manager.py.
Same socket interface: reads user_input.sock, publishes to claude_response.sock.

Architecture:
  - DeepSeek API handles all reasoning and planning (sandbox — no FS/network access)
  - executor.py handles all file/bash/SSH operations (trusted layer)
  - Haiku (Claude API) used as watchdog for risky actions (optional, set WATCHDOG=1)

DeepSeek uses OpenAI-compatible tool calling to request actions.
Executor validates, confirms via Telegram if needed, then executes.

Environment variables (.env):
  DEEPSEEK_API_KEY      — required
  DEEPSEEK_MODEL        — default: deepseek-chat (V3). Use deepseek-reasoner for R1.
  ALLOWED_ROOTS         — comma-separated dirs DeepSeek may read/write (default: PROJECT_DIR)
  WATCHDOG              — set to 1 to enable Claude Haiku review of risky actions
  ANTHROPIC_API_KEY     — required if WATCHDOG=1
"""
from __future__ import annotations

import json
import logging
import os
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Optional

import config
from executor import Action, Result, configure as configure_executor, execute as executor_execute

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [deepseek] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

DEEPSEEK_API_KEY: str = config.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL: str = config.get("DEEPSEEK_MODEL", "deepseek-chat")
ALLOWED_ROOTS: list[str] = [
    r.strip() for r in config.get("ALLOWED_ROOTS", config.PROJECT_DIR).split(",") if r.strip()
]
WATCHDOG_ENABLED: bool = config.get("WATCHDOG", "0") == "1"
MAX_TOOL_ROUNDS = 10       # max consecutive tool calls before forcing text response
MAX_HISTORY = 40           # messages to keep in context (older ones dropped)

# ── Tool definitions (OpenAI function calling format) ─────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the full contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative file path"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files and directories at a path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or overwrite a file with new content. Requires user confirmation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string", "description": "Full new file content"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Run a shell command. Requires user confirmation for anything that modifies state.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Delete a file. Requires user confirmation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    },
]

SYSTEM_PROMPT = f"""You are an AI assistant with access to the user's computer via tools.

You can read files freely. For writes, deletes, and shell commands the user will be asked to confirm before anything executes — so propose actions freely, they won't happen without approval.

Working context:
- User: {config.USER_NAME or 'Lynn'}
- Allowed directories: {', '.join(ALLOWED_ROOTS)}
- Timezone: {config.USER_TIMEZONE}

When working on code or files:
1. Read relevant files first to understand the current state
2. Propose changes clearly, explaining what and why
3. Use write_file for edits (provide the full new file content)
4. Use bash for running tests, git commands, SSH to remote machines

Be concise. No need to narrate every tool call — just do the work and summarize results.
"""


# ── DeepSeek client ───────────────────────────────────────────────────────────

def _get_openai_client():
    try:
        from openai import OpenAI
    except ImportError:
        log.error("openai package not installed. Run: pip install openai")
        sys.exit(1)
    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    )


# ── Watchdog (Claude Haiku review of risky actions) ───────────────────────────

def _watchdog_review(action: Action) -> tuple[bool, str]:
    """Returns (approved, reason). Only called for non-auto-approve actions."""
    if not WATCHDOG_ENABLED:
        return True, "watchdog disabled"
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=config.get("ANTHROPIC_API_KEY", ""))
        prompt = (
            f"Review this action requested by DeepSeek:\n"
            f"Type: {action.type}\nParams: {json.dumps(action.params, indent=2)}\n\n"
            f"Is this action safe and sensible for a developer assistant? "
            f"Reply with JSON: {{\"safe\": true/false, \"reason\": \"...\"}}"
        )
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = msg.content[0].text.strip()
        if '{' in raw:
            raw = raw[raw.index('{'):raw.rindex('}')+1]
        result = json.loads(raw)
        return bool(result.get("safe")), result.get("reason", "")
    except Exception as e:
        log.warning(f"Watchdog error: {e} — defaulting to approve")
        return True, f"watchdog error: {e}"


# ── Brain session ─────────────────────────────────────────────────────────────

class DeepSeekBrain:
    def __init__(self):
        self.client = _get_openai_client()
        self.history: list[dict] = []
        self._lock = threading.Lock()
        configure_executor(ALLOWED_ROOTS)
        log.info(f"Brain ready. Model: {DEEPSEEK_MODEL}, allowed roots: {ALLOWED_ROOTS}")

    def _trim_history(self):
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]

    def _run_tool(self, name: str, args: dict, send_confirm) -> str:
        action = Action(id=f"{name}_{int(time.time())}", type=name, params=args)

        # Optional Haiku watchdog review before Telegram confirmation
        if WATCHDOG_ENABLED and name not in ("read_file", "list_dir"):
            safe, reason = _watchdog_review(action)
            if not safe:
                log.warning(f"Watchdog blocked {name}: {reason}")
                return f"[blocked by watchdog: {reason}]"

        result: Result = executor_execute(action, send_confirm)
        if result.success:
            return result.output or "done"
        return f"[error: {result.error}]"

    def chat(self, user_text: str, send_confirm, publish_text) -> str:
        """
        Process a user message. May call tools multiple times.
        send_confirm(action_id, summary) — sends Telegram confirmation request
        publish_text(text) — streams intermediate text back to user
        Returns final text response.
        """
        with self._lock:
            self.history.append({"role": "user", "content": user_text})
            self._trim_history()

            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history
            final_text = ""

            for round_num in range(MAX_TOOL_ROUNDS):
                response = self.client.chat.completions.create(
                    model=DEEPSEEK_MODEL,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                )
                msg = response.choices[0].message

                # Accumulate any text content
                if msg.content:
                    final_text = msg.content
                    if round_num > 0:
                        publish_text(f"_{msg.content}_")

                # No tool calls → done
                if not msg.tool_calls:
                    break

                # Execute tool calls
                messages.append(msg)
                tool_results = []
                for tc in msg.tool_calls:
                    fn_name = tc.function.name
                    fn_args = json.loads(tc.function.arguments)
                    log.info(f"Tool call: {fn_name}({list(fn_args.keys())})")
                    output = self._run_tool(fn_name, fn_args, send_confirm)
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": output[:8000],  # cap tool output
                    })

                messages.extend(tool_results)

            else:
                final_text = "[max tool rounds reached — stopping]"

            # Save final assistant turn to history
            self.history.append({"role": "assistant", "content": final_text})
            return final_text


# ── Socket server (same interface as session_manager.py) ─────────────────────

class BrainServer:
    def __init__(self):
        self.brain = DeepSeekBrain()
        self._response_subscribers: list[socket.socket] = []
        self._subs_lock = threading.Lock()

    def _publish(self, text: str, user_id: str):
        payload = json.dumps({"text": text, "source": "deepseek", "user_id": user_id}) + "\n"
        data = payload.encode()
        with self._subs_lock:
            dead = []
            for s in self._response_subscribers:
                try:
                    s.sendall(data)
                except Exception:
                    dead.append(s)
            for s in dead:
                self._response_subscribers.remove(s)

    def _handle_response_subscriber(self, conn: socket.socket):
        with self._subs_lock:
            self._response_subscribers.append(conn)
        # Keep connection open until client disconnects
        try:
            while conn.recv(1):
                pass
        except Exception:
            pass
        with self._subs_lock:
            if conn in self._response_subscribers:
                self._response_subscribers.remove(conn)

    def _handle_user_input(self, data: bytes):
        try:
            msg = json.loads(data.decode())
        except Exception:
            return

        # Handle executor confirmation responses (from Telegram inline buttons)
        if msg.get("type") == "confirm_response":
            from executor import resolve_confirmation
            action_id = msg.get("action_id", "")
            approved = bool(msg.get("approved", False))
            resolve_confirmation(action_id, approved)
            log.info(f"Confirmation resolved: action_id={action_id} approved={approved}")
            return

        text = msg.get("text", "").strip()
        user_id = str(msg.get("user_id", ""))
        if not text:
            return

        def send_confirm(action_id: str, summary: str):
            payload = json.dumps({"type": "confirm_request", "action_id": action_id, "summary": summary, "user_id": user_id}) + "\n"
            data = payload.encode()
            with self._subs_lock:
                dead = []
                for s in self._response_subscribers:
                    try:
                        s.sendall(data)
                    except Exception:
                        dead.append(s)
                for s in dead:
                    self._response_subscribers.remove(s)

        def publish_intermediate(text: str):
            self._publish(text, user_id)

        def run():
            try:
                response = self.brain.chat(text, send_confirm, publish_intermediate)
                self._publish(response, user_id)
            except Exception as e:
                log.error(f"Brain error: {e}", exc_info=True)
                self._publish(f"[error: {e}]", user_id)

        threading.Thread(target=run, daemon=True).start()

    def _serve_user_input(self):
        sock_path = config.USER_INPUT_SOCK
        Path(sock_path).unlink(missing_ok=True)
        os.makedirs(os.path.dirname(sock_path), exist_ok=True)
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(sock_path)
        srv.listen(5)
        log.info(f"Listening on {sock_path}")
        while True:
            conn, _ = srv.accept()
            threading.Thread(target=self._recv_conn, args=(conn,), daemon=True).start()

    def _recv_conn(self, conn: socket.socket):
        buf = b""
        try:
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    if line.strip():
                        self._handle_user_input(line.strip())
        except Exception:
            pass
        finally:
            conn.close()

    def _serve_response_subscribers(self):
        sock_path = config.CLAUDE_RESPONSE_SOCK
        Path(sock_path).unlink(missing_ok=True)
        os.makedirs(os.path.dirname(sock_path), exist_ok=True)
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(sock_path)
        srv.listen(10)
        log.info(f"Response socket: {sock_path}")
        while True:
            conn, _ = srv.accept()
            threading.Thread(target=self._handle_response_subscriber, args=(conn,), daemon=True).start()

    def run(self):
        if not DEEPSEEK_API_KEY:
            log.error("DEEPSEEK_API_KEY not set in .env")
            sys.exit(1)
        threading.Thread(target=self._serve_response_subscribers, daemon=True).start()
        self._serve_user_input()  # blocks


if __name__ == "__main__":
    BrainServer().run()
