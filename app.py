import streamlit as st
from st_audiorec import st_audiorec
import tempfile
import os
import speech_recognition as sr
from openai import OpenAI

# Load OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Page setup
st.set_page_config(page_title="AI-Powered Transcriber", layout="centered")

# CSS for layout tweak
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("AI-Powered Transcriber")
st.write("Record your voice below. We'll transcribe and polish it using AI!")

# Step 1: Record audio
st.subheader("Step 1: Record Audio")
wav_audio_data = st_audiorec()

# Step 2: Transcribe and Enhance
if wav_audio_data:
    st.audio(wav_audio_data, format='audio/wav')

    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav_audio_data)
        file_path = f.name

    recognizer = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)

    try:
        # Raw transcription with Google SpeechRecognition
        raw_transcript = recognizer.recognize_google(audio)
        st.success("Raw Transcription:")
        st.write(raw_transcript)

        if st.button(" Enhance Transcript"):
            with st.spinner("Enhancing with GPT-4..."):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant who rewrites transcripts to improve grammar, clarity, and formatting."
                        },
                        {
                            "role": "user",
                            "content": raw_transcript
                        }
                    ]
                )
                enhanced = response.choices[0].message.content
                st.markdown("### ✨ Enhanced Transcript")
                st.markdown(enhanced)

    except Exception as e:
        st.error(f"Transcription error: {e}")

    finally:
        os.remove(file_path)

else:
    st.info("Click the microphone above and speak to start transcription.")

