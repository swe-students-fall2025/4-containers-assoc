from flask import Flask, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env from root directory

app = Flask(__name__)

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
spells_col = db["spells"]

@app.route("/")
def index():
    spells = list(spells_col.find({}, {"_id": 0}))
    return render_template("index.html", spells=spells)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)