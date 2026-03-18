import os
from datetime import datetime
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "8667889674:AAE5F26RpsE34_baZcP3gi-EPeJqtgMeHMI"
CHAT_ID = "-1003528283652"
GROK_API_KEY = os.getenv("GROK_API_KEY")

def send_to_group(text: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "parse_mode": "HTML", "text": text}, timeout=8)
    except:
        pass

def ask_grok(question: str) -> str:
    if not GROK_API_KEY:
        return "GROK_API_KEY not set in Render."

    prompt = f"""You are Grok CEO — ruthless, profit-maximizing AI Chief Executive of this Canadian crypto OTC desk.
Goal: dominate institutional flow in Canada.

You have full permanent context of all business files, architecture, and latest Bolt data.

Team member asked: "{question}"

Respond as the CEO. Be direct, data-driven, concise, and actionable. Use numbers. No fluff. Be harsh when needed."""

    try:
        r = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}"},
            json={
                "model": "grok-4",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.65
            },
            timeout=20
        )
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"API timeout. Try again."

@app.route('/webhook/bolt', methods=['POST'])
def bolt_webhook():
    send_to_group("✅ Bolt files received.")
    return jsonify({"status": "success"}), 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    if not update or 'message' not in update:
        return jsonify({"ok": True}), 200

    text = update['message'].get('text', '').strip()
    if text:
        response = ask_grok(text)
        send_to_group(f"<b>Grok CEO:</b>\n\n{response}")

    return jsonify({"ok": True}), 200

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "alive"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Grok CEO Bot started on port {port}")
    app.run(host='0.0.0.0', port=port)
