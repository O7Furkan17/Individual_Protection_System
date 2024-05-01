import cv2


class IPCamera:
    def __init__(self, ip_address, port, width=None, height=None):

        self.video_capture = None
        if width is None or height is None:
            self.size = None
        else:
            self.size = (width, height)

        self.ip_address = ip_address
        self.port = port
        self.video_capture = None

    def connect(self):

        url = f"https://{self.ip_address}:{self.port}/video"

        self.video_capture = cv2.VideoCapture(url)

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

# IP kamera bağlantısı
ip_camera = IPCamera(ip_address='192.168.1.100', port=8080, width=640, height=480)
connected = ip_camera.connect()

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
