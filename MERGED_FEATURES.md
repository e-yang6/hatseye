# HATSEYE - Merged Features (Roboflow + Arduino)

## ✅ Successfully Merged!

This branch (`roboflow-integration`) now combines two major features:

### 1. 🔍 Roboflow Road Damage Detection
- Custom YOLO model: `road-damage-lh70u-dk94k/1`
- Real-time object detection in webcam feed
- Smooth bounding box display (no flickering)
- Toggle button to start/stop detection
- Terminal logging for detected classes

### 2. 🤖 Arduino Connection
- Serial communication with Arduino
- Real-time motor intensity and distance display
- 4 motors (M1, M2, M3, M4) with sensor data
- Visual indicators with red dots (opacity based on intensity)
- Auto-detect Arduino port

## 🎯 Combined Features

Both features work simultaneously:
- **Roboflow detection**: Displays bounding boxes on road damage in the video feed
- **Arduino display**: Shows motor sensor data in the top-left corner
- **Voice interaction**: Gemini AI analysis with wake word detection
- **Text-to-speech**: ElevenLabs responses

## 🚀 How to Use

### Start the Server
```bash
cd /Users/ryan/Desktop/Hatseye2/hatseye
source .venv-roboflow/bin/activate
python3 web_gui.py
```

### Open Browser
Navigate to: http://localhost:8080

### Features in Web UI
1. **Webcam Feed**: Live camera with overlay
2. **Roboflow Toggle**: Click "🔍 Start Detection" to enable road damage detection
3. **Arduino Display**: Shows motor data (if Arduino is connected)
4. **Voice Activation**: Click "🎤 Activate" and say "hey hats eye" followed by your question
5. **Gemini AI**: Analyzes images and responds with voice

## 📁 New Files Added

### Arduino Files
- `arduino_integrated.ino` - Arduino sketch for sensors/motors
- `arduino_serial.py` - Python serial communication module
- `monitor_motors.py` - Motor monitoring utility

### Roboflow Files
- `roboflow_detector.py` - Roboflow Inference SDK integration
- `roboflow_http.py` - Original HTTP API (deprecated)
- `test_roboflow.py` - Test script for detection

### Documentation
- `ROBOFLOW_FIXED.md` - Roboflow setup guide
- `CUSTOM_MODEL_READY.md` - Custom model documentation
- `SMOOTH_DETECTION_FIXED.md` - Flickering fix details
- `MERGED_FEATURES.md` - This file

## 🔧 Configuration

Edit `config.py` (local only, not tracked):
```python
# Gemini API Key
GEMINI_API_KEY = "your-key-here"

# ElevenLabs API Key
ELEVENLABS_API_KEY = "your-key-here"

# Camera Index (None = auto-detect)
CAMERA_INDEX = None

# Arduino Connection (None = auto-detect)
ARDUINO_PORT = None  # or 'COM3', '/dev/ttyUSB0', etc.
ARDUINO_BAUDRATE = 9600
```

## 📊 System Status

Server startup shows:
```
✓ Roboflow detector available
✓ Webcam initialized successfully
✓ Connected! Found 34 available model(s)
✓ ElevenLabs text-to-speech available
✓ Arduino connected
```

## 🎨 Web UI Features

### Top-Left Corner
- Arduino motor data display (when connected)
- Format: `M1: 123 (45cm)  M2: 89 (32cm)  M3: 156 (18cm)  M4: 34 (67cm)`
- Red dots indicate intensity (brighter = stronger)

### Center-Bottom
- Roboflow toggle button
- "🔍 Start Detection" / "🛑 Stop Detection"

### Bottom Panel
- Voice activation button
- Question input field
- Response display area

## 🔀 Branch Info

- **Current branch**: `roboflow-integration`
- **Main branch**: Unchanged (safe)
- **Merge commit**: `3b368c4`

To merge into main later:
```bash
git checkout main
git merge roboflow-integration
```

## ✨ What's Working

✅ Roboflow road damage detection  
✅ Arduino motor data display  
✅ Gemini AI image analysis  
✅ Voice wake word detection  
✅ Text-to-speech responses  
✅ Smooth bounding boxes (no flickering)  
✅ Real-time motor sensor updates  
✅ Combined UI with both features  

## 🎉 Success!

Both features are now integrated and working together in the same web application!
