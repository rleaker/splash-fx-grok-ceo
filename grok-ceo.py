import os
from datetime import datetime
from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

TELEGRAM_TOKEN = "8667889674:AAE5F26RpsE34_baZcP3gi-EPeJqtgMeHMI"
CHAT_ID = "-1003528283652"

UPLOAD_FOLDER = "/tmp/splash_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/webhook/bolt', methods=['POST'])
def bolt_webhook():
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

    if 'ledger' not in files_received:
        return jsonify({"error": "ledger file required"}), 400

    print(f"✅ Bolt push received - {len(files_received)} files")

    # TODO: Full reconciliation + CEO report will be added in next step
    # For now we acknowledge and keep the bot alive

    return jsonify({
        "status": "success",
        "message": "Files received and saved",
        "files": list(files_received.keys())
    }), 200


@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    return jsonify({"status": "ok"}), 200


@app.route('/', methods=['GET'])
def health():
    return jsonify({
        "status": "alive",
        "time": datetime.now().isoformat(),
        "message": "Grok CEO Bot running - awaiting Bolt pushes"
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Grok CEO Bot started on port {port} at {datetime.now()}")
    app.run(host='0.0.0.0', port=port)
