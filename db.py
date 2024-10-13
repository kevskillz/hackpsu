from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# MongoDB connection URI
uri = "mongodb+srv://main:hackpsu24@hackpsu.kvd7j.mongodb.net/?retryWrites=true&w=majority&appName=HackPSU"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
print(client)
# Specify the database and collection
db = client['sample_mflix']  # Replace with your database name
print(db)
# print(db)
# collection = db['your_collection_name']  # Replace with your collection name

# # Create a document to insert
# document = {
#     'key1': 'value1',
#     'key2': 'value2',
#     # Add more key-value pairs as needed
# }

# # Insert the document into the collection
# result = collection.insert_one(document)

# # Print the result
# print(f'Document inserted with ID: {result.inserted_id}')
