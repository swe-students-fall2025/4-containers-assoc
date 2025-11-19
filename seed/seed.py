import json
import os
import time
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Load connection settings with safe defaults for Docker
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "holingo")

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
spells_col = db["spells"]
users_col = db["users"]

# Load JSON data
with open("spells.json", "r", encoding="utf-8") as f:
    spells = json.load(f)

with open("users.json", "r", encoding="utf-8") as f:
    users = json.load(f)

if isinstance(spells, list) and spells:
    if spells_col.count_documents({}) == 0:
        spells_col.insert_many(spells)
        print(f"✨ Seeded {len(spells)} spells into '{DB_NAME}.spells'!")
    else:
        print("✔ Spells collection already contains data — skipping seeding.")
else:
    print("⚠ spells.json does not appear to contain a list of spell docs.")

if isinstance(users, list) and users:
    if users_col.count_documents({}) == 0:
        users_col.insert_many(users)
        print(f"✨ Seeded {len(users)} users into '{DB_NAME}.users'!")
    else:
        print("✔ Users collection already contains data — skipping seeding.")
else:
    print("⚠ users.json does not appear to contain a list of user docs.")