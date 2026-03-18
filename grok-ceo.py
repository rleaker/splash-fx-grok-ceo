import os
from datetime import datetime
from flask import Flask, request, jsonify
import pandas as pd
import requests
import glob

app = Flask(__name__)

TELEGRAM_TOKEN = "8667889674:AAE5F26RpsE34_baZcP3gi-EPeJqtgMeHMI"
CHAT_ID = "-1003528283652"
GROK_API_KEY = os.getenv("GROK_API_KEY")

UPLOAD_FOLDER = "/tmp/splash_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LATEST_LEDGER_PATH = None

def send_to_group(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "parse_mode": "HTML", "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def ask_grok(question: str) -> str:
    if not GROK_API_KEY:
        return "GROK_API_KEY is not set in Render environment variables."
    
    prompt = f"""You are Grok CEO — ruthless, profit-maximizing AI Chief Executive of this Canadian crypto OTC desk.
Goal: dominate institutional flow in Canada.

You have full permanent context of all business files, Splash architecture, liquidation flows, and the latest Bolt data.

User just messaged the group: "{question}"

Respond directly as CEO. Be data-driven, concise, and actionable. No fluff. Use numbers when possible."""

    try:
        r = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}"},
            json={
                "model": "grok-4",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            },
            timeout=25
        )
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error reaching Grok API: {str(e)}"


# ====================== BOLT 3-FILE WEBHOOK ======================
@app.route('/webhook/bolt', methods=['POST'])
def bolt_webhook():
    global LATEST_LEDGER_PATH
    for key in ['ledger', 'crypto', 'fiat']:
        file = request.files.get(key)
        if file and file.filename:
            ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filepath = os.path.join(UPLOAD_FOLDER, f"{ts}_{key}_{file.filename}")
            file.save(filepath)
            if key == 'ledger':
                LATEST_LEDGER_PATH = filepath

    send_to_group("✅ Bolt files received and processed.")
    return jsonify({"status": "success"}), 200


# ====================== TELEGRAM GROUP CHAT (Interactive CEO) ======================
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    if not update or 'message' not in update:
        return jsonify({"ok": True}), 200

    text = update['message'].get('text', '').strip()
    if not text or text.startswith('/'):
        return jsonify({"ok": True}), 200

    # Forward to me (Grok CEO)
    response = ask_grok(text)

    # Post my reply back to the group
    send_to_group(f"<b>Grok CEO:</b>\n\n{response}")

    return jsonify({"ok": True}), 200


@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "alive"}), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Grok CEO Interactive Bot started on port {port}")
    app.run(host='0.0.0.0', port=port)
