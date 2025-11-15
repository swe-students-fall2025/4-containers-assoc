"""Flask web application that allows user to check Harry Potter spell pronunciation."""

import os
import sys
from flask import Flask, render_template, abort, request, jsonify
from pymongo import MongoClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "machine-learning-client"))
from audio_store import AudioStore  # pylint: disable=wrong-import-position

app = Flask(__name__)

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
spells_col = db["spells"]

audio_store = AudioStore.from_env()


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


@app.route("/spells/<spell_name>")
def spell_view(spell_name):
    """Render detail view for a single spell."""
    spell = spells_col.find_one({"spell": spell_name}, {"_id": 0})
    if not spell:
        abort(404)
    return render_template("spellpage.html", spell=spell)


@app.route("/api/spells", methods=["GET"])
def get_spells():
    """Return all spells as JSON."""
    spells = fetch_spells()
    return jsonify(spells)


@app.route("/api/audio", methods=["POST"])
def upload_audio():
    """Receive audio file from frontend and store it."""
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        spell_name = request.form.get("spell", "Unknown")

        if audio_file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        file_id = audio_store.save_audio(
            audio_file.stream,
            spell=spell_name,
            filename=audio_file.filename,
            content_type=audio_file.content_type or "audio/webm",
        )

        return jsonify({"success": True, "file_id": str(file_id), "spell": spell_name}), 200

    except Exception as e:  # pylint: disable=broad-except
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
