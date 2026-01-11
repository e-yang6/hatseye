# HATSEYE
AI-powered vision assistant for visually impaired users  
Voice-activated object recognition with real-time camera analysis  

---
Overview
--------

Ever struggle with identifying objects in your daily life? Need a hands-free way to know what you're looking at?

Traditional vision assistance apps require constant interaction and aren't optimized for quick, single-sentence responses.  
That's why we built HATSEYE: a voice-activated vision analyzer that uses natural language wake words and AI-powered image analysis to help visually impaired users understand their surroundings.

HATSEYE combines voice recognition, real-time webcam streaming, Google Gemini Vision API, and Arduino sensor integration to provide instant, conversational assistance. Simply say "hey hats eye" to activate, ask your question naturally, and receive a clear, one-sentence answer about what you're seeing.

---

Features
--------

Core Capabilities  
- Voice Activation: Natural language wake word "hey hats eye" with flexible phonetic matching.  
- Real-time Webcam Streaming: Live camera feed with automatic camera detection and selection.  
- AI Vision Analysis: Google Gemini Vision API provides intelligent object identification and scene understanding.  
- Text-to-Speech: ElevenLabs integration delivers natural voice responses.  
- Single-Sentence Responses: Optimized prompts for clear, concise answers tailored for visually impaired users.  
- Arduino Integration: Real-time motor and sensor data display for haptic feedback systems.  
- Web GUI: Full-featured browser interface with minimalist design and webcam display.  

Technical Features  
- Wake Word Detection: Web Speech API with phonetic matching and keyword combination logic.  
- Image Capture: OpenCV-based frame capture with multi-camera support and auto-detection.  
- Audio Playback: Background sound effects for wake word detection and question received confirmation.  
- Serial Communication: PySerial integration for Arduino motor control and ultrasonic sensor data.  
- State Management: Independent API calls ensure no conversation history between requests.  
- Responsive Design: Clean, minimalist interface focused on webcam display and essential information.  
- Favicon Generation: Automatic color inversion with transparency preservation from source images.  

---

Architecture
------------

HATSEYE connects multiple systems into a unified vision assistance pipeline:

User Voice Input → Web Speech API → Wake Word Detection → Question Transcription → Webcam Frame Capture → Google Gemini Vision API → Text-to-Speech → Audio Response  
Camera Feed → OpenCV Processing → Frame Encoding → Base64 Encoding → Gemini API → Single-Sentence Analysis → ElevenLabs TTS  
Arduino Serial → PySerial Communication → Sensor Data Parsing → Motor Status Display → Real-time UI Updates  

---

Tech Stack
-----------

| Category | Technologies |
|-----------|---------------|
| Frontend | HTML5, CSS3, JavaScript (ES6), Web Speech API |
| Backend | Python 3.8+, Flask 2.3+, OpenCV (cv2) |
| AI & ML | Google Gemini Vision API, ElevenLabs Text-to-Speech |
| Hardware | Arduino (Ultrasonic Sensors, PWM Motors), PySerial |
| Image Processing | Pillow (PIL), NumPy |
| Audio | Pygame (backend), Web Audio API (frontend) |
| Web Framework | Flask with Jinja2 templating |

---

How It Works
------------

1. Wake Word Activation – User says "hey hats eye" (or phonetic variations), Web Speech API detects wake word with flexible matching.  
2. Question Capture – System listens for user's question about the visual scene, plays confirmation sound effect.  
3. Frame Capture – OpenCV captures current webcam frame from selected camera source with automatic camera detection.  
4. AI Analysis – Base64-encoded image sent to Google Gemini Vision API with optimized prompt for visually impaired assistance.  
5. Response Generation – Gemini provides single-sentence answer, sent to ElevenLabs for natural voice synthesis.  
6. Audio Playback – Text-to-speech audio played through browser, with visual indicators for system status.  
7. Arduino Integration – Real-time sensor data displayed showing motor intensity and distance measurements for haptic feedback.  

---

Data Sources
------------

- Web Speech API for real-time voice recognition and transcription
- OpenCV camera feed for live image capture
- Google Gemini Vision API for AI-powered image analysis and object identification
- ElevenLabs API for natural text-to-speech synthesis
- Arduino Serial Protocol for ultrasonic sensor and motor control data
- CSV configuration files for API keys and camera settings

---

Challenges Overcome
-------------------

- Integrated Web Speech API with flexible phonetic wake word matching for natural activation.  
- Built stateless Gemini API integration ensuring independent requests with no conversation history.  
- Implemented browser autoplay policy workarounds with user activation overlay for audio playback.  
- Created seamless Arduino serial communication with JSON parsing and auto-detection fallbacks.  
- Optimized master prompt for single-sentence responses tailored to visually impaired users.  
- Developed real-time webcam streaming with Flask and OpenCV frame encoding for low latency.  
- Integrated multiple audio systems (Pygame backend, Web Audio API frontend) with error handling.  

---

Future Roadmap
--------------

- Mobile App: Native iOS and Android applications with improved wake word detection.  
- Offline Mode: On-device AI processing for privacy and reduced latency.  
- Advanced Wake Word: Custom wake word training for personalized activation.  
- Multi-language Support: Translation and TTS in multiple languages.  
- Haptic Feedback: Enhanced Arduino motor patterns for different object types and distances.  
- Database Integration: Store question history and response patterns for improved assistance.  
- Wearable Integration: Support for smart glasses and wearable camera systems.  
- Custom Prompts: User-configurable master prompts for specialized use cases.  

---

Team
----

| Member |
|---------|
| (Add team member names here) |

---

Links
-----

- (Add project links here)
