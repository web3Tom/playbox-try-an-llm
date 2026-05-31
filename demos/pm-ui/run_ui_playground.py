"""
Streamlit chat UI for product managers to interact with Azure OpenAI models.

Provides a non-technical entry point for exploring different GPT-5 series models
via a simple chat interface. Users can select model variant and engage in conversation.

Env vars:
  AZURE_OPENAI_ENDPOINT: Azure OpenAI deployment endpoint
  AZURE_OPENAI_API_KEY: Azure OpenAI API key
"""

import logging
import os
import sys

import streamlit as st
from openai import AzureOpenAI, OpenAIError

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def init_azure_client() -> AzureOpenAI | None:
    """Initialize Azure OpenAI client from environment variables."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    if not endpoint or not api_key:
        logger.warning("Missing Azure credentials: AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY not set")
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


def main():
    """Main Streamlit app."""
    st.set_page_config(page_title="Polestar Playbox — Chat Interface", layout="wide")
    st.title("Polestar Playbox — Chat Interface")
    st.markdown("Explore different GPT-5 series models for PM workflows.")

    client = init_azure_client()
    if not client:
        st.warning(
            "⚠️ Missing Azure OpenAI credentials. "
            "Please set `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` environment variables."
        )
        st.info("**Run this app on port 8501:** `uv run streamlit run demos/pm-ui/run_ui_playground.py`")
        return

    col1, col2 = st.columns([3, 1])
    with col2:
        model_choice = st.selectbox(
            "Select Model",
            ["gpt-5.4", "gpt-5.4-mini", "gpt-5.4-nano", "gpt-5.2"],
            help="Choose the model variant for this conversation."
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                logger.info(f"Sending message to {model_choice}")
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
                )
                assistant_message = response.choices[0].message.content
                message_placeholder.markdown(assistant_message)
                st.session_state.messages.append({"role": "assistant", "content": assistant_message})
                logger.info(f"Received response from {model_choice}")
            except OpenAIError as e:
                error_msg = f"API Error: {str(e)}"
                logger.error(error_msg)
                st.error(error_msg)
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(error_msg)
                st.error(error_msg)


if __name__ == "__main__":
    main()
