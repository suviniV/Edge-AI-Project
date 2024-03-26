import cv2
import os
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import RPi.GPIO as GPIO
import time

# Define pin numbers
light_sensor_pin = 18  # GPIO pin for the light sensor
led_pin = 17  # GPIO pin for the LED

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(light_sensor_pin, GPIO.IN)
GPIO.setup(led_pin, GPIO.OUT)


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
    faceID = []

    for path, subdirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.startswith("."):
                # Skipping files that start with .
                print("Skipping system file")
                continue
            id = os.path.basename(path)  # fetching subdirectory names
            img_path = os.path.join(path, filename)  # fetching image path
            print("img_path:", img_path)
            print("id:", id)
            test_img = cv2.imread(img_path)  # loading each image one by one
            if test_img is None:
                print("Image not loaded properly")
                continue
            faces_rect, gray_img = face_detection(
                test_img)  # Calling faceDetection function to return faces detected in particular image
            if len(faces_rect) != 1:
                continue  # Since we are assuming only single person images are being fed to classifier
            (x, y, w, h) = faces_rect[0]
            roi_gray = gray_img[y:y + w, x:x + h]  # cropping region of interest i.e. face area from grayscale image
            faces.append(roi_gray)
            faceID.append(int(id))
    return faces, faceID


# Function to train haar classifier and takes faces,faceID returned by previous function as its arguments
def train_classifier(faces, faceID):
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.train(faces, np.array(faceID))
    return face_recognizer


# Function to draw bounding boxes around detected face in image
def draw_rect(test_img, face):
    (x, y, w, h) = face
    cv2.rectangle(test_img, (x, y), (x + w, y + h), (255, 0, 0), thickness=5)


# Function writes name of person for detected label
def put_text(test_img, text, x, y):
    cv2.putText(test_img, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 4)


# Function to save the training images into a yml file
def train_and_save_classifier(training_images_path, output_file_path):
    faces, faceID = labels_for_training_data(training_images_path)
    face_recognizer = train_classifier(faces, faceID)
    face_recognizer.write(output_file_path)


def send_email_alert(image):
    # Email configuration
    sender_email = 'akhabeer02@gmail.com'
    sender_app_password = 'ulcw soap fxyi wyhz'
    receiver_email = 'sheffa58@gmail.com'
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


def light_Sensor():
    """
    Function to determine if it's dark based on light sensor reading.
    Adjust the threshold value according to ambient light conditions.
    """
    light_value = GPIO.input(light_sensor_pin)
    return light_value == GPIO.LOW


try:
    while True:
        if light_Sensor():
            GPIO.output(led_pin, GPIO.HIGH)  # Turn on the LED
        else:
            GPIO.output(led_pin, GPIO.LOW)  # Turn off the LED
        time.sleep(0.1)  # Delay for stability

except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on Ctrl+C exit
