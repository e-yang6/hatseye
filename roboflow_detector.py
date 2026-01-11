#!/usr/bin/env python3
"""
HATSEYE - Roboflow Integration using Inference SDK
Uses Roboflow Inference SDK for reliable object detection
"""

import cv2
import numpy as np

try:
    from inference_sdk import InferenceHTTPClient
    INFERENCE_AVAILABLE = True
except ImportError:
    INFERENCE_AVAILABLE = False
    print("Warning: inference_sdk not available")

class RoboflowDetector:
    """Manages Roboflow Inference for object detection in web app"""
    
    def __init__(self, api_key="dyQPAMFEMQE8DzcdptsU", 
                 model_id="road-damage-lh70u-dk94k/1"):
        """
        Initialize Roboflow detector
        
        Args:
            api_key: Roboflow API key
            model_id: Model ID (format: project_id/version_id)
                     Default: "road-damage-lh70u-dk94k/1" - Your custom YOLO model for road damage detection
                     Alternative: "coco/3" for general object detection
        """
        if not INFERENCE_AVAILABLE:
            raise ImportError("inference_sdk not available")
            
        self.api_key = api_key
        self.model_id = model_id
        
        print(f"Initializing Roboflow with model: {model_id}")
        
        # Initialize the inference client
        self.client = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key=api_key
        )
        
    def annotate_frame(self, frame):
        """
        Send frame to Roboflow and draw bounding boxes
        
        Args:
            frame: OpenCV frame (BGR numpy array)
            
        Returns:
            Annotated frame with bounding boxes and detection data
        """
        try:
            # Convert frame to RGB (Roboflow expects RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run inference
            result = self.client.infer(frame_rgb, model_id=self.model_id)
            
            # Draw predictions on frame
            annotated_frame = self.draw_predictions(frame.copy(), result)
            return annotated_frame, result
                
        except Exception as e:
            print(f"Roboflow detection error: {e}")
            import traceback
            traceback.print_exc()
            return frame, None
    
    def draw_predictions(self, frame, result):
        """Draw bounding boxes and labels on frame"""
        if not result or 'predictions' not in result:
            return frame
        
        predictions = result['predictions']
        count = len(predictions)
        
        for pred in predictions:
            # Get bounding box coordinates
            x = int(pred['x'])
            y = int(pred['y'])
            width = int(pred['width'])
            height = int(pred['height'])
            
            x1 = int(x - width / 2)
            y1 = int(y - height / 2)
            x2 = int(x + width / 2)
            y2 = int(y + height / 2)
            
            # Get class and confidence
            class_name = pred.get('class', 'object')
            confidence = pred.get('confidence', 0)
            
            # Choose color based on class (green for now)
            color = (0, 255, 0)
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label background
            label = f"{class_name}: {confidence:.2f}"
            (label_w, label_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.rectangle(frame, (x1, y1 - label_h - 10), 
                         (x1 + label_w, y1), color, -1)
            
            # Draw label text
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Draw object count at top
        cv2.putText(frame, f"Objects Detected: {count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame
