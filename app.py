import streamlit as st
import tempfile
import os
import speech_recognition as sr
import openai
from pydub import AudioSegment

# Load OpenAI API key securely from secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Voice Transcriber", layout="centered")
st.title("🎙️ Record or Upload & Transcribe Audio")
st.markdown("Use the built-in recorder or upload a `.wav` file to transcribe your voice.")

# HTML5 Voice Recorder
st.markdown("### 🎤 Record your voice")
st.components.v1.html(
    """
    <html>
    <body>
    <button onclick="startRecording()">🎙️ Start Recording</button>
    <button onclick="stopRecording()">⏹️ Stop & Download</button>
    <br><br>
    <audio id="audioPlayback" controls></audio>
    <script>
        let mediaRecorder;
        let audioChunks = [];

        async function startRecording() {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = document.getElementById('audioPlayback');
                audio.src = audioUrl;

                const link = document.createElement('a');
                link.href = audioUrl;
                link.download = 'recorded.wav';
                link.innerText = '⬇️ Download recording';
                document.body.appendChild(link);
            };

            mediaRecorder.start();
        }

        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
            }
        }
    </script>
    </body>
    </html>
    """,
    height=250,
)

# Upload Section
st.markdown("### 📤 Upload your `.wav` file to transcribe")
uploaded_file = st.file_uploader("Upload WAV audio file", type=["wav"])

def convert_to_pcm(input_path):
    output_path = input_path.replace(".wav", "_converted.wav")
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="wav", codec="pcm_s16le")
    return output_path

def transcribe_and_enhance(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        transcript = recognizer.recognize_google(audio)
        st.success("📝 Transcription")
        st.write(transcript)

        if st.button("✨ Enhance Transcript"):
            with st.spinner("Using GPT-4 to polish..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Improve grammar, clarity, and structure of this transcript."},
                        {"role": "user", "content": transcript}
                    ]
                )
                st.subheader("✅ Enhanced Transcript")
                st.markdown(response.choices[0].message["content"])

    except Exception as e:
        st.error(f"Transcription failed: {e}")
    finally:
        os.remove(audio_path)

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    try:
        converted_path = convert_to_pcm(tmp_path)
        transcribe_and_enhance(converted_path)
    finally:
        os.remove(tmp_path)
