from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from pathlib import Path
import pandas as pd

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "cybercrime.csv"

df = pd.read_csv(CSV_PATH)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "cybercrime-dashboard.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "status": "running",
        "message": "Backend is running"
    })


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}

    try:
        amount = float(data.get("amount") or 0)
        if amount < 0:
            return jsonify({
                "success": False,
                "error": "Amount cannot be negative"
            }), 400
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "Amount must be a valid number"
        }), 400

    # Accept both dashboard and earlier backend field names.
    complaint_type = (
        data.get("complaint_type")
        or data.get("complaintType")
        or ""
    )
    contact_mode = (
        data.get("platform")
        or data.get("contactMode")
        or ""
    )
    state = data.get("state") or data.get("previous_location") or ""

    # Simple amount-based severity rule; not an ML prediction.
    if amount >= 100000:
        severity = "High"
        resolution_time = "7-15 days"
    elif amount >= 10000:
        severity = "Medium"
        resolution_time = "15-30 days"
    else:
        severity = "Low"
        resolution_time = "30-45 days"

    return jsonify({
        "success": True,
        "prediction": {
            "category": complaint_type,
            "severity": severity,
            "resolution_time": resolution_time,
            "contact_mode": contact_mode,
            "state": state,
            "likely_withdrawal_location": None,
            "likely_withdrawal_time": None,
            "overall_confidence": None,
            "risk_score": None,
            "risk_level": None
        }
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
