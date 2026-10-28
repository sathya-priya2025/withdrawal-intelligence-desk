from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from pathlib import Path
import pandas as pd

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "cybercrime.csv"

df = pd.read_csv(CSV_PATH)
df.columns = df.columns.str.strip()
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
# Keep existing severity logic
if amount >= 100000:
    severity = "High"
    resolution_time = "7-15 days"
elif amount >= 10000:
    severity = "Medium"
    resolution_time = "15-30 days"
else:
    severity = "Low"
    resolution_time = "30-45 days"

# Use dataset to find the closest matching transaction
location = None
withdrawal_time = None

required = {
    "amount",
    "transaction_count",
    "previous_location",
    "predicted_location",
    "predicted_time"
}

if required.issubset(df.columns) and not df.empty:
    dataset = df.copy()
    dataset["amount"] = pd.to_numeric(
        dataset["amount"], errors="coerce"
    )
    dataset = dataset.dropna(
        subset=["amount", "predicted_location", "predicted_time"]
    )

    if not dataset.empty:
        closest = (dataset["amount"] - amount).abs().idxmin()
        location = str(dataset.loc[closest, "predicted_location"])
        withdrawal_time = str(dataset.loc[closest, "predicted_time"])

    return jsonify({
        "success": True,
        "prediction": {
            "category": complaint_type,
            "severity": severity,
            "resolution_time": resolution_time,
            "contact_mode": contact_mode,
            "state": state,
            "likely_withdrawal_location": location,
            "likely_withdrawal_time": withdrawal_time,
            "overall_confidence":overall_confidence,
            "risk_score":risk_score,
            "risk_level":risk_level
            if not dataset.empty:
    # Confidence here means the percentage of rows
    # sharing the selected location and time.
    matching = dataset[
        (dataset["predicted_location"].astype(str) == location) &
        (dataset["predicted_time"].astype(str) == withdrawal_time)
    ]

    overall_confidence = round(
        len(matching) / len(dataset) * 100, 2
    )

    # Simple amount-based risk score (0-100).
    risk_score = min(round(amount / 1000), 100)

    if risk_score >= 70:
        risk_level = "High"
    elif risk_score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"
        }
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
