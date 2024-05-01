import cv2


class TestCamera:
    def __init__(self, width, height):
        self.video_capture = None
        self.size = (width, height)

    def connect(self):

        self.video_capture = cv2.VideoCapture(0)

        if not self.video_capture.isOpened():
            print("Video akışı başlatılamadı.")
            return False
        return True

    def disconnect(self):

        if self.video_capture is not None:
            self.video_capture.release()

    def get_frame(self):

        ret, frame = self.video_capture.read()
        if not ret:
            print("Video akışından çerçeve alınamadı.")
            return None
        frame = cv2.resize(frame, self.size)
        return frame

''' örnek kullanım :  

# Default camera bağlantısı
test_camera = TestCamera(640, 480)
connected = test_camera.connect()

if connected:
    while True:

        frame = ip_camera.get_frame()
        if frame is not None:

            # model_output = model.predict(frame)

            cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    ip_camera.disconnect()


cv2.destroyAllWindows()
'''