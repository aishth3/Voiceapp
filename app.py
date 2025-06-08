import streamlit as st
import tempfile
import os
import speech_recognition as sr
from openai import OpenAI
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, ClientSettings
import av
import numpy as np
import wave

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Voice Transcriber", layout="centered")
st.title("🎙️ Upload or Record Audio & Transcribe")
st.markdown("Upload a `.wav` file or record audio to get transcription and enhancement.")

# ---------- File Upload Section ----------
uploaded_file = st.file_uploader("📤 Upload a WAV audio file", type=["wav"])

# ---------- WebRTC Audio Recording Section ----------
st.markdown("### Or record your voice below:")

class AudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray().flatten()
        self.frames.append(audio)
        return frame

ctx = webrtc_streamer(
    key="send_audio",
    mode="sendonly",
    in_audio=True,
    client_settings=ClientSettings(media_stream_constraints={"audio": True, "video": False}),
    audio_processor_factory=AudioProcessor,
)

recorded_audio_path = None

if ctx.state.playing and ctx.audio_processor:
    if st.button("📥 Save Recording"):
        # Save the recorded raw audio as a .wav file
        raw_audio = np.concatenate(ctx.audio_processor.frames, axis=0)
        sample_rate = 48000  # WebRTC default sample rate
        recorded_audio_path = os.path.join(tempfile.gettempdir(), "recorded.wav")

        with wave.open(recorded_audio_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(sample_rate)
            wf.writeframes(raw_audio.astype(np.int16).tobytes())

        st.audio(recorded_audio_path, format="audio/wav")
        st.success("Recording saved!")

# ---------- Transcription + Enhancement Logic ----------
def transcribe_and_enhance(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        transcript = recognizer.recognize_google(audio)
        st.success("📝 Transcription")
        st.write(transcript)

        if st.button("✨ Enhance Transcript"):
            with st.spinner("Polishing with GPT-4..."):
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
        os.remove(audio_path)

# ---------- Trigger Transcription ----------
if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/wav')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    transcribe_and_enhance(tmp_path)

elif recorded_audio_path is not None:
    transcribe_and_enhance(recorded_audio_path)
