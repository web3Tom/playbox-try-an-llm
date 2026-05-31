# Audio Transcription Demo

## Goal

Demonstrates audio transcription and diarization using Azure OpenAI's `gpt-4o-transcribe-diarize` endpoint. Illustrates enterprise audio processing workflows.

## How to Run

```bash
uv run python demos/transcription/transcribe.py
```

## Environment Variables

- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI deployment endpoint
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key

## Expected Workflow

1. Load audio file (`sample_audio.mp4`)
2. Call `client.audio.transcriptions.create(model="gpt-4o-transcribe-diarize", file=...)`
3. Parse and return transcript with diarization metadata

Point the `audio_file` path in `main()` at a real audio file to run it against your own recording.
