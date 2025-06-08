import streamlit as st
import tempfile
import os
import speech_recognition as sr
from openai import OpenAI

# Load OpenAI client securely
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Voice Transcriber", layout="centered")
st.title("🎙️ Upload Audio & Transcribe")
st.markdown("Upload a `.wav` file to get transcription and enhancement.")

# Upload audio file
uploaded_file = st.file_uploader("📤 Upload a WAV audio file", type=["wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/wav')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(tmp_path) as source:
        audio = recognizer.record(source)

    try:
        transcript = recognizer.recognize_google(audio)
        st.success("📝 Transcription")
        st.write(transcript)

        if st.button("✨ Enhance Transcript"):
            with st.spinner("Polishing..."):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Improve grammar, clarity, and structure of this transcript."},
                        {"role": "user", "content": transcript}
                    ]
                )
                st.subheader("✅ Enhanced Transcript")
                st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Transcription failed: {e}")
    finally:
        os.remove(tmp_path)

