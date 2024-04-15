GPIO.setup(motion_pin, GPIO.IN)
GPIO.setup(ir_pin, GPIO.IN)

# Define the path to the Python files you want to run
lightsent_script = "lightsensor.py"
face_recognition_script = "alert.py"

# Flag to track if motion is detected
motion_detected = False

try:
    print("Motion and IR detection program started...")
    while True:
        # Check if motion is detected
        if GPIO.input(motion_pin) and not motion_detected:
            print("Motion detected!")
            motion_detected = True
            # Run lightsent.py
            subprocess.run(["python3", lightsent_script])
        # Check if motion is detected and IR is detected
        if motion_detected and GPIO.input(ir_pin):
            print("IR detected after motion!")
            # Run faceRecognition.py
            subprocess.run(["python3", face_recognition_script])
            # Reset motion detected flag
            motion_detected = False

        time.sleep(0.1)  # Adjust sleep time for desired polling frequency
except KeyboardInterrupt:
    print("Exiting...")
finally:
# Clean up GPIO