import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import speech_recognition as sr
import tempfile
import numpy as np
import av
from pydub import AudioSegment
import os
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Voice Transcriber", layout="centered")
st.title("🎙️ AI Voice Transcriber with GPT-4 Enhancement")

# Buffer to collect audio frames
audio_frames = []

class AudioProcessor:
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        audio_frames.append(audio)
        return frame

# Start WebRTC
webrtc_ctx = webrtc_streamer(
    key="audio",
    mode=WebRtcMode.SENDONLY,
    client_settings=ClientSettings(media_stream_constraints={"audio": True, "video": False}),
    audio_receiver_size=1024,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"audio": True},
    sendback_audio=False,
    audio_processor_factory=AudioProcessor,
)

if webrtc_ctx.state.playing:
    st.success("🎙 Recording started. Speak now.")

    if st.button("📝 Transcribe Now"):
        if not audio_frames:
            st.warning("No audio captured yet.")
        else:
            st.info("Transcribing...")

            audio_np = np.concatenate(audio_frames, axis=0).astype(np.int16)
            sample_rate = 48000

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                segment = AudioSegment(
                    audio_np.tobytes(),
                    frame_rate=sample_rate,
                    sample_width=2,
                    channels=1
                )
                segment.export(f.name, format="wav")
                temp_path = f.name

            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_path) as source:
                audio = recognizer.record(source)

            try:
                transcript = recognizer.recognize_google(audio)
                st.success("Transcript:")
                st.write(transcript)

                if st.button("✨ Enhance with GPT-4"):
                    with st.spinner("Enhancing..."):
                        response = client.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": "Fix grammar and clarity of this transcript."},
                                {"role": "user", "content": transcript}
                            ]
                        )
                        st.subheader("Enhanced Transcript")
                        st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"Transcription failed: {e}")
            finally:
                os.remove(temp_path)

else:
    st.info("🛑
