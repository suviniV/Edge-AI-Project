from picamera import PiCamera
from gpiozero import MotionSensor, LightSensor
import time
import requests

# use random values from 0 - 1
import random
# Initialize sensors and camera
motion_sensor = MotionSensor(4)
light_sensor = LightSensor(17)
camera = PiCamera()


# Function to upload image to Azure
def upload_to_azure(image):
    # Code to upload image to Azure Blob Storage
    # Azure endpoint URL to be placed
    url = 'https://xxxxxx'
    files = {'file': open(image, 'rb')}
    response = requests.post(url, files=files)
    print(response.text)  # Print response from Azure


while True:
    motion_sensor.wait_for_motion()
    print("Motion detected")
    # Hard coding for testing
    random_value = random.random()
    print(random_value)
    light_intensity = random_value
    if light_intensity < 0.5:  # Adjust threshold as needed
        # Code to turn on the light
        print("Low light detected. Turning on the light.")
    else:
        print("Sufficient light. Proceeding without turning on the light.")

    # Capture image
    image_path = '/home/pi/image.jpg'  # Adjust path as needed
    camera.capture(image_path)
    print("Image captured")

    # Upload image to Azure
    upload_to_azure(image_path)

    time.sleep(1)  # Adjust delay as needed
