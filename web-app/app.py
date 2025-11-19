"""Flask web application that allows user to check Harry Potter spell pronunciation."""

import os
from bson import ObjectId
from flask import Flask, redirect, render_template, abort, request, jsonify, url_for, flash
import requests
from pymongo import MongoClient
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from models import User
from dotenv import load_dotenv
load_dotenv()

login_manager = LoginManager()

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL")

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    login_manager.init_app(app) # config login manager for login
    login_manager.login_view = "login" 

    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    app.db = client[os.getenv("DB_NAME", "default_db")]
    app.spells_col = app.db["spells"]

    @login_manager.user_loader
    def load_user(user_id):
        db_user = app.db.users.find_one({"_id": ObjectId(user_id)})
        return User(db_user) if db_user else None

    @app.route("/audio")
    @login_required
    def index():
        """Render the live recognition dashboard for a single selected spell."""
        spell_name = request.args.get("spell")

        current_spell = None
        if spell_name:
            current_spell = app.spells_col.find_one({"spell": spell_name}, {"_id": 0})

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

        spells = list(app.spells_col.find(filter_r, {"_id": 0}))

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
        spell = app.spells_col.find_one({"spell": spell_name}, {"_id": 0})
        if not spell:
            abort(404)
        return render_template("spellpage.html", spell=spell)


    @app.route("/api/spells", methods=["GET"])
    def get_spells():
        """Return all spells as JSON."""
        spells = list(app.spells_col.find({}, {"_id": 0}))
        return jsonify(spells)


    @app.route("/api/audio", methods=["POST"])
    @login_required
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

            ml_result["spell"] = spell_name
            return jsonify(ml_result), 200

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
        
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            if not email or not password:
                flash("Please fill in both fields!")
                return redirect(url_for("login"))
            
            db_email = app.db.users.find_one({"email": email})
            # no such user
            if not db_email:
                flash("Email not registered.")
                return redirect(url_for("login"))
            
            if db_email["password"] == password:
                user = User(db_email)
                login_user(user)              
                return redirect(url_for("profile"))
            else:
                flash("Wrong password!")
                return redirect(url_for("login"))
            
        return render_template("login.html")
    
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("spells_view"))

    @app.route('/register', methods = ['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")

            if not username or not email or not password:
                flash("Please fill in all fields!")
                return redirect(url_for("register"))
            
            db_email = app.db.users.find_one({"email": email})
            if db_email:
                flash("Email already registered!")
                return redirect(url_for("register"))
        
            new_user = ({
                "username": username,
                "email": email,
                "password": password,
            })
            doc = app.db.users.insert_one(new_user)

            user_doc = app.db.users.find_one({"_id": doc.inserted_id})
            user = User(user_doc)
            login_user(user)

            return redirect(url_for("profile"))
        return render_template("register.html")
    
    @app.route("/profile")
    @login_required
    def profile():
        userdata = app.db.users.find_one({"_id": ObjectId(current_user.id)})
        return render_template("profile.html", user = userdata)
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
