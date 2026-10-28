
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    complaint_type = data.get("complaintType", "")
    description = data.get("description", "")
    amount = float(data.get("amount", 0))
    contact_mode = data.get("contactMode", "")
    state = data.get("state", "")

    # Simple rule-based prediction
    if amount >= 100000:
        severity = "High"
        resolution_time = "7-15 days"

    elif amount >= 10000:
        severity = "Medium"
        resolution_time = "15-30 days"

    else:
        severity = "Low"
        resolution_time = "30-45 days"

    result = {
        "category": complaint_type,
        "severity": severity,
        "resolution_time": resolution_time,
        "contact_mode": contact_mode,
        "state": state
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
