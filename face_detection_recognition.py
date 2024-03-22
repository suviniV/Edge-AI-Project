import cv2
import os
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Face detection function using haar cascade model
def face_detection(test_img):
    # converting color image to grayscale image
    gray_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
    # Load haar classifier
    face_haar_cascade = cv2.CascadeClassifier('HaarCascade/haarcascade_frontalface_default.xml')
    # Multiscale used to return the rectangle
    faces = face_haar_cascade.detectMultiScale(gray_img, scaleFactor=1.32, minNeighbors=5)
    return faces, gray_img

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
