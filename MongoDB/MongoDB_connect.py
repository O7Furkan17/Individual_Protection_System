from pymongo import MongoClient

default_uri = 'mongodb://localhost:27017/'
default_dbName = 'DetectionDB'

class MongoDBConnection:
    def __init__(self, uri = default_uri, database_name = default_dbName):
        self.client = MongoClient(uri)
        self.db = self.client[database_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def close_connection(self):
        self.client.close()
