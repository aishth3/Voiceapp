import streamlit as st
from st_audiorec import st_audiorec
import tempfile
import os
from openai import OpenAI


st.set_page_config(page_title="Transcriber", layout="centered")
# Apply CSS to move interface higher
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize OpenAI client
client = OpenAI(api_key="api_key")
st.title("AI-Powered Meeting Transcriber")
st.markdown("Record your voice below and get an instant transcription!!")

# Step 1: Record audio
st.subheader("Record Your Voice")
wav_audio_data = st_audiorec()

# Step 2: Transcribe using OpenAI Whisper
if wav_audio_data is not None:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav_audio_data)
        file_path = f.name

    st.info("Transcribing your audio...")

    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        st.success("Transcription:")
        st.write(transcript.text)

    except Exception as e:
        st.error(f"OpenAI Whisper API error: {e}")

    # Clean up temporary file
    os.remove(file_path)
