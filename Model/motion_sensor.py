"""
This script was done while testing the motion sensor individually
"""

import RPi.GPIO as GPIO
import time
import subprocess

# Set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)

# Set up GPIO pin for motion sensor
motion_pin = 26
GPIO.setup(motion_pin, GPIO.IN)

# Define the path to the Python file you want to run on motion detection
file_to_run = "Model/functions.py"

try:
    print("Motion detection program started...")
    while True:
        # Check if motion is detected
        if GPIO.input(motion_pin):
            print("Motion detected!")
            # Run the other Python file
            subprocess.run(["python3", file_to_run])
            time.sleep(1)  # Adjust sleep time as needed to avoid rapid multiple detections
        else:
            print("No motion detected")
            time.sleep(0.1)  # Adjust sleep time for desired polling frequency
except KeyboardInterrupt:
    print("Exiting...")
finally:
    # Clean up GPIO
    GPIO.cleanup()