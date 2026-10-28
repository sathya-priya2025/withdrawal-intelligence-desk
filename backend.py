from flask import Flask, request, jsonify,send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return send_from_directory(
        os.path.dirname(os.path.abspath(__file__)),
        "cybercrime-dashboard.html"
    )

@app.route("/health")
def health():
    return jsonify({
        "status": "success",
        "message": "Backend is running"
    })

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
