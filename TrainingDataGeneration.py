import cv2
# Capturing Images for training data
cap = cv2.VideoCapture(0)

count = 0
while count < 500:
    ret, test_img = cap.read()
    if not ret:
        continue
    cv2.imwrite("frame%d.jpg" % count, test_img)
    count += 1
    resized_img = cv2.resize(test_img, (1000, 700))
    cv2.imshow('face detection Tutorial ', resized_img)
    cv2.waitKey(10)

cap.release()
cv2.destroyAllWindows()