import cv2
import time
import threading

class Camera(threading.Thread):

    def run(self, *args, **kwargs):
        self.cap = cv2.VideoCapture(1)
        self.show = False
        self.a = 0
        self.b = 0
        self.record = 0
        self.frame_width = int(self.cap.get(3))
        self.frame_height = int(self.cap.get(4))
        self.recordflag = False

        while self.cap.isOpened():
            if self.show:
                ret, frame = self.cap.read()

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                h, s, v = cv2.split(hsv)

                s = s + self.a

                hsv = cv2.merge([h, s, v])
                frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                self.cap.set(cv2.CAP_PROP_EXPOSURE, self.b)
                cv2.imshow('Webcam', frame)

                if self.recordflag:
                    self.result.write(frame)
            else:
                self.cap.release()
                # Destroy all the windows
                cv2.destroyAllWindows()
                while not self.show:
                    time.sleep(1)
                    pass
                self.cap = cv2.VideoCapture(1)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # After the loop release the cap object
        self.cap.release()
        # Destroy all the windows
        cv2.destroyAllWindows()

    def saturation(self, value):
        self.a = value

    def exposure(self, value):
        self.b = value

    def startrecord(self, path):

        self.record = self.record + 1

        filename = (path + "\Arraycapture_" + str(self.record) + ".avi")
        print(filename)

        size = (self.frame_width, self.frame_height)

        self.result = cv2.VideoWriter(filename,
                                      cv2.VideoWriter_fourcc(*'MJPG'),
                                      20, size)
        self.recordflag = True
        print("Recording Started")

    def stoprecord(self):

        self.recordflag = False
        print("Recording Stopped")

    def close(self):
        self.show = False

    def open(self):
        self.show = True
