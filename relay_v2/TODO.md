# Relay v2 — Dev TODO

## Pending

- [ ] **Message source metadata in responses** — Claude should know whether a message came from Telegram or CLI (or which CLI user, future multi-user). The `source` field already flows through QueueItem and is published with each response; expose it to the Claude prompt so it can tailor its reply (e.g. keep responses concise for Telegram, can be verbose for CLI). Consider injecting source into the PTY message prefix: `[from:telegram] user message here`.

## Done

- [x] Permission deadlock via PermissionRequest hook (concurrent_updates fix)
- [x] JSONL-based response detection
- [x] TelegramNode inline Allow/Deny buttons for permission requests
