import cv2
import os
import numpy as np


# Face detection function using haar cascade model
def face_detection(test_img):
    # converting color image to grayscale image
    gray_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
    # Load haar classifier
    face_haar_cascade = cv2.CascadeClassifier('HaarCascade/haarcascade_frontalface_default.xml')
    # Multiscale used to return the rectangle
    faces = face_haar_cascade.detectMultiScale(gray_img, scaleFactor=1.32, minNeighbors=5)
    return faces, gray_img
