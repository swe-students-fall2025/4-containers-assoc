"""Flask web application that allows user to check Harry Potter spell pronunciation."""

from itertools import product
import os
import sys
from bson import ObjectId
from flask import Flask, redirect, render_template, abort, request, jsonify, url_for
import requests
from pymongo import MongoClient
import tempfile

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..")
)
# from machine_learning_client.audio_store import AudioStore  # pylint: disable=wrong-import-position,import-error
# from machine_learning_client.pronun_assess import convert_to_wav, pronunciation_assessment  # pylint: disable=wrong-import-position,import-error
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL")

def create_app():
    app = Flask(__name__)

    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME")]
    spells_col = db["spells"]

    @app.route("/audio")
    def index():
        """Render the live recognition dashboard for a single selected spell."""
        spell_name = request.args.get("spell")

        current_spell = None
        if spell_name:
            current_spell = spells_col.find_one({"spell": spell_name}, {"_id": 0})

        return render_template("index.html", spell=current_spell)


    @app.route("/")
    def spells_view():
        """Render the spell compendium page."""
        query = request.args.get("q")
        # by type/ difficulty
        t = request.args.get("t")
        diff = request.args.get("p")
        spells = []
        filter_r = {}

        if query:
            filter_r = {
            "$or": [
                {"spell": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        }
            
        if t and t != "":
            filter_r["type"] = t
        if diff and diff != "":
            filter_r["difficulty"] = diff

        spells = list(spells_col.find(filter_r, {"_id": 0}))

        return render_template(
            "spells.html",
            spells=spells,
            query=query,
            type=t,
            difficulty=diff
        )


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
        spells = list(spells_col.find({}, {"_id": 0}))
        return jsonify(spells)


    @app.route("/api/audio", methods=["POST"])
    def upload_audio():
        """Receive audio file from frontend, forward to ml-client, return assessment result."""
        try:
            if "audio" not in request.files:
                return jsonify({"success": False, "error": "No audio file provided"}), 400

            audio_file = request.files["audio"]
            spell_name = request.form.get("spell") or "Unknown"

            files = {
                "audio": (audio_file.filename, audio_file.stream, audio_file.mimetype or "audio/webm")
            }
            data = {"spell": spell_name}

            # Send to ml-client container
            ml_resp = requests.post(
                ML_SERVICE_URL + "/assess",
                files=files,
                data=data,
                timeout=60,
            )

            try:
                ml_result = ml_resp.json()
            except ValueError:
                return jsonify({"success": False, "error": "Invalid response from ML service"}), 500

            # 🔹 Ensure spell is always present in the response
            ml_result["spell"] = spell_name

            # Always 200 here; "success" is in the JSON
            return jsonify(ml_result), 200

        except Exception as e:  # noqa: BLE001
            return jsonify({"success": False, "error": str(e)}), 500
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
