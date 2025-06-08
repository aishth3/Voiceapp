# AI-Powered Transcriber 🎙️

This is a simple, browser-based voice-to-text app built using **Streamlit** and **OpenAI Whisper**.

As soon as you record your voice using the built-in mic recorder, the app automatically transcribes your speech using OpenAI's Whisper API and displays the result within seconds.

🚀 Live App: [https://transcribed.streamlit.app](https://transcribed.streamlit.app)

---

## Features

- Voice recording via microphone (no file uploads needed)
- Automatic transcription after recording (no extra clicks)
- Powered by OpenAI Whisper (`whisper-1` model)
- Clean, minimal interface with instant feedback

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) – for frontend and app hosting
- [st_audiorec](https://pypi.org/project/st-audiorec/) – for microphone recording
- [OpenAI Python SDK](https://github.com/openai/openai-python) – for Whisper integration

---

## 📦 Installation (for local dev)

1. Clone the repo or copy `app.py`
2. Create a `.streamlit/secrets.toml` file with your OpenAI key:

   ```toml
   OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
