
import os
from datetime import datetime
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "8667889674:AAE5F26RpsE34_baZcP3gi-EPeJqtgMeHMI"
CHAT_ID = "-1003528283652"

def send_to_group(text: str):
    print(f"Attempting to send to group: {text[:100]}...")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "parse_mode": "HTML", "text": text}, timeout=10)
        print(f"Telegram response: {r.status_code} - {r.text}")
        return r.ok
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False

@app.route('/webhook/bolt', methods=['POST'])
def bolt_webhook():
    print("Bolt webhook triggered - files received")
    send_to_group("✅ Bolt files received by server.")
    return jsonify({"status": "success"}), 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    print("Telegram message received")
    return jsonify({"ok": True}), 200

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "alive", "time": datetime.now().isoformat()}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Grok CEO Bot started on port {port} at {datetime.now()}")
    app.run(host='0.0.0.0', port=port)
