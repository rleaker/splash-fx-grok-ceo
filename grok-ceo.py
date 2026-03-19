import os
from datetime import datetime
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "8667889674:AAE5F26RpsE34_baZcP3gi-EPeJqtgMeHMI"
CHAT_ID = "-1003528283652"

def send_to_group(text: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": CHAT_ID, 
            "parse_mode": "HTML", 
            "text": text
        }, timeout=6)
    except:
        pass

@app.route('/webhook/bolt', methods=['POST'])
def bolt_webhook():
    print("Bolt webhook hit")
    send_to_group("✅ Bolt files received.")
    return jsonify({"status": "success"}), 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    print("Telegram message received")
    update = request.get_json(silent=True)
    if update and 'message' in update:
        text = update['message'].get('text', '').strip()
        if text:
            send_to_group(f"<b>Grok CEO:</b>\n\n{text}\n\n(Still in debug mode - full intelligence coming soon)")
    return jsonify({"ok": True}), 200

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "alive", "time": datetime.now().isoformat()}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Grok CEO Bot started on port {port} at {datetime.now()}")
    app.run(host='0.0.0.0', port=port)
