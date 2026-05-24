# Migrate Relay to DeepSeek

> This guide is written for the relay agent on aevadim-09 (or any machine running the Claude relay).
> Follow these steps to switch from the Claude CLI backend to DeepSeek V4.

## What changes

- `session_manager.py` (Claude CLI subprocess) → `deepseek_brain.py` (DeepSeek API)
- `executor.py` handles all file/bash/SSH actions with Telegram confirmation buttons
- Everything else stays the same: same Telegram bot, same socket interface, same proactive node

---

## Step 1 — Pull the branch

```bash
cd ~/cognitive-hq/claude-telegram-relay
git fetch origin
git checkout deepseek-relay
git pull origin deepseek-relay
```

---

## Step 2 — Add DeepSeek API key to .env

Open `.env` and add at the bottom:

```
DEEPSEEK_API_KEY=sk-c200f3ed016b4509ada90945b5c1aa4a
DEEPSEEK_MODEL=deepseek-chat
ALLOWED_ROOTS=/home/lynnkse/cognitive-hq,/home/lynnkse/.claude-relay
```

`ALLOWED_ROOTS` = comma-separated directories DeepSeek is allowed to read/write.
Adjust the paths to match this machine's layout.

---

## Step 3 — Install openai package in relay venv

```bash
~/.pyenv/versions/cognitive-hq/bin/pip install openai
```

Verify:
```bash
~/.pyenv/versions/cognitive-hq/bin/python3 -c "from openai import OpenAI; print('ok')"
```

---

## Step 4 — Stop the current relay

Kill all running relay processes:

```bash
pkill -f session_manager
pkill -f telegram_node
pkill -f proactive_node
pkill -f cli_node
```

Verify nothing is left:
```bash
ps aux | grep -E 'session_manager|telegram_node|proactive_node' | grep -v grep
```

---

## Step 5 — Start the DeepSeek relay

```bash
cd ~/cognitive-hq/claude-telegram-relay/relay_v2
bash start_relay_deepseek.sh
```

This starts:
- `deepseek_brain.py` (DeepSeek brain + executor)
- `telegram_node.py` (Telegram interface, same as before)
- `proactive_node.py` (check-ins, same as before)

---

## Step 6 — Test

Send a message to the Telegram bot. It should respond via DeepSeek.

Test file access:
> "Read the file relay_v2/config.py and tell me what PROJECT_DIR is set to"

Test confirmation flow (write action):
> "Add a comment to the top of relay_v2/config.py"
→ Should send Telegram inline buttons: ✅ Approve / ❌ Deny

---

## Rollback

To go back to Claude relay at any time:

```bash
pkill -f deepseek_brain
cd ~/cognitive-hq/claude-telegram-relay/relay_v2
bash start_relay.sh
```

---

## Notes

- `deepseek-chat` currently maps to **deepseek-v4-flash** (DeepSeek's latest fast model)
- Use `DEEPSEEK_MODEL=deepseek-reasoner` for R1 (slower, deeper reasoning, costs more)
- Watchdog: set `WATCHDOG=1` in .env to enable Claude Haiku review of risky actions (requires `ANTHROPIC_API_KEY`)
- Max tool rounds per message: 10 (configurable in `deepseek_brain.py` → `MAX_TOOL_ROUNDS`)
- Conversation history: 40 messages rolling window
