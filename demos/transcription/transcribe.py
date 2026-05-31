"""
Audio transcription demo using Azure OpenAI's gpt-4o-transcribe-diarize endpoint.

NOTE: The gpt-4o-transcribe-diarize endpoint is not yet deployed in this Azure environment.
This script demonstrates the correct structure and API call; actual transcription will fail
until the endpoint becomes available.

Env vars:
  AZURE_OPENAI_ENDPOINT: Azure OpenAI deployment endpoint
  AZURE_OPENAI_API_KEY: Azure OpenAI API key
"""

import logging
import os

from openai import AzureOpenAI, APIError

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def init_azure_client() -> AzureOpenAI | None:
    """Initialize Azure OpenAI client from environment variables."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    if not endpoint or not api_key:
        logger.error("Missing Azure credentials: AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY not set")
        return None

    try:
        return AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-15-preview"
        )
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI client: {e}")
        return None


def transcribe_audio(client: AzureOpenAI, audio_file_path: str) -> str:
    """Transcribe audio file using gpt-4o-transcribe-diarize endpoint."""
    try:
        if not os.path.exists(audio_file_path):
            logger.error(f"Audio file not found: {audio_file_path}")
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        logger.info(f"Transcribing: {audio_file_path}")

        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="gpt-4o-transcribe-diarize",
                file=audio_file
            )

        transcription = response.text if hasattr(response, 'text') else str(response)
        logger.info(f"Transcription complete: {len(transcription)} characters")
        return transcription

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        raise
    except APIError as e:
        if "not deployed" in str(e).lower() or "not found" in str(e).lower():
            logger.error("gpt-4o-transcribe-diarize endpoint is not yet deployed in this Azure environment.")
            logger.info("This demo is illustrative. Endpoint availability: check Azure OpenAI deployment status.")
            raise RuntimeError("Transcription endpoint not yet deployed.") from e
        logger.error(f"API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during transcription: {e}")
        raise


def main():
    """Run transcription demo."""
    client = init_azure_client()
    if not client:
        logger.error("Cannot proceed without Azure OpenAI client.")
        return

    audio_file = "sample_audio.mp4"
    logger.info(f"Demo: transcribe {audio_file}")

    try:
        result = transcribe_audio(client, audio_file)
        print(f"\nTranscription:\n{result}")
    except RuntimeError as e:
        logger.warning(f"Demo skipped: {e}")
        print(f"⚠️  {e}")
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise


if __name__ == "__main__":
    main()
