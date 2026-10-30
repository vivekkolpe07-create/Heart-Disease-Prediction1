from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os
import json
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify, session, redirect, url_for


# Project folder ka path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



# Frontend folder ko Flask se connect karna
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

CORS(app)


# Session Configuration
app.secret_key = "cardioai-development-secret-key"

# Database path
DB_PATH = os.path.join(BASE_DIR, "users.db")

# Initialize User Database
def init_db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# LOGIN PAGE
@app.route("/login")
def login_page():
    if session.get("user_id"):
        return redirect("/")
    return app.send_static_file("login.html")


# SIGNUP PAGE
@app.route("/signup")
def signup_page():
    if session.get("user_id"):
        return redirect("/")
    return app.send_static_file("signup.html")


# SIGNUP API
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    hashed_password = generate_password_hash(password)

    conn = sqlite3.connect(DB_PATH)

    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )
        conn.commit()

        session.clear()
        session["user_id"] = cursor.lastrowid
        session["user_name"] = name

        return jsonify({
            "message": "Account created successfully",
            "redirect": "/"
        })

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409

    finally:
        conn.close()


# LOGIN API
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    conn = sqlite3.connect(DB_PATH)

    try:
        user = conn.execute(
            "SELECT id, name, password FROM users WHERE email = ?",
            (email,)
        ).fetchone()
    finally:
        conn.close()

    if user and check_password_hash(user[2], password):
        session.clear()
        session["user_id"] = user[0]
        session["user_name"] = user[1]

        return jsonify({
            "message": "Login successful",
            "redirect": "/"
        })

    return jsonify({"error": "Invalid email or password"}), 401


# LOGOUT API
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({
        "message": "Logged out",
        "redirect": "/login"
    })


# Model aur scaler load karna
model = joblib.load(os.path.join(BASE_DIR, "model", "heart_model.pkl"))
scaler = joblib.load(os.path.join(BASE_DIR, "model", "scaler.pkl"))

FEATURES = [
    "age", "sex", "cp", "trestbps", "chol",
    "fbs", "restecg", "thalach", "exang",
    "oldpeak", "slope", "ca", "thal"
]


# Website homepage
@app.route("/")
def home():
    if not session.get("user_id"):
        return redirect("/login")

    return app.send_static_file("index.html")


# API health check
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

# Model performance metrics
@app.route("/api/metrics", methods=["GET"])
def metrics():
    if not session.get("user_id"):
        return jsonify({"error": "Please login first"}), 401
    metrics_path = os.path.join(BASE_DIR, "model", "metrics.json")

    with open(metrics_path, "r") as file:
        data = json.load(file)

    return jsonify(data)


# Heart disease prediction
@app.route("/api/predict", methods=["POST"])
def predict():

    if not session.get("user_id"):
        return jsonify({"error": "Please login first"}), 401
    try:
        data = request.get_json()        

        if not data:
            return jsonify({"error": "No input data provided"}), 400

        missing = [feature for feature in FEATURES if feature not in data]

        if missing:
            return jsonify({
                "error": "Missing input features",
                "missing_features": missing
            }), 400

        input_data = pd.DataFrame(
            [[data[feature] for feature in FEATURES]],
            columns=FEATURES
        )

        input_scaled = scaler.transform(input_data)

        prediction = int(model.predict(input_scaled)[0])
        probability = model.predict_proba(input_scaled)[0]

        return jsonify({
            "prediction": prediction,
            "result": "Higher predicted risk" if prediction == 1 else "Lower predicted risk",
            "probability": {
                "class_0": round(float(probability[0]) * 100, 2),
                "class_1": round(float(probability[1]) * 100, 2)
            }
        })

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400

    except Exception as error:
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)