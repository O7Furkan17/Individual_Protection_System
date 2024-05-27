from pymongo import MongoClient


# MongoDB bağlantısı
client = MongoClient('mongodb://localhost:27017/')
db = client['DetectionDB']

# Koleksiyon referansı
detections_collection = db['detections']

print(client.list_database_names())
print(db.list_collection_names())