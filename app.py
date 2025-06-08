import streamlit as st
from st_audiorec import st_audiorec
import tempfile
import os
from openai import OpenAI

# Set page config
st.set_page_config(page_title="Transcriber", layout="centered")

# Apply CSS to shift layout up
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
    }
    img.loading-gif {
        width: 50px !important;
        height: auto;
        margin: 10px auto;
        display: block;
    }
    </style>
""", unsafe_allow_html=True)

# Set up OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# App Title
st.title(" AI-Powered Meeting Transcriber")
st.markdown(" Record your voice and click **Transcribe** to get instant results!")

# Step 1: Record audio
st.subheader(" Record Your Voice")
wav_audio_data = st_audiorec()

# Step 2: Display Transcribe button
if wav_audio_data:
    st.audio(wav_audio_data, format='audio/wav')
    if st.button(" Transcribe"):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(wav_audio_data)
            file_path = f.name

        # Show small loading animation
        st.markdown(
            '<img src="https://i.gifer.com/ZZ5H.gif" class="loading-gif" alt="Loading...">',
            unsafe_allow_html=True
        )
        st.info("Transcribing audio...")

        try:
            with open(file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )

            st.success(" Transcription Complete!")
            st.subheader(" Transcript")
            st.write(transcript.text)

        except Exception as e:
            st.error(f"❌ OpenAI Whisper API error: {e}")

        os.remove(file_path)
else:
    st.caption("Click the microphone above to record your voice.")
