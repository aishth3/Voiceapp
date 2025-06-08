import streamlit as st
from st_audiorec import st_audiorec
import tempfile
import os
from openai import OpenAI

# Page config
st.set_page_config(page_title="Transcriber", layout="centered")

# Layout adjustment
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Title
st.title("AI-Powered Transcriber")
st.write("Record your voice OR upload an audio file, then click Transcribe to view the text.")

# Section 1: Audio Recorder
st.subheader("Option 1: Record Audio")
wav_audio_data = st_audiorec()

# Section 2: File Upload Fallback
st.subheader("Option 2: Upload Audio File")
uploaded_file = st.file_uploader("Upload a .wav, .mp3, or .m4a file", type=["wav", "mp3", "m4a"])

# Use recorded audio if available; else use uploaded file
audio_source = None
audio_format = None

if wav_audio_data:
    st.audio(wav_audio_data, format='audio/wav')
    audio_source = wav_audio_data
    audio_format = 'recorded'

elif uploaded_file is not None:
    st.audio(uploaded_file)
    audio_source = uploaded_file.read()
    audio_format = 'uploaded'

# Transcription button
if audio_source:
    if st.button("Transcribe"):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_source)
            file_path = f.name

        with st.spinner("Transcribing..."):
            try:
                with open(file_path, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )

                st.success("Transcription Complete")
                st.subheader("Transcript")
                st.write(transcript.text)

            except Exception as e:
                st.error(f"Error during transcription: {e}")

            finally:
                os.remove(file_path)

else:
    st.info("Please record audio or upload a file to enable transcription.")
