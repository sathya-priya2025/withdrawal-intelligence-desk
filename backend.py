from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return """
    <html>
        <head>
            <title>Withdrawal Intelligence Desk</title>
        </head>
        <body>
            <h1>Withdrawal Intelligence Desk</h1>
            <p>Cybercrime Prediction Backend is Running!</p>
            <p>API Status: Active</p>
        </body>
    </html>
    """

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
