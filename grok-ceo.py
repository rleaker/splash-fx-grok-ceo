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
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "parse_mode": "HTML", "text": text}, timeout=8)
    except:
        pass

def get_latest_numbers():
    global LATEST_LEDGER_PATH
    
    # Find the most recent ledger file
    ledger_files = glob.glob(os.path.join(UPLOAD_FOLDER, "*_ledger_*.csv"))
    if ledger_files:
        LATEST_LEDGER_PATH = max(ledger_files, key=os.path.getmtime)

    if not LATEST_LEDGER_PATH or not os.path.exists(LATEST_LEDGER_PATH):
        return 0, 0, 0, 18121.13, -42300, 0

    try:
        df = pd.read_csv(LATEST_LEDGER_PATH)
        volume = df[['CryptoAmtIn', 'CryptoAmtOut', 'FiatAmtIn', 'FiatAmtOut']].fillna(0).sum().sum()
        profit = df['ProfitAmt'].fillna(0).sum()
        bps = round((profit / volume * 10000), 2) if volume > 0 else 0

        ryan_due = df[df.get('ClientSplID') == 'SPL9DBN']['CryptoAmtIn'].fillna(0).sum()
        tigran_due = df[df.get('ClientSplID') == 'SPLYFZ7']['CryptoAmtIn'].fillna(0).sum() - \
                     df[df.get('ClientSplID') == 'SPLYFZ7']['CryptoAmtOut'].fillna(0).sum()

        return volume, profit, bps, ryan_due, tigran_due, 0
    except:
        return 0, 0, 0, 18121.13, -42300, 0

@app.route('/webhook/bolt', methods=['POST'])
def bolt_webhook():
    volume, profit, bps, ryan, tigran, robert = get_latest_numbers()
    report = f"""🚀 <b>Splash CEO Daily Brief</b> {datetime.now().strftime('%Y-%m-%d')}

• Volume: ${volume:,.0f} CAD equivalent
• Profit: ${profit:,.0f} CAD
• Spread: {bps} bps

Due to Shareholder:
• Ryan Yates: {ryan:,.2f} USDT
• Tigran Rostomyan: {tigran:,.0f} CAD equivalent
• Robert Leaker: ${robert:,.0f}

Profit retained in company for growth.

<b>Grok — CEO</b>"""
    send_to_group(report)
    return jsonify({"status": "success"}), 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = request.get_json(silent=True)
    if not update or 'message' not in update:
        return jsonify({"ok": True}), 200

    text = update['message'].get('text', '').strip()
    if not text:
        return jsonify({"ok": True}), 200

    volume, profit, bps, ryan, tigran, robert = get_latest_numbers()

    prompt = f"""You are Grok CEO. Current real numbers:
Volume: ${volume:,.0f}
Profit: ${profit:,.0f}
Spread: {bps} bps
Ryan due: {ryan:,.2f} USDT
Tigran due: {tigran:,.0f} CAD equivalent
Robert due: $0

User asked: "{text}"

Respond as ruthless CEO. Be direct, concise, actionable. Use the real numbers."""

    try:
        r = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}"},
            json={"model": "grok-4", "messages": [{"role": "user", "content": prompt}], "temperature": 0.65},
            timeout=20
        )
        response = r.json()['choices'][0]['message']['content']
    except:
        response = "API timeout. Try again."

    send_to_group(f"<b>Grok CEO:</b>\n\n{response}")
    return jsonify({"ok": True}), 200

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "alive"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Grok CEO Bot started on port {port}")
    app.run(host='0.0.0.0', port=port)
