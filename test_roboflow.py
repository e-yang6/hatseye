#!/usr/bin/env python3
"""
Test Roboflow detection to debug issues
"""

import cv2
import numpy as np
from roboflow_detector import RoboflowDetector

def test_roboflow():
    """Test Roboflow detection with a sample frame"""
    print("Initializing Roboflow detector with YOUR custom YOLO model...")

    # Use your custom model by default
    detector = RoboflowDetector()

    # Capture a real webcam frame for testing
    print("Capturing webcam frame...")
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Could not capture webcam frame, using test frame...")
        # Create a test frame (640x480 with some colored shapes)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(frame, (100, 100), (200, 200), (255, 0, 0), -1)
        cv2.circle(frame, (400, 300), 50, (0, 255, 0), -1)

    print("Sending frame to Roboflow...")
    annotated_frame, predictions = detector.annotate_frame(frame)

    if predictions:
        print(f"✓ Predictions received!")
        print(f"Number of objects: {len(predictions.get('predictions', []))}")

        # Print details of detected objects
        for pred in predictions.get('predictions', []):
            print(f"  - {pred.get('class')}: {pred.get('confidence'):.2f}")

        # Save the annotated frame
        cv2.imwrite('test_roboflow_output.jpg', annotated_frame)
        print("Saved annotated frame to test_roboflow_output.jpg")
    else:
        print("✗ No predictions received")
        print("This could mean:")
        print("  1. API key is invalid")
        print("  2. Model/workspace name is incorrect")
        print("  3. Network issue")
        print("  4. Model doesn't detect anything in the test frame")

if __name__ == "__main__":
    test_roboflow()
