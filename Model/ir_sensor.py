import RPi.GPIO as GPIO
import time

# Set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)

# Define GPIO pin connected to the output of the IR sensor
IR_PIN = 15

# Set up the GPIO pin as input
GPIO.setup(IR_PIN, GPIO.IN)

try:
    while True:
        # Read the state of the IR sensor
        if GPIO.input(IR_PIN) == GPIO.HIGH:
            print("IR sensor not detected something!")
        else:
            print("IR sensor detecting something.")
            break
        time.sleep(0.1)  # Adjust the delay as needed
except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on Ctrl+C exit