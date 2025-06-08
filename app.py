import streamlit as st
from st_audiorec import st_audiorec
import tempfile
import os
from openai import OpenAI

# Page setup
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

# App header
st.title("AI-Powered Transcriber")
st.write("Record your voice and click Transcribe to view your transcript.")

# Record audio
st.subheader("Record Audio")
wav_audio_data = st_audiorec()

# If audio was recorded, show button
if wav_audio_data:
    st.audio(wav_audio_data, format='audio/wav')
    
    if st.button("Transcribe"):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(wav_audio_data)
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
                st.error(f"Error: {e}")
            finally:
                os.remove(file_path)
else:
    st.caption("Click the mic above to start recording.")
