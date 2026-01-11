#!/usr/bin/env python3
"""
Minimalist Motor Monitor for HATSEYE
Continuously displays motor intensities from Arduino in plain text
"""

import requests
import time
import sys

API_URL = "http://localhost:5000/arduino/data"

def get_motor_data():
    """Fetch motor data from Flask API"""
    try:
        response = requests.get(API_URL, timeout=1)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException:
        return None

def format_motor_display(data):
    """Format motor data in minimalist plain text"""
    if not data:
        return "No data"
    
    # Handle JSON format: {"sensors": [{"id": 1, "distance": X, "intensity": Y}, ...]}
    if "sensors" in data and isinstance(data["sensors"], list):
        lines = []
        for sensor in data["sensors"]:
            motor_id = sensor.get("id", 0)
            intensity = sensor.get("intensity", 0)
            distance = sensor.get("distance", 0)
            lines.append(f"M{motor_id}: {intensity:3d} ({distance:3d}cm)")
        return "  ".join(lines)
    
    # Handle simple format: S1_int: 123, S2_int: 456, etc.
    motors = []
    for i in range(1, 5):
        intensity_key = f"S{i}_int"
        distance_key = f"S{i}_dist"
        if intensity_key in data:
            intensity = data.get(intensity_key, 0)
            distance = data.get(distance_key, 0)
            motors.append(f"M{i}: {intensity:3d} ({distance:3d}cm)")
    
    if motors:
        return "  ".join(motors)
    
    # Fallback: print all data
    return str(data)

def main():
    """Main monitor loop"""
    print("HATSEYE Motor Monitor")
    print("=" * 50)
    print("Format: M1: intensity (distance)  M2: intensity (distance)  ...")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    print()
    
    try:
        while True:
            data = get_motor_data()
            display = format_motor_display(data)
            
            # Clear line and print (for continuous update effect)
            print(f"\r{display}", end="", flush=True)
            
            time.sleep(0.1)  # Update every 100ms
            
    except KeyboardInterrupt:
        print("\n\nStopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
