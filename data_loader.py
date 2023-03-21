import pymongo
import json

# Load JSON data
with open('courses.json', 'r') as f:
    data = json.load(f)

# Connect to MongoDB
client = pymongo.MongoClient('localhost', 27017)
db = client['mydatabase']
collection = db['courses']

# Create index
collection.create_index([('name', pymongo.ASCENDING)])

# Insert data
result = collection.insert_many(data)

# Print result
print(f"{len(result.inserted_ids)} documents inserted.")