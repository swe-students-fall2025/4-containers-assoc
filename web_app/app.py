"""Flask web application that allows user to check Harry Potter spell pronunciation."""

from itertools import product
import os
import sys
from bson import ObjectId
from flask import Flask, redirect, render_template, abort, request, jsonify, url_for
from pymongo import MongoClient
import tempfile

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..")
)
from machine_learning_client.audio_store import AudioStore  # pylint: disable=wrong-import-position,import-error
from machine_learning_client.pronun_assess import convert_to_wav, pronunciation_assessment  # pylint: disable=wrong-import-position,import-error

def create_app():
    app = Flask(__name__)

    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME")]
    spells_col = db["spells"]

    audio_store = AudioStore.from_env()

    @app.route("/")
    def index():
        """Render the live recognition dashboard for a single selected spell."""
        spell_name = request.args.get("spell")

        current_spell = None
        if spell_name:
            current_spell = spells_col.find_one({"spell": spell_name}, {"_id": 0})

        return render_template("index.html", spell=current_spell)


    @app.route("/spells")
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

            return (
                jsonify({"success": True, "file_id": str(file_id), "spell": spell_name}),
                200,
            )

        except Exception as e:  # pylint: disable=broad-except
            return jsonify({"error": str(e)}), 500

    @app.route("/api/pronunciation", methods=["POST"])
    def assess_pronunciation():
        """Assess pronunciation of uploaded audio file."""
        try:
            data = request.get_json(silent=True) or {}
            file_id = data.get("file_id")
            spell_name = data.get("spell")

            if not file_id or not spell_name:
                return jsonify({"error": "file_id and spell are required"}), 400
            
            spell_doc = spells_col.find_one({"spell": spell_name}, {"_id": 0})
            if not spell_doc:
                return jsonify({"error": "Spell not found"}), 404
            
            standard = spell_doc["spell"]

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                audio_store.load_audio_to_file(ObjectId(file_id), tmp)
                user_audio = tmp.name

            user_wav = convert_to_wav(user_audio)

            result = pronunciation_assessment(standard, user_wav)

            # clean up temp file
            try:
                os.remove(user_audio)
            except OSError:
                pass

            return jsonify(result), (200 if result.get("success") else 500)

        except Exception as e:  # pylint: disable=broad-except
            return jsonify({"error": str(e)}), 500
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
