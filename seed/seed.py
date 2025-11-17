import json
import os
from pymongo import MongoClient
import time

# Wait for Mongo to be available
time.sleep(3)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["spells"]

with open("./spells.json") as f:
    data = json.load(f)

if collection.count_documents({}) == 0:
    collection.insert_many(data)
    print("✨ Seeded spells collection successfully.")
else:
    print("✔ Collection already has data — skipping seeding.")

