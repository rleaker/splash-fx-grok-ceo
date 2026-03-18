import os
import sys
import pandas as pd
from datetime import datetime
import requests
from flask import Flask, request, jsonify
import io
import tempfile

app = Flask(__name__)

# ====================== CONFIG ======================
TELEGRAM_TOKEN = "8667889674:AAE5F26RpsE34_baZcP3gi-EPeJqtgMeHMI"
CHAT_ID = "-1003528283652"
GROK_API_KEY = os.getenv("GROK_API_KEY")

if not GROK_API_KEY:
    print("ERROR: Set GROK_API_KEY environment variable")
    sys.exit(1)

UPLOAD_FOLDER = "/tmp/splash_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===================================================

@app.route('/webhook/bolt', methods=['POST'])
def bolt_webhook():
    """New Bolt webhook - accepts 3 files: ledger, crypto, fiat"""
    files_received = {}
    
    for key in ['ledger', 'crypto', 'fiat']:
        file = request.files.get(key)
        if file and file.filename:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"{timestamp}_{key}_{file.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            files_received[key] = filepath
            print(f"✅ Saved {key} file: {filename}")

    if not files_received:
        return jsonify({"error": "No files received"}), 400

    print(f"✅ Bolt webhook success - received {len(files_received)} files")

    # TODO: In next version we will call Grok CEO analysis here with all 3 files
    return jsonify({
        "status": "success",
        "message": "Files received and saved",
        "files": list(files_received.keys())
    }), 200


@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Keep original Telegram bot functionality alive"""
    update = request.get_json()
    if update and 'message' in update:
        print("Received Telegram message - bot still alive")
        # For now just acknowledge. We can expand later.
        return jsonify({"status": "ok"}), 200
    
    return jsonify({"status": "ok"}), 200


@app.route('/', methods=['GET'])
def health_check():
    """Health check so Render never kills the container"""
    return jsonify({
        "status": "alive",
        "time": datetime.now().isoformat(),
        "endpoints": ["/webhook/bolt", "/webhook", "/"]
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Grok CEO Bot starting on port {port}")
    app.run(host='0.0.0.0', port=port)
