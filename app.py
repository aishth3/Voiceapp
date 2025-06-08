import streamlit as st
from streamlit_audiorecorder import audiorecorder
import tempfile
import os
import speech_recognition as sr
from openai import OpenAI

# Load OpenAI client using Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Page setup
st.set_page_config(page_title="AI-Powered Transcriber", layout="centered")

# CSS to adjust padding
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🎙️ AI-Powered Transcriber")
st.write("Record your voice and get a clean transcript.")

# Step 1: Record audio
st.subheader("Step 1: Record")
audio_data = audiorecorder("Click to record", "Recording...")

# Step 2: Transcribe if recording exists
if audio_data is not None:
    st.audio(audio_data.tobytes(), format='audio/wav')

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_data.tobytes())
        file_path = f.name

    recognizer = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)

    try:
        transcript = recognizer.recognize_google(audio)
        st.success("Raw Transcript:")
        st.write(transcript)

        if st.button(" Enhance Transcript"):
            with st.spinner("Improving clarity and grammar..."):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant. Clean up the user's spoken transcript for grammar, clarity, and readability."
                        },
                        {"role": "user", "content": transcript}
                    ]
                )
                st.markdown("### Enhanced Transcript")
                st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Transcription error: {e}")

    finally:
        os.remove(file_path)
else:
    st.info("Click the button above to start recording your voice.")
