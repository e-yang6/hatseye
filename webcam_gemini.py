#!/usr/bin/env python3
"""
HATSEYE - Voice-Centered Vision Analyzer
Uses wake word "hey hats eye" to activate, then listens for questions
Captures webcam frame and analyzes using Gemini API
"""

import cv2
import sys
import time
import json
import base64
import requests
import tempfile
import os
from PIL import Image
from io import BytesIO
from config import GEMINI_API_KEY, ELEVENLABS_API_KEY, CAMERA_INDEX

# Try to import ElevenLabs for text-to-speech
ELEVENLABS_AVAILABLE = False
elevenlabs_client = None
play_audio_func = None
try:
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
    # Initialize ElevenLabs client with API key
    elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    
    # Try to use pygame for audio playback (works on Windows without ffmpeg)
    try:
        import pygame
        pygame.mixer.init()
        play_audio_func = "pygame"
    except ImportError:
        # Fallback to elevenlabs play if pygame not available
        try:
            from elevenlabs.play import play as play_audio_func
        except:
            play_audio_func = None
except ImportError:
    pass
except Exception as e:
    print(f"Warning: Could not initialize ElevenLabs: {e}")
    ELEVENLABS_AVAILABLE = False

# Try to import speech recognition, with fallback if PyAudio is not available
AUDIO_AVAILABLE = False
sr = None
try:
    import speech_recognition as sr
    AUDIO_AVAILABLE = True
except (ImportError, OSError):
    # PyAudio not available - will use text input mode
    pass

def list_available_cameras():
    """List all available camera indices"""
    available = []
    # Try up to 10 camera indices
    for i in range(10):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                # Try to read a frame to confirm it works
                ret, _ = cap.read()
                if ret:
                    available.append(i)
                cap.release()
        except:
            continue
    return available

def capture_webcam_frame():
    """Capture a single frame from the default webcam"""
    # Try different approaches on Windows - DirectShow is often more reliable than MSMF
    # CAP_DSHOW = 700 for DirectShow backend on Windows
    try:
        CAP_DSHOW = 700  # DirectShow backend constant
    except:
        CAP_DSHOW = cv2.CAP_ANY  # Fallback if constant not available
    
    backends = [
        (CAP_DSHOW, "DirectShow"),  # Try DirectShow first on Windows (more reliable)
        (cv2.CAP_ANY, "Default"),   # Fall back to default
    ]
    
    cap = None
    # Use configured camera index, or try camera indices in order if None
    if CAMERA_INDEX is not None:
        camera_indices = [CAMERA_INDEX]  # Use configured camera index
    else:
        camera_indices = [0, 1, 2]  # Auto-detect: try first 3 camera indices (0 is usually default)
    
    for backend, backend_name in backends:
        for camera_index in camera_indices:
            try:
                cap = cv2.VideoCapture(camera_index, backend)
                
                if cap.isOpened():
                    # Minimal initialization delay
                    time.sleep(0.1)
                    
                    # Set smaller size for speed
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 512)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)
                    
                    # Read one frame only (skip warmup for speed)
                    ret, frame = cap.read()
                    if ret and frame is not None and frame.size > 0:
                        # Convert BGR to RGB for PIL and resize immediately
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil_image = Image.fromarray(frame_rgb)
                        
                        # Resize to smaller size immediately for faster processing
                        max_size = (512, 512)
                        if pil_image.size[0] > max_size[0] or pil_image.size[1] > max_size[1]:
                            pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
                        
                        cap.release()
                        return pil_image
                    else:
                        cap.release()
                        cap = None
                else:
                    if cap:
                        cap.release()
                    cap = None
            except Exception as e:
                if cap:
                    try:
                        cap.release()
                    except:
                        pass
                cap = None
                continue  # Try next camera index
        
        # If we found a working camera with this backend, break
        if cap and cap.isOpened():
            break
    
    return None

def list_available_models():
    """List available models using REST API"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            available = []
            model_details = []
            for m in data.get('models', []):
                model_name = m.get('name', '').replace('models/', '')
                methods = m.get('supportedGenerationMethods', [])
                if 'generateContent' in methods:
                    available.append(model_name)
                    model_details.append({
                        'name': model_name,
                        'methods': methods
                    })
            return available, model_details
        else:
            print(f"Error listing models: {response.status_code}", file=sys.stderr)
            return [], []
    except Exception as e:
        print(f"Error listing models: {e}", file=sys.stderr)
        return [], []

def image_to_base64(image):
    """Convert PIL Image to base64 string - optimized for speed"""
    # Resize image to smaller size for faster upload and processing
    max_size = (512, 512)  # Smaller size = faster
    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Use lower quality for faster encoding
    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=75, optimize=True)
    img_bytes = buffered.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')

# Cache model list to avoid repeated API calls
_cached_model = None
_cached_available_models = None  # Cache the list of available models globally

def analyze_image_with_gemini(image, user_prompt):
    """
    Send image to Gemini API for analysis - optimized for speed with proper error handling.
    Each call is completely independent - no conversation history is maintained.
    Every request starts fresh with no context from previous interactions.
    """
    global _cached_model
    
    # List of FREE-TIER models - try Flash first, then fallback to other free models
    # Free tier typically supports: gemini-1.5-flash, gemini-1.5-flash-8b, gemini-1.5-pro, gemini-pro-vision
    # Avoid: gemini-exp-*, gemini-2.0-*, gemini-2.5-* (these require billing)
    
    # Known free-tier models in priority order (Flash first for speed, then others as fallback)
    known_free_tier_flash = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-8b',
    ]
    
    known_free_tier_other = [
        'gemini-1.5-pro',
        'gemini-pro-vision',
    ]
    
    # Try to get available models, but use known free-tier models as base
    # Use cached model list if available to avoid repeated API calls
    global _cached_available_models
    try:
        if _cached_available_models is None:
            # Only try once - if it fails, cache empty list to avoid repeated failed calls
            try:
                _cached_available_models, _ = list_available_models()
                if not _cached_available_models:
                    _cached_available_models = []  # Cache empty list to prevent retries
            except:
                _cached_available_models = []  # Cache empty list on error to prevent retries
        available_models = _cached_available_models if _cached_available_models else []
        if available_models:
            # Filter to only free-tier models (exclude exp, 2.0, 2.5, preview which require billing)
            free_tier_models = [
                m for m in available_models 
                if not any(excluded in m.lower() for excluded in ['exp', '2.0', '2.5', 'pro-2', 'preview'])
                and any(allowed in m.lower() for allowed in ['flash', '1.5-pro', 'pro-vision'])
            ]
            
            if free_tier_models:
                # Prioritize flash models (faster and cheaper), then other free models
                flash_models = [m for m in free_tier_models if 'flash' in m.lower()]
                other_models = [m for m in free_tier_models if 'flash' not in m.lower()]
                
                # Build priority list: available flash first, then available others, then known fallbacks
                models_to_try = []
                if flash_models:
                    models_to_try.extend(flash_models[:2])  # Max 2 flash models
                if other_models:
                    models_to_try.extend(other_models[:2])  # Max 2 other models
                
                # Add known models as fallbacks if not already included
                for model in known_free_tier_flash + known_free_tier_other:
                    if model not in models_to_try:
                        models_to_try.append(model)
            else:
                # If filtering removed everything, use known models with flash first
                models_to_try = known_free_tier_flash + known_free_tier_other
        else:
            # Default to known free-tier models (flash first, then others)
            models_to_try = known_free_tier_flash + known_free_tier_other
    except:
        # Fallback to known free-tier models only (flash first, then others)
        models_to_try = known_free_tier_flash + known_free_tier_other
    
    # Remove duplicates while preserving order
    seen = set()
    models_to_try = [m for m in models_to_try if m not in seen and not seen.add(m)]
    
    # Use cached model if available, otherwise start with first model
    if _cached_model and _cached_model in models_to_try:
        start_index = models_to_try.index(_cached_model)
        models_to_try = [models_to_try[start_index]] + [m for m in models_to_try if m != models_to_try[start_index]]
    
    # Master prompt for visually impaired assistance
    # Optimized for clarity and conciseness
    analysis_prompt = f"You are helping a visually impaired person identify visual objects. Answer their question about what they can see in this image with one clear, simple sentence. Be direct and helpful. Question: {user_prompt}"

    # Optimize image - smaller and faster encoding
    max_size = (512, 512)
    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Fast base64 encoding with lower quality
    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=70, optimize=True)
    image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # Try each model ONE AT A TIME until one works
    # Try v1beta first (standard), only try v1 if v1beta fails
    api_versions = ['v1beta', 'v1']
    last_error = None
    
    for model_name in models_to_try:
        # Try each API version for this model
        model_succeeded = False
        for api_version in api_versions:
            try:
                url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
                
                # CRITICAL: Each request is completely independent - NO conversation history is maintained.
                # The contents array contains ONLY the current message (never previous messages).
                # This ensures each new prompt starts fresh with zero context from past interactions.
                # Each call creates a brand new payload dictionary - no state persists between calls.
                payload = {
                    "contents": [
                        {
                            "role": "user",  # Single-turn conversation - no history
                            "parts": [
                                {"text": analysis_prompt},
                                {
                                    "inline_data": {
                                        "mime_type": "image/jpeg",
                                        "data": image_base64
                                    }
                                }
                            ]
                        }
                        # NOTE: Only ONE message in contents array - no assistant responses, no history from previous calls
                    ],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 50,  # Increased to allow complete sentence
                        "topP": 0.8,
                    }
                }
                
                # Safety check: Verify we're not accidentally including history
                # (This is a safeguard - the structure above already ensures no history)
                if len(payload["contents"]) != 1:
                    raise ValueError("Payload must contain exactly one message - conversation history not allowed")
                
                headers = {"Content-Type": "application/json"}
                response = requests.post(url, json=payload, headers=headers, timeout=15)
            
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check for safety filters blocking the response
                    if 'promptFeedback' in result and result['promptFeedback'].get('blockReason'):
                        block_reason = result['promptFeedback']['blockReason']
                        last_error = f"Model {model_name} blocked by safety filter"
                        break  # Try next API version
                    
                    if 'candidates' in result and len(result['candidates']) > 0:
                        candidate = result['candidates'][0]
                        
                        # Check if candidate was blocked
                        if 'finishReason' in candidate and candidate['finishReason'] != 'STOP':
                            last_error = f"Model {model_name} finish reason: {candidate['finishReason']}"
                            break  # Try next API version
                        
                        if 'content' in candidate and 'parts' in candidate['content']:
                            parts = candidate['content']['parts']
                            if parts and len(parts) > 0:
                                # Look for text in any part
                                result_text = None
                                for part in parts:
                                    if 'text' in part:
                                        result_text = part['text'].strip()
                                        break
                                
                                if result_text:
                                    # SUCCESS - cache the working model and return immediately
                                    _cached_model = model_name
                                    
                                    # Return the response (should be one simple sentence as requested)
                                    # Clean up any extra whitespace
                                    result_text = result_text.strip()
                                    # Ensure it ends with punctuation if it doesn't already
                                    if result_text and not result_text.endswith(('.', '!', '?')):
                                        result_text += '.'
                                    return result_text
                                else:
                                    last_error = f"Model {model_name} returned no text"
                                    break  # Try next API version
                            else:
                                last_error = f"Model {model_name} returned empty parts"
                                break  # Try next API version
                        else:
                            last_error = f"Model {model_name} returned invalid structure"
                            break  # Try next API version
                    else:
                        last_error = f"Model {model_name} returned no candidates"
                        break  # Try next API version
                        
                elif response.status_code == 404:
                    # Model not found - try next API version
                    last_error = f"Model {model_name} not found"
                    break  # Try next API version
                    
                elif response.status_code == 400:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('error', {}).get('message', 'Bad request')
                    
                    # Check if it's a quota error - stop trying completely if so
                    error_lower = error_msg.lower()
                    if 'quota' in error_lower or 'exceeded' in error_lower or 'billing' in error_lower:
                        error_msg_full = f"Quota exceeded. Please check your Google Cloud billing or wait for quota reset."
                        print(f"\n⚠ Debug: {error_msg_full}", file=sys.stderr)
                        return f"Error: {error_msg_full}"
                    
                    last_error = f"Model {model_name}: {error_msg[:50]}"  # Truncate long errors
                    break  # Try next API version
                    
                elif response.status_code == 403:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('error', {}).get('message', 'Forbidden')
                    
                    # Check if it's a quota error (sometimes 403 is used for quota)
                    error_lower = error_msg.lower()
                    if 'quota' in error_lower or 'exceeded' in error_lower or 'billing' in error_lower:
                        error_msg_full = f"Quota exceeded. Please check your Google Cloud billing or wait for quota reset."
                        print(f"\n⚠ Debug: {error_msg_full}", file=sys.stderr)
                        return f"Error: {error_msg_full}"
                    
                    # Auth error - stop trying all models
                    error_msg_full = f"API Key error. Please check your API key in config.py"
                    print(f"\n⚠ Debug: {error_msg_full}", file=sys.stderr)
                    return f"Error: {error_msg_full}"
                    
                else:
                    # Other error - try next API version
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('error', {}).get('message', f'Status {response.status_code}')
                    
                    # Check if it's a quota error in any status code
                    error_lower = error_msg.lower()
                    if 'quota' in error_lower or 'exceeded' in error_lower or 'billing' in error_lower:
                        error_msg_full = f"Quota exceeded. Please check your Google Cloud billing or wait for quota reset."
                        print(f"\n⚠ Debug: {error_msg_full}", file=sys.stderr)
                        return f"Error: {error_msg_full}"
                    
                    last_error = f"Model {model_name}: {error_msg[:50]}"  # Truncate
                    break  # Try next API version
                
            except requests.exceptions.Timeout:
                last_error = f"Model {model_name} timeout"
                break  # Try next API version
            except requests.exceptions.RequestException as e:
                last_error = f"Model {model_name} network error"
                break  # Try next API version
            except Exception as e:
                last_error = f"Model {model_name} error"
                break  # Try next API version
        
        # If we get here, this model failed with all API versions
        # Continue to next model silently (no error returned yet)
        continue
    
    # If we get here, ALL models failed - return error (will be silent, not spoken)
    error_msg = "I couldn't analyze that image."
    if last_error:
        print(f"\n⚠ Debug: {last_error}", file=sys.stderr)
    # Return with error prefix so text_to_speech is skipped
    return f"Error: {error_msg}"

def is_error_message(text):
    """Check if the message is an error/debug message that shouldn't be spoken"""
    if not text:
        return True
    text_lower = text.lower()
    return (text.startswith("Error:") or 
            text.startswith("I couldn't") or 
            "debug:" in text_lower or
            "⚠" in text or
            "debug" in text_lower or
            "api key error" in text_lower or
            "couldn't analyze" in text_lower or
            "quota" in text_lower or
            "exceeded" in text_lower or
            "billing" in text_lower or
            "please check" in text_lower or
            "wait for quota" in text_lower or
            "google cloud" in text_lower)

def play_sound_file(filepath):
    """Play an MP3 sound file using pygame (if available)"""
    if play_audio_func != "pygame":
        return False  # Only pygame supports file playback in this codebase
    
    if not os.path.exists(filepath):
        return False  # File doesn't exist, silently skip
    
    try:
        # pygame is already imported and mixer initialized if play_audio_func == "pygame"
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        # Wait for playback to finish (non-blocking check)
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)
        return True
    except Exception:
        # Silently fail - don't interrupt the application if sound can't play
        return False

def text_to_speech(text):
    """Convert text to speech using ElevenLabs and play it - optimized for speed"""
    if not ELEVENLABS_AVAILABLE or elevenlabs_client is None:
        return False
    
    # Skip TTS for error/debug messages
    if is_error_message(text):
        return False
    
    try:
        # Use default voice ID directly (no lookup for speed)
        voice_id = "EXAVITQu4vr4xnSDxMaL"  # Bella voice - clear, natural female voice good for accessibility
        
        # Generate audio with fastest settings
        audio_generator = elevenlabs_client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_turbo_v2_5",  # Turbo model is fastest
            optimize_streaming_latency=4,  # Maximum speed optimization
        )
        
        # Convert generator to bytes
        audio_bytes = b"".join(audio_generator)
        
        # Play the audio immediately - no output for speed
        if play_audio_func == "pygame":
            import pygame
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            try:
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                # Wait for playback to finish (non-blocking check)
                while pygame.mixer.music.get_busy():
                    time.sleep(0.05)  # Shorter sleep for faster response
                os.unlink(tmp_path)
                return True
            except Exception:
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                return False
        elif play_audio_func:
            play_audio_func(audio_bytes)
            return True
        else:
            return False
    except Exception as e:
        return False

def listen_for_audio(recognizer, microphone, timeout=5):
    """Listen for audio input and return transcribed text - minimal output for speed"""
    if not AUDIO_AVAILABLE:
        return None
    try:
        with microphone as source:
            # Minimal ambient noise adjustment for speed
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
        
        # Recognize speech - no output for speed
        try:
            text = recognizer.recognize_google(audio)
            return text.lower()
        except Exception as e:
            return None
    except Exception as e:
        return None

def detect_wake_word(recognizer, microphone):
    """Continuously listen for wake word 'hey hats eye'"""
    if not AUDIO_AVAILABLE:
        return False
    
    # Lenient wake phrase variations - accept reasonable variations
    wake_keywords = {
        'hats': ['hats', 'hat', 'hat\'s', 'hot', 'hut', 'hart', 'heart', 'hard'],
        'eye': ['eye', 'i', 'ai', 'aye', 'sauce', 'saws', 'saw', 'so', 'sigh', 'sighs']
    }
    
    # Phonetically similar phrases - reasonable matching
    wake_phrases = [
        # Original variations
        'hey hats eye', 'hey hats i', 'hey hat eye', 'hey hat i',
        'hats eye', 'hat eye', 'hats i', 'hat i',
        # Phonetic variations that sound similar
        'hot sauce', 'hot saw', 'hat sauce', 'hat saw',
        'heart sauce', 'hard sauce', 'hot sighs', 'hat sighs',
        # Partial matches with context
        'hey hot', 'hey hat', 'hey heart', 'hey hard',
        # Common variations
        'hat seye', 'hats ai', 'hats aye', 'hats sauce',
        'hot eye', 'hot i', 'heart eye', 'hard eye'
    ]
    
    print("Listening for wake word\n")
    
    # Initialize microphone and adjust for ambient noise once (minimal for speed)
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)  # Minimal adjustment for speed
    
    while True:
        try:
            with microphone as source:
                # Passive listening: wait for any sound, then capture
                print("Listening...", end="\r", flush=True)
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
            
            try:
                text = recognizer.recognize_google(audio).lower().strip()
                
                # Check for exact phrase matches first
                for phrase in wake_phrases:
                    if phrase in text:
                        print("Wake word detected!\n")
                        # Play wake word sound if available
                        wake_sound_path = os.path.join("public", "wake_word_sound.mp3")
                        play_sound_file(wake_sound_path)
                        return True
                
                # LENIENT matching: look for hat/eye-like keywords in words (not substrings)
                words = text.split()
                text_lower = text.lower()
                
                # Check for keywords in actual words (not substrings) - reduces false positives
                has_hat = any(kw in word.lower() for word in words for kw in wake_keywords['hats'])
                has_eye = any(kw in word.lower() for word in words for kw in wake_keywords['eye'])
                
                # Require at least 2 words - avoid single word triggers
                if len(words) < 2:
                    continue
                
                # LENIENT: If both keywords are present in a 2-3 word phrase, accept it
                if 2 <= len(words) <= 3 and has_hat and has_eye:
                    print("Wake word detected!\n")
                    # Play wake word sound if available
                    wake_sound_path = os.path.join("public", "wake_word_sound.mp3")
                    play_sound_file(wake_sound_path)
                    return True
                
                # LENIENT: If text contains "hey" or "hi" + both hat/eye keywords (2-4 words)
                if len(words) <= 4 and ('hey' in text_lower or 'hi' in text_lower) and has_hat and has_eye:
                    print("Wake word detected!\n")
                    # Play wake word sound if available
                    wake_sound_path = os.path.join("public", "wake_word_sound.mp3")
                    play_sound_file(wake_sound_path)
                    return True
                
            except Exception as e:
                # Continue listening silently for speed
                continue
        except Exception as e:
            error_name = type(e).__name__
            if 'WaitTimeout' in error_name or 'Timeout' in error_name:
                # Timeout is fine, just continue listening
                continue
            # Other errors, continue listening silently
            continue
        except KeyboardInterrupt:
            return False

def main():
    """Main voice-centered interactive loop"""
    # Test API key by listing models ONCE and cache it
    global _cached_available_models
    print("Testing Gemini API connection...")
    _cached_available_models, _ = list_available_models()
    if _cached_available_models:
        print(f"✓ Connected! Found {len(_cached_available_models)} available model(s)")
    else:
        print("⚠ Warning: Could not connect to Gemini API. Continuing anyway...")
    
    # Check if audio is available
    if not AUDIO_AVAILABLE:
        print("=" * 60)
        print("🎩 HATSEYE - Vision Analyzer")
        print("=" * 60)
        print("\n⚠️  Voice features are not available (PyAudio not installed)")
        print("\nTo enable voice features on Windows:")
        print("  1. pip install pipwin")
        print("  2. pipwin install pyaudio")
        print("\nFalling back to text input mode...\n")
        print("=" * 60)
        print("Enter your prompt (or 'quit' to exit):")
        print()
        
        # Text input fallback
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                if not user_input:
                    continue
                image = capture_webcam_frame()
                if image is None:
                    continue
                print("\n🤖 Analyzing with AI...")
                result = analyze_image_with_gemini(image, user_input)
                print("\n" + "─" * 60)
                print("💬 Response:")
                print("─" * 60)
                print(result)
                print("─" * 60 + "\n")
                
                # Convert response to speech and play it (skips error messages automatically)
                text_to_speech(result)
                print()
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
        return
    
    # Initialize speech recognition
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    # Use cached model list from startup (don't call API again)
    print("=" * 60)
    print("🎩 HATSEYE - Voice Vision Analyzer")
    print("=" * 60)
    print("\nChecking available models...")
    if _cached_available_models:
        print(f"Found {len(_cached_available_models)} available model(s)")
        vision_models = [m for m in _cached_available_models if 'pro' in m.lower() or 'vision' in m.lower() or 'flash' in m.lower() or '1.5' in m or '2.0' in m or '2.5' in m]
        if vision_models:
            print(f"Vision-capable models: {', '.join(vision_models[:5])}")
        else:
            print("Will try standard vision model names...")
    else:
        print("Warning: Could not retrieve available models. Will try standard model names...")
    
    # Check ElevenLabs availability
    if ELEVENLABS_AVAILABLE:
        print("✓ ElevenLabs text-to-speech available - responses will be read aloud")
    else:
        print("⚠ ElevenLabs not available - responses will be text only")
        print("  Install with: pip install elevenlabs")
    
    print("\n" + "=" * 60)
    print("Voice Commands:")
    print("  Wake word: \"hey hats eye\"")
    print("  Then speak your question (e.g., \"what am I holding?\" or \"read the text\")")
    print("  Press Ctrl+C to exit")
    print("=" * 60)
    print()
    
    # Test microphone and show what it hears
    print("Testing microphone...")
    try:
        with microphone as source:
            print("Adjusting for ambient noise (1 second)...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✓ Microphone ready")
            
            # Optional: Test recognition with a short listen
            print("\nTest: Say something to test recognition (or wait 3 seconds)...")
            try:
                test_audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                test_text = recognizer.recognize_google(test_audio)
                print(f"✓ Test successful! Heard: \"{test_text}\"\n")
            except Exception:
                print("✓ Microphone is working (no test audio detected)\n")
    except Exception as e:
        print(f"✗ Microphone error: {e}")
        print("Falling back to text input mode...\n")
        # Fallback to text input
        while True:
            try:
                user_input = input("You (text): ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                if not user_input:
                    continue
                image = capture_webcam_frame()
                if image is None:
                    continue
                print("\nAnalyzing image...")
                result = analyze_image_with_gemini(image, user_input)
                print("\n" + result + "\n")
                
                # Convert response to speech and play it (skips error messages automatically)
                text_to_speech(result)
                print()
            except KeyboardInterrupt:
                break
        return
    
    # Main loop: wake word detection -> question listening -> analysis
    while True:
        try:
            # Wait for wake word
            if not detect_wake_word(recognizer, microphone):
                break  # KeyboardInterrupt
            
            # Wake word detected, now listen for question - minimal output
            question = listen_for_audio(recognizer, microphone, timeout=5)
            
            if question is None:
                continue  # Silently continue for speed
            
            if question in ['quit', 'exit', 'stop', 'goodbye']:
                print("\n👋 Goodbye!")
                break
            
            # Play question received sound if available
            question_sound_path = os.path.join("public", "question_received_sound.mp3")
            play_sound_file(question_sound_path)
            
            # Capture webcam frame - only once
            image = capture_webcam_frame()
            if image is None:
                continue
            
            # Analyze with Gemini - only one model runs at a time, tries next if fails
            result = analyze_image_with_gemini(image, question)
            
            # Convert response to speech immediately (voice is what matters, not text)
            # text_to_speech automatically skips error/debug messages - only called once
            text_to_speech(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}", file=sys.stderr)
            print()
            time.sleep(1)

if __name__ == "__main__":
    main()