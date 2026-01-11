#!/usr/bin/env python3
"""
Web GUI for HATSEYE - Full functionality in browser
Run this file to start a web server, then open http://localhost:5000 in your browser
"""

from flask import Flask, render_template, Response, request, jsonify, send_file
import cv2
import threading
import time
import base64
import tempfile
import os
from PIL import Image
from io import BytesIO

# Import HATSEYE functionality
from webcam_gemini import (
    analyze_image_with_gemini,
    capture_webcam_frame,
    text_to_speech,
    is_error_message,
    play_sound_file,
    list_available_models,
    list_available_cameras,
    ELEVENLABS_AVAILABLE,
    _cached_available_models
)
from config import CAMERA_INDEX

app = Flask(__name__)

# Global variables for webcam
camera = None
camera_lock = threading.Lock()

def get_camera():
    """Get or create camera instance - uses configured camera index or auto-detects"""
    global camera
    
    if camera is None:
        # Try DirectShow backend first on Windows (more reliable)
        try:
            CAP_DSHOW = 700  # DirectShow backend constant
        except:
            CAP_DSHOW = cv2.CAP_ANY
        
        # Use configured camera index, or try camera indices in order if None
        if CAMERA_INDEX is not None:
            camera_indices = [CAMERA_INDEX]  # Use configured camera index
        else:
            camera_indices = [0, 1, 2]  # Auto-detect: try first 3 camera indices (0 is usually default)
        
        # Try different backends
        for backend in [CAP_DSHOW, cv2.CAP_ANY]:
            for camera_index in camera_indices:
                try:
                    cam = cv2.VideoCapture(camera_index, backend)
                    if cam.isOpened():
                        # Set reasonable resolution
                        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        camera = cam
                        return camera
                    else:
                        cam.release()
                except:
                    continue
    
    return camera

def release_camera():
    """Release camera resources"""
    global camera
    if camera is not None:
        camera.release()
        camera = None

def generate_frames():
    """Generate video frames from webcam"""
    cam = get_camera()
    if cam is None:
        # Return a black frame if camera is not available
        black_frame = b'\x00' * (640 * 480 * 3)
        while True:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + black_frame + b'\r\n')
        return
    
    while True:
        with camera_lock:
            success, frame = cam.read()
        
        if not success:
            # If frame read fails, try to reinitialize camera
            release_camera()
            cam = get_camera()
            if cam is None:
                break
            continue
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        
        # Yield frame in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze current webcam frame with Gemini API"""
    try:
        # Capture current frame
        image = capture_webcam_frame()
        if image is None:
            return jsonify({'error': 'Could not capture webcam frame'}), 500
        
        # Get question from request
        data = request.get_json()
        question = data.get('question', 'What is in this image?')
        
        # Analyze with Gemini
        result = analyze_image_with_gemini(image, question)
        
        # Check if it's an error message
        is_error = is_error_message(result)
        
        return jsonify({
            'result': result,
            'is_error': is_error
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tts', methods=['POST'])
def tts():
    """Generate text-to-speech audio"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        print(f"TTS request received for text: {text[:50]}...")
        
        if not text or is_error_message(text):
            print(f"TTS rejected: Invalid text or error message")
            return jsonify({'error': 'Invalid text for TTS'}), 400
        
        if not ELEVENLABS_AVAILABLE:
            print("TTS rejected: ElevenLabs not available")
            return jsonify({'error': 'ElevenLabs not available. Please check your API key in config.py'}), 503
        
        # Generate TTS audio
        from webcam_gemini import elevenlabs_client
        if elevenlabs_client is None:
            print("TTS rejected: ElevenLabs client is None")
            return jsonify({'error': 'ElevenLabs client not initialized'}), 503
        
        voice_id = "EXAVITQu4vr4xnSDxMaL"  # Bella voice
        print(f"Generating TTS with voice: {voice_id}")
        
        audio_generator = elevenlabs_client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_turbo_v2_5",
            optimize_streaming_latency=4,
        )
        
        # Convert generator to bytes
        print("Converting audio generator to bytes...")
        audio_bytes = b"".join(audio_generator)
        print(f"TTS audio generated: {len(audio_bytes)} bytes")
        
        if len(audio_bytes) == 0:
            print("TTS Error: Generated audio is empty")
            return jsonify({'error': 'Generated audio is empty'}), 500
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        print(f"TTS audio saved to: {tmp_path}")
        
        # Return audio file
        # Note: Flask will handle the file, but we'll clean up after a delay
        def delayed_cleanup():
            import threading
            def cleanup():
                time.sleep(5)  # Wait for download to complete
                try:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                        print(f"Cleaned up temp TTS file: {tmp_path}")
                except Exception as cleanup_error:
                    print(f"Error cleaning up temp file: {cleanup_error}")
            thread = threading.Thread(target=cleanup)
            thread.daemon = True
            thread.start()
        
        delayed_cleanup()
        
        return send_file(tmp_path, mimetype='audio/mpeg', as_attachment=False, download_name='response.mp3')
    except Exception as e:
        import traceback
        print(f"TTS Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Get system status"""
    return jsonify({
        'elevenlabs_available': ELEVENLABS_AVAILABLE,
        'camera_available': get_camera() is not None,
        'current_camera_index': CAMERA_INDEX
    })

@app.route('/cameras', methods=['GET'])
def list_cameras():
    """List available camera indices"""
    try:
        cameras = list_available_cameras()
        return jsonify({
            'cameras': cameras,
            'current_camera_index': CAMERA_INDEX
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/set_camera', methods=['POST'])
def set_camera():
    """Set camera index (requires restart to take effect)"""
    try:
        data = request.get_json()
        camera_index = data.get('camera_index')
        
        # Validate camera index
        if camera_index is not None:
            try:
                camera_index = int(camera_index)
                if camera_index < 0:
                    return jsonify({'error': 'Camera index must be non-negative'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid camera index'}), 400
        
        # Update config file
        config_path = os.path.join(os.path.dirname(__file__), 'config.py')
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        # Replace CAMERA_INDEX line
        import re
        if re.search(r'^CAMERA_INDEX\s*=', config_content, re.MULTILINE):
            # Replace existing line
            config_content = re.sub(
                r'^CAMERA_INDEX\s*=.*$',
                f'CAMERA_INDEX = {camera_index}' if camera_index is not None else 'CAMERA_INDEX = None',
                config_content,
                flags=re.MULTILINE
            )
        else:
            # Add new line
            config_content += f'\nCAMERA_INDEX = {camera_index if camera_index is not None else "None"}\n'
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        return jsonify({
            'success': True,
            'message': f'Camera index set to {camera_index}. Please restart the server for changes to take effect.',
            'camera_index': camera_index
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sound/<filename>')
def sound_file(filename):
    """Serve sound files from public folder"""
    sound_path = os.path.join('public', filename)
    if os.path.exists(sound_path):
        # Determine MIME type based on extension
        mimetype = 'audio/mpeg'
        if filename.endswith('.wav'):
            mimetype = 'audio/wav'
        elif filename.endswith('.ogg'):
            mimetype = 'audio/ogg'
        return send_file(sound_path, mimetype=mimetype)
    print(f"Sound file not found: {sound_path}")
    return jsonify({'error': 'Sound file not found'}), 404

if __name__ == '__main__':
    try:
        print("=" * 60)
        print("🎩 HATSEYE - Web GUI (Full Functionality)")
        print("=" * 60)
        print("\nStarting web server...")
        print("Open your browser and go to: http://localhost:5000")
        print("\nFeatures:")
        print("  - Webcam display")
        print("  - Voice recognition (browser Web Speech API)")
        print("  - Gemini AI image analysis")
        print("  - Text-to-speech responses")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 60)
        
        # Test camera access
        cam = get_camera()
        if cam is None:
            print("\n⚠️  Warning: Could not access webcam. The page will still load but video may not work.")
        else:
            print("✓ Webcam initialized successfully")
            # Release immediately, will reopen in generate_frames
            cam.release()
            camera = None
        
        # Test Gemini API connection
        print("\nTesting Gemini API connection...")
        try:
            available_models, _ = list_available_models()
            if available_models:
                print(f"✓ Connected! Found {len(available_models)} available model(s)")
            else:
                print("⚠ Warning: Could not connect to Gemini API. Continuing anyway...")
        except Exception as e:
            print(f"⚠ Warning: Could not test Gemini API: {e}")
        
        # Check ElevenLabs
        if ELEVENLABS_AVAILABLE:
            print("✓ ElevenLabs text-to-speech available")
        else:
            print("⚠ ElevenLabs not available - responses will be text only")
        
        print("\n" + "=" * 60)
        
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        release_camera()
        print("Goodbye!")
