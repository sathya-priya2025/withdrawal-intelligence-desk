from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Load CSV from the same folder as this file
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "cybercrime.csv"

df = pd.read_csv(CSV_PATH)
df.columns = df.columns.str.strip()


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}

    try:
        amount = float(data.get("amount") or 0)
        if amount < 0:
            return jsonify({"error": "Amount cannot be negative"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount"}), 400

    complaint_type = data.get("complaintType", "")
    description = data.get("description", "")
    contact_mode = data.get("contactMode", "")
    state = data.get("state", "")

    # Keep the existing severity rules
    if amount >= 100000:
        severity = "High"
        resolution_time = "7-15 days"
    elif amount >= 10000:
        severity = "Medium"
        resolution_time = "15-30 days"
    else:
        severity = "Low"
        resolution_time = "30-45 days"

    # Find the dataset row with the closest transaction amount
    location = None
    withdrawal_time = None

    required_columns = [
        "amount",
        "transaction_count",
        "previous_location",
        "withdrawal_location",
        "withdrawal_time"
    ]

    if all(column in df.columns for column in required_columns):
        dataset = df.copy()
        dataset["amount"] = pd.to_numeric(
            dataset["amount"], errors="coerce"
        )
        dataset = dataset.dropna(
            subset=[
                "amount",
                "withdrawal_location",
                "withdrawal_time"
            ]
        )

        if not dataset.empty:
            closest_index = (
                dataset["amount"] - amount
            ).abs().idxmin()

            location = str(
                dataset.loc[closest_index, "withdrawal_location"]
            )
            withdrawal_time = str(
                dataset.loc[closest_index, "withdrawal_time"]
            )

    result = {
        "category": complaint_type,
        "severity": severity,
        "resolution_time": resolution_time,
        "contact_mode": contact_mode,
        "state": state,
        "likely_withdrawal_location": location,
        "likely_withdrawal_time": withdrawal_time
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
