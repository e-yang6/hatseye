#!/usr/bin/env python3
"""
HATSEYE - Roboflow HTTP Integration
Uses Roboflow HTTP API for web app camera integration
"""

import cv2
import base64
import requests
import numpy as np

class RoboflowHTTPDetector:
    """Manages Roboflow HTTP API inference for object detection in web app"""

    def __init__(self, api_key="dyQPAMFEMQE8DzcdptsU",
                 workspace="productivity-ki6ig",
                 model="detect-count-and-visualize-7",
                 is_workflow=True):
        """
        Initialize Roboflow HTTP detector

        Args:
            api_key: Roboflow API key
            workspace: Workspace name
            model: Model/workflow name
            is_workflow: True if using a workflow, False if using a model
        """
        self.api_key = api_key
        self.workspace = workspace
        self.model = model
        self.is_workflow = is_workflow

        # Use different base URL for workflows vs models
        if is_workflow:
            self.base_url = f"https://detect.roboflow.com/{workspace}/{model}"
        else:
            self.base_url = "https://detect.roboflow.com"

    def annotate_frame(self, frame):
        """
        Send frame to Roboflow and draw bounding boxes

        Args:
            frame: OpenCV frame (BGR numpy array)

        Returns:
            Annotated frame with bounding boxes and detection data
        """
        try:
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            img_bytes = buffer.tobytes()

            # Prepare request based on type (workflow vs model)
            if self.is_workflow:
                # For workflows, send base64 encoded image in JSON body
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                url = f"{self.base_url}"
                params = {"api_key": self.api_key}

                response = requests.post(
                    url,
                    params=params,
                    json={
                        "image": {
                            "type": "base64",
                            "value": img_base64
                        }
                    },
                    timeout=5
                )
            else:
                # For models, send as multipart file
                url = f"{self.base_url}/{self.workspace}/{self.model}/1"
                params = {
                    "api_key": self.api_key,
                    "confidence": 25,
                    "overlap": 30,
                }

                response = requests.post(
                    url,
                    params=params,
                    files={"file": img_bytes},
                    timeout=5
                )

            print(f"Roboflow API response status: {response.status_code}")
            print(f"Roboflow API URL: {url}")

            if response.status_code == 200:
                predictions = response.json()
                print(f"Roboflow predictions: {predictions}")
                annotated_frame = self.draw_predictions(frame.copy(), predictions)
                return annotated_frame, predictions
            else:
                print(f"Roboflow API error: {response.text}")
                return frame, None

        except Exception as e:
            print(f"Roboflow detection error: {e}")
            return frame, None

    def draw_predictions(self, frame, predictions):
        """Draw bounding boxes and labels on frame"""
        if not predictions or 'predictions' not in predictions:
            return frame

        count = len(predictions['predictions'])

        for pred in predictions['predictions']:
            x = int(pred['x'])
            y = int(pred['y'])
            width = int(pred['width'])
            height = int(pred['height'])

            x1 = int(x - width / 2)
            y1 = int(y - height / 2)
            x2 = int(x + width / 2)
            y2 = int(y + height / 2)

            class_name = pred['class']
            confidence = pred['confidence']

            color = (0, 255, 0)  # Green

            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            (label_w, label_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.rectangle(frame, (x1, y1 - label_h - 10),
                         (x1 + label_w, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # Draw count
        cv2.putText(frame, f"Objects: {count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return frame
