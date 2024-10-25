import cv2


class TestCamera:
    def __init__(self, width=None, height=None):
        self.video_capture = None
        if width is None or height is None:
            self.size = None
        else:
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
        if self.size is not None:
            frame = cv2.resize(frame, self.size)

        return frame


''' 
örnek kullanım :  

# Default camera bağlantısı
test_camera = TestCamera()
connected = test_camera.connect()

if connected:
    while True:

        frame = test_camera.get_frame()
        if frame is not None:
            # model_output = model.predict(frame)

            cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    test_camera.disconnect()

cv2.destroyAllWindows()
'''
