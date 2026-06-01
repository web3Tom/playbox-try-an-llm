<!-- FOR AI AGENTS. Scoped to demos/transcription/ — the closest AGENTS.md wins. -->
<!-- Generated with the agent-rules skill (scoped). Edit content, not structure. -->

# AGENTS.md — transcription demo

<!-- AGENTS-GENERATED:START overview -->
## Overview
Multimodal audio processing: transcribe an audio file with speaker diarization via Azure OpenAI's
`gpt-4o-transcribe-diarize` endpoint. Demonstrates a specialized, single-purpose model route
distinct from the text/chat models.
<!-- AGENTS-GENERATED:END overview -->

<!-- AGENTS-GENERATED:START filemap -->
## Key Files
| File | Purpose |
|------|---------|
| `transcribe.py` | `init_azure_client` → `transcribe_audio` (opens file, calls `gpt-4o-transcribe-diarize`) |
| `README.md` | Human-facing walkthrough |
<!-- AGENTS-GENERATED:END filemap -->

<!-- AGENTS-GENERATED:START commands -->
## Run it
| Task | Command | Env vars |
|------|---------|----------|
| Transcribe an audio file | `uv run python demos/transcription/transcribe.py` | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` |

`main()` points `audio_file` at `sample_audio.mp4` — **not committed**. Supply your own recording
(or edit the path) before running; `transcribe_audio` raises `FileNotFoundError` if it is missing.
<!-- AGENTS-GENERATED:END commands -->

## Routing lesson (why this demo exists)
| Job | Role / model | Why |
|-----|--------------|-----|
| Transcribe + diarize audio | `gpt-4o-transcribe-diarize` | A specialized multimodal route — text models cannot do this |

There is no chat model in this path. The lesson: **match the modality to the model.** Pick the
audio endpoint for audio; don't try to coerce a general chat model into it.

<!-- AGENTS-GENERATED:START code-style -->
## Code style
- Python 3.10+, PEP 8, type hints (`-> AzureOpenAI | None`, `-> str`).
- Open audio in binary (`"rb"`); guard with `os.path.exists` before the API call.
- Catch `APIError` from the transcription endpoint distinctly from `FileNotFoundError`.
<!-- AGENTS-GENERATED:END code-style -->

## Boundaries (delta from root)
- **Never** commit audio fixtures containing real recordings / PII (`.mp4` stays out of the repo).
- **Ask first** before adding batch processing or an `audio/` input directory — the demo is single-file by design.

## When stuck
- `FileNotFoundError` → supply `sample_audio.mp4` or repoint `audio_file` in `main()`.
- Root conventions: repo-root `AGENTS.md`. Routing table: root `AGENTS.md` Heuristics.
