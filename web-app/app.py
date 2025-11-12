"""Flask web application that allows user to check Harry Potter spell pronounciation."""

import os
from flask import Flask, render_template, abort
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient

load_dotenv()  # loads .env from root directory

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
db = client[DB_NAME]
spells_col = db["spells"]


def fetch_spells():
    """Return all spells from MongoDB without ObjectId fields."""
    return list(spells_col.find({}, {"_id": 0}))


@app.route("/spell/<spell_name>")
def spell_view(spell_name):
    """Display a specific spell by its name."""
    spell = spells_col.find_one({"spell": spell_name})
    if not spell:
        abort(404)
    return render_template("spellpage.html", spell=spell)




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
