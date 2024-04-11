from Model import functions as func

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