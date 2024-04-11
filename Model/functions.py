# Importing Necessary Libraries
import cv2
import os
import numpy as np
import smtplib
from picamera.array import PiRGBArray
from picamera import PiCamera
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from gpiozero import MotionSensor, LightSensor, LED
from signal import pause
import time
from gpiozero import LightSensor, LED
from signal import pause

# Define pin numbers
light_sensor_pin = 18  # GPIO pin for the light sensor
lED_pin = 17  # GPIO pin for the LED

# Initialize light sensor and LED
light_sensor = LightSensor(light_sensor_pin)
led = LED(lED_pin)


# Face detection function using haar cascade model
def face_detection(test_img):
    # converting color image to grayscale image
    gray_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
    # Load haar classifier
    face_haar_cascade = cv2.CascadeClassifier('HaarCascade/haarcascade_frontalface_default.xml')
    # Multiscale used to return the rectangle
    faces = face_haar_cascade.detectMultiScale(gray_img, scaleFactor=1.32, minNeighbors=5)
    return faces, gray_img


# Function to generate the labels for the training dataset which is passed as the parameter directory
# returns part of gray_img which is face along with its label/ID
def labels_for_training_data(directory):
    faces = []
    face_id = []

    for path, sub_dir_names, filenames in os.walk(directory):
        for filename in filenames:
            if filename.startswith("."):
                # Skipping files that start with .
                print("Skipping system file")
                continue
            id_no = os.path.basename(path)  # fetching subdirectory names
            img_path = os.path.join(path, filename)  # fetching image path
            print("img_path:", img_path)
            print("id:", id_no)
            test_img = cv2.imread(img_path)  # loading each image one by one
            # Handling if the image isn't loaded properly
            if test_img is None:
                print("Image not loaded properly")
                continue
            # Calling face_detection function to return faces detected in particular image
            faces_rect, gray_img = face_detection(
                test_img)
            # Handling of detecting multiple faces since we are only feeding single person images to the classifier
            if len(faces_rect) != 1:
                continue
            (x, y, w, h) = faces_rect[0]
            roi_gray = gray_img[y:y + w, x:x + h]  # cropping region of interest i.e. face area from grayscale image
            faces.append(roi_gray)
            face_id.append(int(id_no))
    return faces, face_id


# Function to train haar classifier and takes faces,faceID returned by previous function as its arguments
def train_classifier(faces, face_id):
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.train(faces, np.array(face_id))
    return face_recognizer


# Function to draw bounding boxes around detected face in image
def draw_rect(test_img, face):
    (x, y, w, h) = face
    cv2.rectangle(test_img, (x, y), (x + w, y + h), (255, 0, 0), thickness=5)


# Function writes name of person for detected label
def put_text(test_img, text, x, y):
    cv2.putText(test_img, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 4)


# Function to save the training images into a yml file
def save_training_images_to_yml(training_images_path, output_file_path):
    faces, face_id = labels_for_training_data(training_images_path)
    face_recognizer = train_classifier(faces, face_id)
    face_recognizer.write(output_file_path)


# Main function which calls the functions required for the facial_recognition
def main_function():
    # Load saved training data
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.read('trainingData.yml')

    name = {0: "Kavindya", 1: "Ashken", 2: "Abdul"}

    # Initializing the PiCamera
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.frame_rate = 32
    raw_capture = PiRGBArray(camera, size=(640, 480))
    time.sleep(0.1)
    # Loop to continuously capture frames from the camera
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        # Extract the captured frame as a numpy array
        test_img = frame.array
        # Detect faces in the captured frame
        faces_detected, gray_img = face_detection(test_img)
        # Draw rectangles around the detected faces
        for (x, y, w, h) in faces_detected:
            draw_rect(test_img, (x, y, w, h))
        # Loop through each detected face
        for face in faces_detected:
            # Extract the coordinates and dimensions of the detected face
            (x, y, w, h) = face
            # Extract the region of interest (ROI) in grayscale from the captured frame
            roi_gray = gray_img[y:y + w, x:x + h]
            label, confidence = face_recognizer.predict(roi_gray)  # predicting the label of given image
            print("confidence:", confidence)
            print("label:", label)
            draw_rect(test_img, face)
            predicted_name = name[label]
            if confidence < 39:  # If confidence less than 37 then don't print predicted face text on screen
                put_text(test_img, predicted_name, x, y)
            else:
                # Deviations: Handling unrecognized faces
                put_text(test_img, "Unknown", x, y)

        cv2.imshow('face recognition', test_img)
        raw_capture.truncate(0)
        # wait until 'q' key is pressed to terminate
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


def send_email_alert(image):
    # Email configuration
    sender_email = 'akhabeer02@gmail.com'
    sender_app_password = 'ulcw soap fxyi wyhz'
    receiver_email = 'kabeer.20210888@iit.ac.lk'
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'Unauthorized Access Detected'
    # Content for the Email
    body = 'An unauthorized person has been detected.'
    msg.attach(MIMEText(body, 'plain'))
    # Attach the captured image
    img_attachment = MIMEImage(image, name='intruder.jpg')
    msg.attach(img_attachment)
    # Establish a secure session with the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_app_password)
    # Send the email
    server.sendmail(sender_email, receiver_email, msg.as_string())
    # Close the SMTP server connection
    server.quit()

#
def is_dark():
    """
    Function to determine if it's dark based on light sensor reading.
    """
    return light_sensor.value < 0.5  # Invert the logic to represent darkness


def turn_on_led():
    led.on()


def turn_off_led():
    led.off()


# When light is detected, turn off the LED
light_sensor.when_dark = turn_on_led
light_sensor.when_light = turn_off_led

pause()  # Pause the script indefinitely to keep the program running


# Define pin numbers
motion_sensor_pin = 23  # GPIO pin for the motion sensor
light_sensor_pin = 18   # GPIO pin for the light sensor
led_pin = 17            # GPIO pin for the LED

# Initialize motion sensor, light sensor, and LED
motion_sensor = MotionSensor(motion_sensor_pin)
light_sensor = LightSensor(light_sensor_pin)
led = LED(led_pin)

# Function to determine if it's dark based on light sensor reading
def is_dark():
    return light_sensor.value < 0.5  # Invert the logic to represent darkness

# Function to turn on the LED
def turn_on_led():
    led.on()

# Function to turn off the LED
def turn_off_led():
    led.off()

# When motion is detected, check if it's dark and turn on the LED
motion_sensor.when_motion = lambda: turn_on_led() if is_dark() else None

# When motion stops, turn off the LED
motion_sensor.when_no_motion = turn_off_led

pause()  # Pause the script indefinitely to keep the program running
