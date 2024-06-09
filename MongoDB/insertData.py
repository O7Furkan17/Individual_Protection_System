from datetime import datetime
import io

class DetectionData:
    def __init__(self, db_connection, collection_name):
        self.collection = db_connection.get_collection(collection_name)
        self.current_id = self.get_last_image_id() + 1

    def get_last_image_id(self):
        last_entry = self.collection.find_one(sort=[("image_id", -1)])
        if last_entry:
            return int(last_entry["image_id"])
        return 0

    def insert_detection(self, image_data, detections_list):
        # Convert PIL Image to bytes
        image_bytes = io.BytesIO()
        image_data.save(image_bytes, format='JPEG')
        image_bytes = image_bytes.getvalue()


        # Prepare data to be inserted
        data = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "image_id": str(self.current_id),
            "image_data": image_bytes,
            "detections_list": detections_list
        }

        # Insert data into the database
        result = self.collection.insert_one(data)
        self.current_id += 1
        return result.inserted_id


