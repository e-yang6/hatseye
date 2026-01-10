# Windows Installation Guide

## PyAudio Installation on Windows

### PyAudio Python Version Compatibility

PyAudio officially supports Python versions **2.7 through 3.13**. As of November 2024, PyAudio 0.2.14 provides pre-built wheels for Python 3.13 on Windows.

**Current Status for Python 3.14:**
- ❌ No official wheels available yet (Python 3.14 was just released)
- ⚠️ You may need to wait for PyAudio updates or use Python 3.13

### Your Current Setup
- You're using: **Python 3.14.0**
- PyAudio compatibility: **Not yet officially supported**

### Options for Python 3.14

#### Option 1: Use Python 3.13 (Recommended for now)
Install Python 3.13 and use it for this project:
1. Download Python 3.13 from python.org
2. Install it (keep Python 3.14 as well)
3. Create a virtual environment with Python 3.13:
   ```bash
   py -3.13 -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   pip install pyaudio
   ```

#### Option 2: Try an unofficial wheel (if available)
Check if there's a community-built wheel for Python 3.14:
1. Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Look for Python 3.14 wheels (may not exist yet)
3. If found, download and install:
   ```bash
   pip install PyAudio-0.2.XX-cp314-cp314-win_amd64.whl
   ```

#### Option 3: Build from source (Advanced)
Requires Visual C++ Build Tools and PortAudio:
1. Install Visual Studio Build Tools
2. Download PortAudio source
3. Compile PyAudio from source

#### Option 4: Use text input mode (No voice features)
The app will automatically work in text input mode if PyAudio is not installed.
You can still use all vision features by typing your questions.

### Method 2: Direct Wheel Installation (For Python 3.13 and earlier)

1. Check your Python version and architecture:
   ```bash
   python --version
   python -c "import platform; print(platform.machine())"
   ```

2. Download the appropriate wheel from:
   https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

   Look for a file like: `PyAudio-0.2.14-cp313-cp313-win_amd64.whl`
   (Replace `cp313` with your Python version and `win_amd64` with your architecture)

3. Install the wheel:
   ```bash
   pip install PyAudio-0.2.14-cp313-cp313-win_amd64.whl
   ```

### Method 3: Using Conda (if you have Anaconda/Miniconda)

```bash
conda install -c conda-forge pyaudio
```

**Note**: Conda may not have Python 3.14 support yet either.

## After Installing PyAudio

Once PyAudio is installed, install the rest of the dependencies:

```bash
pip install -r requirements.txt
```

## Troubleshooting

If you still encounter issues:
- Make sure you have Visual C++ Build Tools installed (PyAudio needs it to compile)
- Try installing an older version: `pip install pyaudio==0.2.11.1`
- As a last resort, you can use the text input mode (the app will automatically fall back if PyAudio is not available)
