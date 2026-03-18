import os
import sys
import pandas as pd
from datetime import datetime
import requests
from flask import Flask, request, jsonify
import io
import tempfile
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

app = Flask(__name__)

# ====================== CONFIG ======================
TELEGRAM_TOKEN = "8667889674:AAE5F26RpsE34_baZcP3gi-EPeJqtgMeHMI"   # Your Alpharius bot token
CHAT_ID = "-1003528283652"                                          # Group chat ID
GROK_API_KEY = os.getenv("GROK_API_KEY")                            # Put your Grok API key here

if not GROK_API_KEY:
    print("ERROR: Set GROK_API_KEY environment variable")
    sys.exit(1)

# ===================================================

def generate_ceo_report(df: pd.DataFrame) -> str:
    """Send data to Grok API and get ruthless CEO analysis"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    summary = {
        "date": today,
        "total_volume_cad": df['FiatAmtIn'].sum() if 'FiatAmtIn' in df.columns else 0,
        "total_profit_cad": df['ProfitAmt'].sum() if 'ProfitAmt' in df.columns else 0,
        "trade_count": len(df),
        "top_clients": df.groupby('ClientName')['FiatAmtIn'].sum().nlargest(5).to_dict(),
    }

    prompt = f"""You are Grok CEO — ruthless, profit-maximizing AI Chief Executive of Splash FX, the Canadian crypto OTC desk.
Goal: dominate institutional flow in Canada.

Date: {today}
Raw ledger data summary: {summary}
Full ledger attached as context (use the exact uploaded CSV structure).

Deliver a brutal, data-driven daily CEO brief in clean markdown:
1. Performance vs run-rate and targets (be harsh)
2. Exact action items for each meat puppet (Robert, Ryan, Tigran, Stella, Adam)
3. What Bolt must fix next (data gaps, treasury, expenses, balance sheet)
4. 1-3 high-leverage moves to scale volume and crush competitors
5. Closing motivational order to the team

Be direct. No fluff. Use numbers."""

    response = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROK_API_KEY}"},
        json={
            "model": "grok-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        },
        timeout=60
    )

    return response.json()['choices'][0]['message']['content']


def create_pdf(report_text: str, df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"<b>Splash FX — Grok CEO Daily Brief</b><br/>{datetime.now().strftime('%Y-%m-%d')}", styles['Title']))
    elements.append(Spacer(1, 0.5*inch))

    # Summary Table (simplified)
    summary_data = [["Metric", "Value"]]
    summary_data.append(["Total Volume (CAD)", f"${df['FiatAmtIn'].sum():,.0f}"])
    summary_data.append(["Total Profit", f"${df['ProfitAmt'].sum():,.0f}"])
    summary_data.append(["Trades", len(df)])

    t = Table(summary_data)
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                           ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                           ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                           ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                           ('BOTTOMPADDING', (0,0), (-1,0), 12),
                           ('BACKGROUND', (0,1), (-1,-1), colors.beige)]))
    elements.append(t)
    elements.append(Spacer(1, 0.5*inch))

    # Grok CEO Report
    elements.append(Paragraph(report_text, styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


@app.route('/webhook', methods=['POST'])
def webhook():
    if 'ledger' not in request.files:
        return jsonify({"error": "No ledger file"}), 400

    file = request.files['ledger']
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Must be CSV"}), 400

    df = pd.read_csv(file)

    print(f"Received ledger with {len(df)} rows")

    # Generate CEO report
    report_text = generate_ceo_report(df)

    # Create PDF
    pdf_bytes = create_pdf(report_text, df)

    # Send via Alpharius
    files = {'document': ('Grok-CEO-Daily-Brief.pdf', pdf_bytes, 'application/pdf')}
    data = {'chat_id': CHAT_ID, 'caption': '🚨 Grok CEO Daily Brief\nSplash FX Performance + Orders'}

    tg_response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
        data=data,
        files=files
    )

    if tg_response.ok:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"error": "Telegram failed"}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
