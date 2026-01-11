#!/usr/bin/env python3
"""
Arduino Serial Communication Module for HATSEYE

This module handles communication between Arduino and Python/Flask
"""

import serial
import serial.tools.list_ports
import threading
import time
import json
import re

# Global variables
arduino_port = None
arduino_serial = None
arduino_lock = threading.Lock()
arduino_data = None
arduino_connected = False

def find_arduino_port():
    """
    Automatically find Arduino port
    Returns port name (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
    """
    # Common Arduino board identifiers
    arduino_keywords = ['arduino', 'ch340', 'ch341', 'cp210', 'ft232', 'usb serial']
    
    ports = serial.tools.list_ports.comports()
    for port in ports:
        port_description = port.description.lower()
        port_hwid = port.hwid.lower()
        
        # Check if port description or hardware ID contains Arduino keywords
        for keyword in arduino_keywords:
            if keyword in port_description or keyword in port_hwid:
                return port.device
    
    # If no Arduino found, return first available port (for testing)
    if ports:
        return ports[0].device
    
    return None

def connect_arduino(port=None, baudrate=9600):
    """
    Connect to Arduino
    Args:
        port: Serial port (e.g., 'COM3' on Windows). If None, auto-detect
        baudrate: Serial baud rate (9600 is standard)
    Returns:
        True if connected successfully, False otherwise
    """
    global arduino_serial, arduino_port, arduino_connected
    
    try:
        # Auto-detect port if not specified
        if port is None:
            port = find_arduino_port()
        
        if port is None:
            print("No Arduino port found")
            return False
        
        # Close existing connection if any
        disconnect_arduino()
        
        # Open serial connection
        arduino_serial = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        
        arduino_port = port
        arduino_connected = True
        print(f"Connected to Arduino on {port}")
        return True
        
    except Exception as e:
        print(f"Error connecting to Arduino: {e}")
        arduino_connected = False
        return False

def disconnect_arduino():
    """Close Arduino connection"""
    global arduino_serial, arduino_port, arduino_connected
    
    with arduino_lock:
        if arduino_serial is not None:
            try:
                arduino_serial.close()
            except:
                pass
            arduino_serial = None
        arduino_port = None
        arduino_connected = False

def read_arduino_data():
    """
    Read data from Arduino
    Returns:
        Dictionary with Arduino data, or None if no data available
    """
    global arduino_serial, arduino_data
    
    if not arduino_connected or arduino_serial is None:
        return None
    
    try:
        with arduino_lock:
            if arduino_serial.in_waiting > 0:
                # Read until we get a complete line (ending with \n)
                line = arduino_serial.readline().decode('utf-8', errors='ignore').strip()
                
                if line:
                    # Debug: print raw line (uncomment to debug)
                    # print(f"Arduino raw: {line[:100]}")  # Print first 100 chars
                    
                    # Try to parse as JSON
                    try:
                        data = json.loads(line)
                        arduino_data = data
                        return data
                    except json.JSONDecodeError as e:
                        # If JSON parsing fails, try key-value pairs
                        data = {}
                        pairs = re.findall(r'(\w+):\s*([^,}]+)', line)
                        for key, value in pairs:
                            try:
                                data[key] = int(value.strip())
                            except ValueError:
                                try:
                                    data[key] = float(value.strip())
                                except ValueError:
                                    data[key] = value.strip()
                        
                        if data:
                            arduino_data = data
                            return data
                        else:
                            # If parsing failed completely, log for debugging
                            # print(f"Failed to parse Arduino data: {line[:100]}")
                            pass
    except Exception as e:
        print(f"Error reading from Arduino: {e}")
        import traceback
        traceback.print_exc()
        # Don't disconnect on error - might be temporary
    
    return None

def send_to_arduino(command):
    """
    Send command to Arduino
    Args:
        command: String command to send
    Returns:
        True if sent successfully, False otherwise
    """
    global arduino_serial
    
    if not arduino_connected or arduino_serial is None:
        return False
    
    try:
        with arduino_lock:
            arduino_serial.write(f"{command}\n".encode('utf-8'))
            return True
    except Exception as e:
        print(f"Error sending to Arduino: {e}")
        disconnect_arduino()
        return False

def arduino_read_loop():
    """Background thread that continuously reads from Arduino"""
    global arduino_connected
    
    # Read buffer periodically to clear old data
    first_read = True
    while arduino_connected:
        try:
            # On first connection, flush any old data
            if first_read and arduino_serial:
                with arduino_lock:
                    if arduino_serial.in_waiting > 0:
                        arduino_serial.reset_input_buffer()  # Clear old data
                first_read = False
            
            data = read_arduino_data()
            if data:
                # Debug: print first successful read (comment out after debugging)
                # print(f"Arduino data received: {data}")
                pass
        except Exception as e:
            print(f"Error in arduino_read_loop: {e}")
        
        time.sleep(0.1)  # Read every 100ms

def get_latest_data():
    """Get the most recently read Arduino data"""
    return arduino_data

def is_connected():
    """Check if Arduino is connected"""
    return arduino_connected

# Initialize on import (optional - comment out if you want manual connection)
# connect_arduino()
