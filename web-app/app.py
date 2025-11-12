"""Flask web application that allows user to check Harry Potter spell pronunciation."""

import os
from flask import Flask, render_template
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()  # loads .env from root directory

app = Flask(__name__)

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
spells_col = db["spells"]


def fetch_spells():
    """Return all spells from MongoDB without ObjectId fields."""
    return list(spells_col.find({}, {"_id": 0}))


@app.route("/")
def index():
    """Render the live recognition dashboard with a snapshot of stored spells."""
    spells = fetch_spells()
    return render_template("index.html", spells=spells)


@app.route("/spells")
def spells_view():
    """Render the spell compendium page."""
    spells = fetch_spells()
    return render_template("spells.html", spells=spells)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
