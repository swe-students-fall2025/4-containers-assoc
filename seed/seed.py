import json
import os
import time
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Load connection settings with safe defaults for Docker
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
DB_NAME = os.getenv("DB_NAME", "harrypotter_spells")

print(f"🔌 Connecting to MongoDB at: {MONGO_URI}")

# Retry logic for MongoDB startup delay
client = None
for i in range(10):
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.server_info()  # Force a connection
        print("🍃 MongoDB connection established!")
        break
    except ServerSelectionTimeoutError:
        print(f"⏳ Mongo not ready, retrying... ({i+1}/10)")
        time.sleep(2)

if not client:
    raise RuntimeError("❌ Could not connect to MongoDB")

db = client[DB_NAME]
collection = db["spells"]

# Load JSON data
with open("spells.json", "r", encoding="utf-8") as f:
    spells = json.load(f)

if isinstance(spells, list) and spells:
    if collection.count_documents({}) == 0:
        collection.insert_many(spells)
        print(f"✨ Seeded {len(spells)} spells into '{DB_NAME}.spells'!")
    else:
        print("✔ Collection already contains data — skipping seeding.")
else:
    print("⚠ spells.json does not appear to contain a list of spell docs.")