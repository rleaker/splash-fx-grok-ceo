import os
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = "8667889674:AAE5F26RpsE34_baZcP3gi-EPeJqtgMeHMI"
CHAT_ID = "-1003528283652"

@app.route('/webhook/bolt', methods=['POST'])
def bolt_webhook():
    files = {}
    for key in ['ledger', 'crypto', 'fiat']:
        file = request.files.get(key)
        if file and file.filename:
            files[key] = file.filename
            print(f"✅ Received {key}: {file.filename}")
    
    return jsonify({
        "status": "success",
        "received": list(files.keys()),
        "count": len(files)
    }), 200


@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    return jsonify({"status": "ok"}), 200


@app.route('/', methods=['GET'])
def health():
    return jsonify({
        "status": "alive",
        "time": datetime.now().isoformat(),
        "message": "Grok CEO Bot is running"
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Grok CEO Bot starting on port {port} at {datetime.now()}")
    app.run(host='0.0.0.0', port=port)
