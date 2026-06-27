# ODIN

**ODIN** is my personal, local-first AI assistant — it runs entirely on my own
machine, answers to me ("sir"), and is being grown into a voice-driven helper
for my daily life.

> ODIN is a personal fork of [OpenJarvis](https://github.com/open-jarvis/OpenJarvis),
> the local-first personal-AI framework from Stanford's Scaling Intelligence Lab.
> All credit for the underlying engine goes to the OpenJarvis project; ODIN is my
> customized build on top of it. Licensed under Apache 2.0 — see
> [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

## What ODIN is

A private assistant that reasons, remembers, and (soon) speaks — with no cloud
dependency and no API bills. The model runs locally via Ollama, so my data never
leaves my hardware. ODIN has his own personality, addresses me as "sir," and
opens each session with a short briefing.

## My setup

- **Host:** self-hosted on WSL2 (Ubuntu) on Windows
- **GPU:** NVIDIA RTX 4060 (8 GB)
- **Engine:** Ollama (local inference)
- **Models:** `llama3.1:8b` for everyday chat, `qwen3.5:9b` for heavier reasoning,
  `nomic-embed-text` for memory
- **Interfaces:** a custom browser console + voice via Siri Shortcuts

## Running it

```bash
odin ask "What's on for today?"     # one-shot question
odin chat                           # interactive session
```

`odin` is a thin launcher around the engine; configuration lives in `~/.openjarvis/`.

## Roadmap

- [x] Local brain + memory + personality
- [x] Custom console + Siri voice trigger
- [ ] Text-to-speech (local) so ODIN talks back
- [ ] Calendar / email so the daily briefing goes live
- [ ] Scheduling & automation
- [ ] Music control

## Credit & license

ODIN stands on the shoulders of
[OpenJarvis](https://github.com/open-jarvis/OpenJarvis) by the Stanford Scaling
Intelligence Lab and contributors. Their framework does the heavy lifting; my
fork adds branding, configuration, and personal customizations.

Licensed under the **Apache License 2.0**. The original copyright and license are
retained in [`LICENSE`](LICENSE); modifications and attribution are documented in
[`NOTICE`](NOTICE).
