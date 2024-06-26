# Importing Necessary Libraries
import csv
from datetime import datetime
from io import StringIO
import random
import cv2
import os

import gpiozero
import numpy as np
import smtplib
from picamera.array import PiRGBArray
from picamera import PiCamera
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import time
from azure.storage.blob import BlobServiceClient
import sys


# Face detection function using haar cascade model
def face_detection(test_img):
    """
        Detect faces in the input image using the Haar cascade classifier.

        :param test_img: A color image in BGR format.
        :return: A tuple containing detected faces as rectangles and the grayscale image used for detection.
                 - faces: An array of rectangles representing the detected faces in the format (x, y, w, h),
                          where (x, y) is the top-left corner of the rectangle, and (w, h) are its width and height.
                 - gray_img: The input image converted to grayscale.
    """
    try:
        # converting color image to grayscale image
        gray_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
        # Load haar classifier
        face_haar_cascade = cv2.CascadeClassifier('HaarCascade/haarcascade_frontalface_default.xml')
        # Multiscale used to return the rectangle
        faces = face_haar_cascade.detectMultiScale(gray_img, scaleFactor=1.32, minNeighbors=5)
        return faces, gray_img
    except Exception as e:
        print("Error in face detection:", e)
        return None, None


# Function to generate the labels for the training dataset which is passed as the parameter directory
# returns part of gray_img which is face along with its label/ID
def labels_for_training_data(directory):
    """
        Generate labels for the training dataset based on the directory structure.

        :param directory: The directory containing subdirectories, each representing a different person's images.
        :return: A tuple containing lists of cropped face images (regions of interest) and their corresponding labels/IDs.
                   - faces: A list of cropped face images (grayscale) extracted from the input images.
                   - face_id: A list of integer labels representing the IDs associated with each face image.
    """
    try:
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
    except Exception as e:
        print("Error in generating labels:", e)
        return None, None


# Function to train haar classifier and takes faces,faceID returned by previous function as its arguments
def train_classifier(faces, face_id):
    """
        Train a LBPH face recognizer using the provided faces and corresponding IDs.

        :param faces: A list of cropped face images (grayscale).
        :param face_id: A list of integer labels representing the IDs associated with each face image.
        :return: The trained LBPH face recognizer.
    """
    try:
        face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        face_recognizer.train(faces, np.array(face_id))
        return face_recognizer
    except Exception as e:
        print("Error occurred during training classifier:", e)


# Function to draw bounding boxes around detected face in image
def draw_rect(test_img, face):
    """
        Draw a rectangle around the detected face in the input image.

        :param test_img: The input image.
        :param face: A tuple representing the coordinates and dimensions of the detected face in the format (x, y, w, h),
                     where (x, y) is the top-left corner of the rectangle, and (w, h) are its width and height.
    """
    try:
        (x, y, w, h) = face
        cv2.rectangle(test_img, (x, y), (x + w, y + h), (255, 0, 0), thickness=5)
    except Exception as e:
        print("Error in drawing rectangle:", e)


# Function writes name of person for detected label
def put_text(test_img, text, x, y):
    """
         Write text on the input image at the specified coordinates.

         :param test_img: The input image.
         :param text: The text to be written on the image.
         :param x: The x-coordinate of the starting point of the text.
         :param y: The y-coordinate of the starting point of the text.
    """
    try:
        cv2.putText(test_img, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 4)
    except Exception as e:
        print("Error in putting text:", e)


# Function to save the trained model into a yml file
def images_to_yml_and_training(training_images_path, output_file_path):
    """
        Save the trained model into a YAML file.

        :param training_images_path: The path to the directory containing the training images.
        :param output_file_path: The path to save the output YAML file.
    """
    try:
        faces, face_id = labels_for_training_data(training_images_path)
        face_recognizer = train_classifier(faces, face_id)
        face_recognizer.write(output_file_path)
    except Exception as e:
        print("Error in saving training images to YAML:", e)


# Function to capture the images for training when adding a new user
def capturing_training_images():
    """
    Capture images for training when adding a new user.

    :return: None
    """
    try:
        camera = PiCamera()
        camera.resolution = (1280, 720)  # Set resolution to 1280x720 (720p)
        raw_capture = PiRGBArray(camera, size=(1280, 720))
        time.sleep(0.1)

        # Capture and save 10 frames
        count = 0
        for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
            test_img = frame.array
            cv2.imwrite("frame%d.jpg" % count, test_img)

            count += 1
            resized_img = cv2.resize(test_img, (1000, 700))
            cv2.imshow('face detection Tutorial ', resized_img)
            cv2.waitKey(10)

            raw_capture.truncate(0)

            if count >= 300:
                break

        cv2.destroyAllWindows()
    except Exception as e:
        print("Error in capturing training images:", e)


# Function to download new user from azure containers
def download_images_from_azure_storage(local_folder_path, container_name):
    """
    Downloading the new user data from azure cloud to train the model again

    :param local_folder_path: The local folder path where the images will be downloaded
    :param container_name: The name of the Azure storage container
    """
    account_name = "smartlocktrainingimages"
    account_key = "kwpvrBsa5FRw9z95H4O2Ov0fyWQBgdig/S8+I4YZIY8iChizBeHvX0SS2C4wqbr6CpHR96uU7ypu+AStV7xGUg=="

    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net/",
                                            credential=account_key)

    # Get a container client
    container_client = blob_service_client.get_container_client(container=container_name)
    # List blobs in the container
    blob_list = container_client.list_blobs()

    # Create the local folder if it doesn't exist
    if not os.path.exists(local_folder_path):
        os.makedirs(local_folder_path)

    # Download each blob (image) to the local folder
    for blob in blob_list:
        blob_client = container_client.get_blob_client(blob.name)
        local_file_path = os.path.join(local_folder_path, blob.name)
        with open(local_file_path, "wb") as local_file:
            blob_data = blob_client.download_blob()
            local_file.write(blob_data.readall())


# Function to send email alert when intruder is detected
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


# Function to upload the image of the intruder to the cloud
def upload_unknown_image(image, counter):
    """
    Upload the intruder image to Azure Blob Storage.

    :param image: The image to upload.
    :param counter: The counter value used in the image filename.
    :return: None
    """
    # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(
        "DefaultEndpointsProtocol=https;AccountName=databasecw;AccountKey="
        "tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ==;EndpointSuffix="
        "core.windows.net")

    # Get the container client
    container_client = blob_service_client.get_container_client("unauthorizedaccesspics")

    # Upload the image
    blob_client = container_client.get_blob_client(f"Id{counter}.jpg")
    blob_client.upload_blob(image, overwrite=True)


# Function to upload the log of the intruder to the cloud
def write_unauthorized_access(Id, date):
    """
    Writes unauthorized access logs to a CSV file in Azure Blob Storage.

    :param Id: The ID of the intruder.
    :param date: The timestamp of the unauthorized access event.
    :return: None
    """

    unauthorized_access_logs = []

    # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(
        "DefaultEndpointsProtocol=https;AccountName=databasecw;AccountKey"
        "=tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ==;EndpointSuffix"
        "=core.windows.net")

    # Get the container client
    container_client = blob_service_client.get_container_client("unauthorizedaccesslogs")
    blob_client = container_client.get_blob_client("unauthorizedAccess.csv")
    blob_data = blob_client.download_blob()
    csv_content = blob_data.content_as_text()

    # Read existing logs
    reader = csv.DictReader(csv_content.splitlines())
    for row in reader:
        unauthorized_access_logs.append(row)

    # Append new log with given Id and date
    new_log = {'id': f"Id{Id}", 'time': date.strftime('%Y-%m-%d %H:%M:%S')}
    unauthorized_access_logs.append(new_log)

    # Convert logs to CSV format
    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=['id', 'time'])
    writer.writeheader()
    writer.writerows(unauthorized_access_logs)
    csv_content_updated = csv_buffer.getvalue()

    # Upload updated logs back to the cloud
    blob_client.upload_blob(csv_content_updated, overwrite=True)


# Function to upload the access logs to the cloud
def write_access_logs(name, date):
    """
    Writes access logs to a CSV file in Azure Blob Storage.

    :param name: The name of the user who accessed.
    :param date: The timestamp of the access event.
    :return: None
    """

    unauthorized_access_logs = []

    # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(
        "DefaultEndpointsProtocol=https;AccountName=databasecw;AccountKey"
        "=tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ==;EndpointSuffix"
        "=core.windows.net")

    container_client = blob_service_client.get_container_client("accesslogs")
    blob_client = container_client.get_blob_client("accessLogs.csv")
    blob_data = blob_client.download_blob()
    csv_content = blob_data.content_as_text()

    # Read existing logs
    reader = csv.DictReader(csv_content.splitlines())
    for row in reader:
        unauthorized_access_logs.append(row)

    # Append new log with given Id and date
    new_log = {'name': name, 'time': date.strftime('%Y-%m-%d %H:%M:%S')}
    unauthorized_access_logs.append(new_log)

    # Convert logs to CSV format
    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=['name', 'time'])
    writer.writeheader()
    writer.writerows(unauthorized_access_logs)
    csv_content_updated = csv_buffer.getvalue()

    # Upload updated logs back to the cloud
    blob_client.upload_blob(csv_content_updated, overwrite=True)


# Function to update the door lock status
def door_status_action(new_status):
    """
    Updates the door status in a CSV file stored in Azure Blob Storage.

    :param new_status: The new status of the door ("locked" or "unlocked").
    :return: None
    """

    # Azure Blob Storage connection string
    connection_string = "DefaultEndpointsProtocol=https;AccountName=databasecw;AccountKey=" \
                        "tor4V06NY6XHesq2z9vAZ55l3IWWTv9JpL1KT9S4CahV+e2+b9eh4nMy+cZlnpc6EW1WsYHh489/+AStZimtVQ==" \
                        ";EndpointSuffix=core.windows.net"

    # Connect to Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Prepare CSV content with new status
    csv_content_updated = f"{new_status}\n"

    # Upload updated status back to the cloud
    container_client = blob_service_client.get_container_client("doorlockstatus")
    blob_client = container_client.get_blob_client("doorStatus.csv")
    blob_client.upload_blob(csv_content_updated, overwrite=True)

    # Schedule updating status to "locked" after 30 seconds
    if new_status == "unlocked":
        time.sleep(30)
        door_status_action(new_status="locked")

led = gpiozero.LED(17)
stat = False

def LED():

    global  stat
    led.on()
    led_status = True

def LED_OFF():

    global stat
    led.on()
    led_status = False

# Main function which calls the functions required for the facial_recognition
def main_function():
    """
        Main function for facial recognition.

        :return: None
    """
    try:
        LED()
        print("LED Turned on")
        # Load saved trained model
        face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        face_recognizer.read('trainingImages.yml')

        name = {0: "Suvini Viduneth", 1: "Abdul Khabeer"}

        # Initializing the PiCamera
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 32
        raw_capture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.1)

        unknown_detected = False
        unknown_start_time = None

        start_time = time.time()
        # Loop to continuously capture frames from the camera
        for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
            # Extract the captured frame as a numpy array
            test_img = frame.array
            # Detect faces in the captured frame
            faces_detected, gray_img = face_detection(test_img)
            # Draw rectangles around the detected faces
            for (x, y, w, h) in faces_detected:
                draw_rect(test_img, (x, y, w, h))

            unknown_face_detected = False
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
                if confidence < 39:  # If confidence less than 39 then don't print predicted face text on screen
                    put_text(test_img, predicted_name, x, y)
                    if time.time() - start_time > 12:
                        write_access_logs(name=predicted_name, date=datetime.now())
                        door_status_action(new_status="unlocked")
                        sys.exit(0)
                        LED_OFF()
                else:
                    # Deviations: Handling unrecognized faces
                    put_text(test_img, "Unknown", x, y)
                    unknown_face_detected = True

            if unknown_face_detected:
                if not unknown_detected:
                    unknown_start_time = time.time()
                    unknown_detected = True
                elif time.time() - unknown_start_time > 20:
                    # Sending email alert for unauthorized access
                    send_email_alert(cv2.imencode('.jpg', test_img)[1].tobytes())
                    # Updating the cloud database
                    Id = random.randint(100000, 999999)
                    upload_unknown_image(cv2.imencode('.jpg', test_img)[1].tobytes(), Id)
                    write_unauthorized_access(Id=Id, date=datetime.now())
                    LED_OFF()
                    break  # Terminate the program
            else:
                unknown_detected = False

            cv2.imshow('face recognition', test_img)
            raw_capture.truncate(0)
            # wait until 'q' key is pressed to terminate
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
    except Exception as e:
        print("Error in main function:", e)


# Calling the main function
main_function()
