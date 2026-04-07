# Relay v2 — Dev Log

## 2026-04-07 — Permission deadlock solved + concurrent_updates fix

### Problem
When a message came from Telegram (photo/text), tapping Allow/Deny on the inline keyboard did nothing. The same buttons worked when the message originated from CLI.

### Root cause
python-telegram-bot processes updates from the same chat **sequentially** by default. While `on_photo` (or any handler) was blocking on `await _wait_for_response(...)`, the callback query update (button tap) from the same chat was queued behind it. `on_photo` couldn't finish without permission; the callback couldn't run; classic deadlock.

CLI worked because no Telegram handler was blocking — callback ran freely.

### Fix
Added `concurrent_updates(True)` to the Application builder in `telegram_node.py`:
```python
app = Application.builder().token(token).concurrent_updates(True).post_init(post_init).build()
```

### Also built this session (from previous context)
- `permission_hook.py` — PermissionRequest hook that forwards to permission.sock, waits for decision, returns allow/deny JSON to Claude Code
- `claude_relay_wrapper.sh` — sets `CLAUDE_RELAY_SESSION=1` before exec'ing Claude; used as CLAUDE_PATH so relay's Claude process has the env var, distinguishing it from interactive sessions
- `.claude/settings.json` — registers PermissionRequest hook at project level
- `session_manager.py` — permission.sock server, `_handle_permission_conn`, `_resolve_permission`, `_publish_permission_request`
- `telegram_node.py` — `_permission_dispatcher` background task, `on_permission_callback`, inline Allow/Deny keyboard

### Known issue
`CLAUDE_RELAY_SESSION=1` leaks into interactive terminal sessions if started from the same shell as the relay. Need to ensure wrapper-set env var doesn't pollute interactive Claude Code sessions. Mitigation: use a separate terminal or `unset CLAUDE_RELAY_SESSION` before interactive use.
