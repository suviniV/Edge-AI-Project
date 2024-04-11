import cv2

def capturing_training_images():
    # Initialize the webcam
    camera = cv2.VideoCapture(0)  # 0 corresponds to the default webcam on most systems

    # Set resolution for the webcam (optional)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Check if the webcam is opened successfully
    if not camera.isOpened():
        print("Error: Couldn't open webcam")
        return

    # Capture and save 10 frames
    count = 0
    while True:
        ret, frame = camera.read()  # Read frame from webcam
        if not ret:
            print("Error: Couldn't read frame")
            break

        cv2.imwrite("frame%d.jpg" % count, frame)  # Save frame to a file

        count += 1
        resized_img = cv2.resize(frame, (1000, 700))
        cv2.imshow('Webcam', resized_img)  # Display frame
        if cv2.waitKey(10) & 0xFF == ord('q'):  # Press 'q' to quit
            break

        if count >= 300:
            break

    # Release the webcam and close OpenCV windows
    camera.release()
    cv2.destroyAllWindows()

# Call the function to capture images
capturing_training_images()
