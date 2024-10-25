from pymongo import MongoClient
from pymongo.server_api import ServerApi

#default_uri = 'mongodb://localhost:27017/'
default_uri = ''
default_dbName = 'IndividualProtectionSys'

class MongoDBConnection:
    def __init__(self, uri = default_uri, database_name = default_dbName):
        self.client = MongoClient(uri,server_api=ServerApi('1'))
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        self.db = self.client[database_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def close_connection(self):
        self.client.close()
