import cv2
import multiprocessing
from matplotlib import pyplot as plt

def camera1():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()

        #show Image
        cv2.imshow('Webcam', frame)

        # checks whether q has been hit and stops the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def camera2():
    cap = cv2.VideoCapture(1)
    while cap.isOpened():
        ret, frame = cap.read()

        #show Image
        cv2.imshow('Webcam', frame)

        # checks whether q has been hit and stops the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == '__main__':
    p1 = multiprocessing.Process(target=camera1)
    p2 = multiprocessing.Process(target=camera2)

    p1.start()
    p2.start()