# HATSEYE - Voice-Centered Vision Analyzer

A voice-activated vision analyzer that uses wake word "hey hats eye" to activate, then listens for your question. Captures a webcam frame and analyzes it using Google's Gemini Vision API to identify objects you're holding and extract visible text.

## Features

- **Voice-activated**: Wake word "hey hats eye" to activate
- **Speech-to-text**: Speak your questions naturally
- **Visual indicators**: Shows when listening and processing
- **Conversational responses**: AI responds naturally as if speaking to you
- **Single frame capture**: Captures webcam frame only when activated
- **Object detection**: Identifies what you're holding
- **Text reading**: Extracts visible text from images

## Installation

### Quick Start (Using Virtual Environment)

A virtual environment is already set up with Python 3.8 and PyAudio installed.

**To activate the virtual environment:**
- **Windows PowerShell/CMD:** Run `.\activate_venv.bat` or manually:
  ```bash
  .\venv\Scripts\activate
  ```

**To run the application:**
```bash
python webcam_gemini.py
```

### Manual Installation (If needed)

If you want to set up from scratch:

1. Create a virtual environment with Python 3.8 (PyAudio works best with 3.8-3.13):
   ```bash
   py -3.8 -m venv venv
   .\venv\Scripts\activate
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pyaudio
   ```

### Installing PyAudio (Required for Voice Features)

**Python Version Compatibility:**
PyAudio officially supports Python **2.7 through 3.13**. Python 3.14 is very new and doesn't have official PyAudio wheels yet.

**Windows (Python 3.14):**
If you're using Python 3.14, you have a few options:

**Option 1: Download and install a pre-built wheel manually**
1. Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Download the wheel file matching your Python version and architecture (e.g., `PyAudio-0.2.11-cp314-cp314-win_amd64.whl`)
3. Install it: `pip install PyAudio-0.2.11-cp314-cp314-win_amd64.whl`

**Option 2: Use Python 3.13 (Recommended)**
Install Python 3.13 and use it for this project. PyAudio has official wheels for Python 3.13.

**Option 3: Use text input mode (no voice features)**
If PyAudio is not installed, the app will automatically fall back to text input mode where you can type your questions instead of speaking them. This works with any Python version and provides all vision features without voice.

**Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Note**: If PyAudio is not installed, the app will automatically work in text input mode.

## Usage

Run the application:
```bash
python webcam_gemini.py
```

### Voice Commands:

1. Say **"hey hats eye"** to wake up the assistant
2. Wait for the listening indicator (👂)
3. Speak your question (e.g., "what am I holding?" or "read the text")
4. The assistant will capture a webcam frame, analyze it, and respond conversationally

Press `Ctrl+C` to exit the application.

## Example Flow

```
🔇 Waiting for wake word "hey hats eye"...
✨ Wake word detected!

👂 Listening for your question...
🎤 Listening... ✓
   Transcribing... ✓
   You said: "what am I holding?"

📸 Capturing webcam frame...
🤖 Analyzing with AI...

💬 Response:
────────────────────────────────────────────
You're holding a coffee mug.
────────────────────────────────────────────
```

## Requirements

- Python 3.7+
- Webcam access
- Microphone access
- Google Gemini API key (configured in `config.py`)
- Internet connection (for speech recognition and Gemini API)

## Configuration

The Gemini API key is stored in `config.py`. Make sure your API key has access to vision-capable models.
