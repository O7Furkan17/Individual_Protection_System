from datetime import datetime

class DetectionData:
    def __init__(self, db_connection, collection_name):
        self.collection = db_connection.get_collection(collection_name)
        self.current_id = self.get_last_image_id() + 1

    def get_last_image_id(self):
        last_entry = self.collection.find_one(sort=[("image_id", -1)])
        if last_entry:
            return int(last_entry["image_id"])
        return 0

    def insert_detection(self, image_url, detections_list):
        data = {
            "timestamp": datetime.now().isoformat(),
            "image_id": str(self.current_id),
            "image_url": image_url,
            "detections_list": detections_list
        }
        result = self.collection.insert_one(data)
        self.current_id += 1
        return result.inserted_id

