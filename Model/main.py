from Model import functions as func
import RPi.GPIO as GPIO
import time
face_recognizer = func.main_function()

# Define pin numbers
motion_sensor_pin = 23  # GPIO pin for the motion sensor

# Initialize motion sensor, light sensor, and LED
motion_sensor = MotionSensor(motion_sensor_pin)

# When motion is detected, check if it's dark and turn on the LED
motion_sensor.when_motion = lambda: turn_on_led() if is_dark() else None

# When motion stops, turn off the LED
motion_sensor.when_no_motion = turn_off_led

pause()  # Pause the script indefinitely to keep the program running



# IR Sensor
# Set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
# Define GPIO pin connected to the output of the IR sensor
IR_PIN = 17
# Set up the GPIO pin as input
GPIO.setup(IR_PIN, GPIO.IN)
try:
    while True:
        # Read the state of the IR sensor
        if GPIO.input(IR_PIN) == GPIO.HIGH:
            print("IR sensor detected something!")
        else:
            print("IR sensor not detecting anything.")
        time.sleep(0.1)  # Adjust the delay as needed
except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on Ctrl+C exit