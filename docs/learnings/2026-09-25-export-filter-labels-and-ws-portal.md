# 2026-09-25 — export filter labels and websocket portal

Steps: S-028, S-029 · Branch: arena/01a0c936-cutting-edge-v2 · Commits: local

## What broke
- ffmpeg 4.2 rejected a bed graph that reused `[a0]` and a hidden `.partial` name.
- TestClient `receive_json` never delivered the terminal job message.

## Root cause
- A filter label can feed only one input unless `asplit` copies it. A leading-dot partial has no muxer suffix. Starlette's portal cannot run the server task while the client blocks inside `portal.call`.

## Rule
- Fan out audio with `asplit`, write `name.partial.mp4`, and prove `/ws/jobs/{id}` with a real uvicorn socket, not TestClient.
