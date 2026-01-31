# 🌌 GraviClip: Anti-Gravity Editor

GraviClip is an automated video processing tool designed to turn horizontal YouTube videos into vertical, captioned TikTok-ready clips (9:16) using AI.

## Features
- **Zero-G Download**: Efficiently downloads video sections using `yt-dlp`.
- **Grav-Warp**: Smart center-cropping to converting landscape (16:9) to portrait (9:16).
- **Levitation Subtitles**: Uses OpenAI's **Whisper** to generate subtitles and **FFmpeg** to burn them with a bold, readable aesthetic.
- **Anti-Gravity GUI**: A futuristic Streamlit interface for easy control.

## Installation

1. Install Python Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. System Dependencies:
   - **FFmpeg**: Must be installed and accessible. (The code includes a hardcoded fallback to `C:\ffmpeg\bin` for Windows users).

## Usage

Run the interface:
```bash
streamlit run app.py
```
