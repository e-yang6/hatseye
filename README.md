# HATSEYE
AI-powered vision assistant for visually impaired users  
Voice-activated object recognition with real-time camera analysis and haptic obstacle feedback  

---

## Overview

Traditional vision assistance apps often require constant interaction and aren’t optimized for quick, one-sentence responses or physical proximity awareness.  
That’s why we built **HATSEYE**: a voice-activated assistant that combines AI-powered vision with **ultrasonic sensing + rumble motor haptics** to help visually impaired users understand and navigate their environment.

HATSEYE integrates voice recognition, real-time camera capture, the Google Gemini Vision API, and Arduino-based hardware feedback. Say **“hey hatseye”** to activate, ask a question naturally, get a clear one-sentence spoken response, and feel haptic feedback that indicates how close obstacles are.

---

## Features

- **Voice activation** with a natural wake word (“hey hatseye”)
- **Real-time camera analysis** for object and scene understanding
- **AI-powered responses** via Google Gemini Vision API
- **One-sentence answers** designed for speed and clarity
- **Text-to-speech output** for hands-free use
- **Hardware obstacle feedback** using ultrasonic sensors + rumble motors (haptics)
- **Arduino + serial integration** for live sensor/motor data
- **Simple web interface** for camera preview and system status

---

## Architecture

**Voice + Vision Pipeline**  
Voice Input → Wake Word Detection → Question Transcription → Camera Frame Capture → Gemini Vision → One-Sentence Answer → Text-to-Speech → Audio Response  

**Haptic Pipeline**  
Ultrasonic Sensors → Arduino → Serial Data → Backend Processing → Rumble Motor Feedback  

---

## Tech Stack

| Category | Technologies |
|---------|--------------|
| Frontend | HTML, CSS, JavaScript, Web Speech API |
| Backend | Python, Flask, OpenCV |
| AI | Google Gemini Vision API |
| Text-to-Speech | ElevenLabs |
| Hardware | Arduino, Ultrasonic Sensors, Rumble Motors |
| Communication | Serial (PySerial) |

---

## How It Works

1. User says **“hey hatseye”** to activate.
2. HATSEYE listens for a question about the current scene.
3. The system captures a camera frame in real time.
4. The image is sent to Gemini Vision for analysis.
5. Gemini returns a **single-sentence** response.
6. The response is spoken aloud via text-to-speech.
7. Meanwhile, ultrasonic sensors measure distance to obstacles.
8. Rumble motors provide **haptic feedback** based on proximity.

---

## Future Roadmap

- Mobile app support
- Offline/on-device processing for privacy and lower latency
- Multi-language support
- Improved haptic patterns and wearable form factors
- More customization for response style and feedback strength

---

## Team

- Ryan Gao  
- Ethan Yang  

---

## Links

- Devpost submission: https://devpost.com/software/hatseye
