import streamlit as st
from st_audiorec import st_audiorec
import tempfile
import os
from openai import OpenAI

# Set up the page configuration
st.set_page_config(page_title="Transcriber", layout="centered")

# Apply CSS to adjust layout
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize OpenAI client with secret API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Title and instructions
st.title("🗣️ AI-Powered Meeting Transcriber")
st.markdown("🎙️ Record your voice below and get an instant transcription powered by OpenAI Whisper!")

# Step 1: Record Audio
st.subheader("🎧 Record Your Voice")
wav_audio_data = st_audiorec()

# Step 2: Transcription
if wav_audio_data is not None:
    # Save audio to temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav_audio_data)
        file_path = f.name

    # Display loading animation
    st.info("Transcribing your audio... Please wait.")
    st.image("https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif", caption="AI is listening...", use_column_width=True)

    try:
        # Transcribe using OpenAI Whisper
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        # Show success message and result
        st.success("✅ Transcription Complete!")
        st.subheader("📝 Transcript")
        st.write(transcript.text)

        # Optional: playback the recorded audio
        st.audio(wav_audio_data, format='audio/wav')

    except Exception as e:
        st.error(f"❌ OpenAI Whisper API error: {e}")

    # Clean up temporary file
    os.remove(file_path)
else:
    st.caption("Click the microphone above to begin recording.")

