'''
import cv2
import torch

class YOLOv8Detector:
    def __init__(self, model):
        self.model = model

    def detect_objects(self, frame):
        results = self.model(frame)
        return results

def main():
    # connect to MongoDB
    db_connection = MongoDBConnection(uri='mongodb://localhost:27017/', database_name='DetectionDB')
    detection_data = DetectionData(db_connection=db_connection, collection_name='detections')

    # load model
    model = torch.hub.load('ultralytics/yolov8', 'custom', path='path_to_your_model.pt')
    detector = YOLOv8Detector(model)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # detection
        results = detector.detect_objects(frame)

        # store detections
        detections_list = []
        contains_dangerous_object = False
        for result in results.xyxy[0]:
            class_name = model.names[int(result[5])]
            detections_list.append({
                "object_id": str(result[4].item()),  # Confidence as unique ID
                "class": class_name,
                "confidence": result[4].item()
            })
            if class_name in ["Shotgun", "Handgun", "Knife", "Weapon"]:
                contains_dangerous_object = True

        if contains_dangerous_object: # if there are detections
            # Example image_url
            image_url = "http://example.com/path/to/image.jpg"  # this might be local image path
            detection_data.insert_detection(image_url, detections_list)

        time.sleep(0.1) # 10 fps

    # release sources
    cap.release()
    cv2.destroyAllWindows()
    db_connection.close_connection()

if __name__ == "__main__":
    main()
'''
