# Relay v2 — Dev TODO

## Pending

- [x] **GLM sub-agent via MCP** — `relay_v2/glm_agent.py` built and registered. Model: glm-5.1 (flagship). Key wired in. Tested and working. Claude calls `delegate_to_glm(task, context)` to delegate code tasks. glm-z1 (reasoning) requires paid tier — upgrade when needed.

- [ ] **Automated experiment startup: lab machine + robot over SSH** — Claude autonomously launches the full 5-terminal experiment setup. Prerequisites: (1) SSH key auth from lab machine to robot (`ssh-copy-id`), (2) passwordless sudo on robot scoped to sensor script (`visudo`). Then Claude runs: roscore + roslaunch on lab machine via tmux, and roslaunch + controller + sensors on robot via SSH into tmux sessions. Triggered by "start the experiment" from Telegram. Claude verifies each step launched correctly before proceeding.

- [x] **Deploy relay on work PC for ROS/SLAM repo** — Relay running on work PC. Supabase MCP connected (settings.json updated with auth header). Work bot operational.

- [ ] **`knowledge` table: professional insights across projects** — Separate table from `memory` (which stays personal). Stores lessons learned, procedures, patterns, warnings per project. Has `project` column (null = cross-project). Needs schema migration + `embed` webhook + injection into system prompt filtered by current project. Design doc needed before implementation.

- [ ] **Agentic `search_memory` tool** — Instead of injecting all memory at startup (blunt), give Claude a tool it can call when it judges relevant context exists. Works for both `memory` and `knowledge` tables. Requires exposing a search endpoint the relay can call and pass results back to Claude mid-conversation.

- [ ] **Claude Code hook: Supabase memory injection at session startup** — Build a Claude Code startup hook that queries Supabase `memory` table (facts, goals, preferences) and injects them into the session context. This closes the gap where CLI/Claude Code sessions don't benefit from long-term memory — currently only the Telegram relay gets memory injection via system prompt. Goal: unified memory across both relay and Claude Code sessions, replacing `DERIVED_CONTEXT.DATA.md` for personal/cross-session knowledge.

- [ ] **Full response delivery after multi-step tasks** — After long runs (log + commit + multiple permissions), the final text response sometimes never appears in Telegram. Either the JSONL debounce window is too short for slow multi-tool responses, or the response times out. Need to investigate: check if final text entry is written to JSONL after long tool chains, tune debounce/timeout, and ensure the complete summary response (not just tool confirmations) reaches the user.

- [ ] **Message source metadata in responses** — Claude should know whether a message came from Telegram or CLI (or which CLI user, future multi-user). The `source` field already flows through QueueItem and is published with each response; expose it to the Claude prompt so it can tailor its reply (e.g. keep responses concise for Telegram, can be verbose for CLI). Consider injecting source into the PTY message prefix: `[from:telegram] user message here`.

- [ ] **Dreaming mode / memory consolidation** — Background process that consolidates raw Supabase memory into high-signal durable knowledge. Runs when agent is idle. Three phases: light (extract candidates), REM (detect patterns, strengthen), deep (score + promote to durable memory). See `DREAMING_MODE.md` for full spec. **Prerequisite: plain Supabase memory must be working and validated first.**

- [ ] **[FUTURE PROJECT] Local AI Agent on USB SSD + RTX 3090** — Full spec in `LOCAL_AI_AGENT_SPEC.md`. Model: **Dolphin3.0-Mistral-24B** (Q4, ~14GB VRAM). USB holds all state (chats, memory, vectordb, characters). Compute on RTX 3090 via Ollama. SillyTavern frontend. Optional Telegram bridge. 8-phase deployment via bootstrap script. No cloud dependencies after setup. **Status: spec written, nothing built. Not urgent.**

## Done

- [x] Permission deadlock via PermissionRequest hook (concurrent_updates fix)
- [x] JSONL-based response detection
- [x] TelegramNode inline Allow/Deny buttons for permission requests
