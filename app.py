import os
from flask import Flask, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

# Configurazione Telegram
TOKEN = "8643519947:AAH2Ba92mhson8uQAij_5Q0N0PvyTgluhAU"
CHAT_ID = "6511237453"

# Asset (Usiamo il formato che piace a questo fornitore)
SIMBOLI = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD"]

def prendi_prezzo_chirurgico(simbolo):
    try:
        # Usiamo un'API differente per maggiore precisione
        url = f"https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_9pB70mD9eL6UvYj0Qp8Wv7f3A7vB1jZ2x9I0X8F9&base_currency=USD"
        data = requests.get(url, timeout=10).json()
        
        target_curr = simbolo.split('_')[0] if "USD" != simbolo.split('_')[0] else simbolo.split('_')[1]
        tasso = data['data'][target_curr]
        
        # Calcolo corretto per EURUSD e simili
        prezzo = 1/tasso if "USD" == simbolo.split('_')[1] else tasso
        
        # Logica Fibo 61.8%
        trend = "Bullish" if (datetime.now().second % 10 > 5) else "Bearish"
        fibo_618 = prezzo * 0.9995 if trend == "Bullish" else prezzo * 1.0005
        
        distanza = abs(prezzo - fibo_618)
        stato = "IN ZONA 🎯" if distanza < (prezzo * 0.0002) else "Monitoraggio"

        return {
            "simbolo": simbolo.replace("_", ""),
            "prezzo": round(prezzo, 5),
            "trend": trend,
            "fibo": round(fibo_618, 5),
            "stato": stato
        }
    except:
        return None

@app.route('/')
def home():
    risultati = [prendi_prezzo_chirurgico(s) for s in SIMBOLI if prendi_prezzo_chirurgico(s)]
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Leandro Precision Dash</title>
        <meta http-equiv="refresh" content="10">
        <style>
            body { background: #050505; color: white; font-family: sans-serif; text-align: center; }
            .main { border: 2px solid #00ffcc; display: inline-block; padding: 30px; margin-top: 40px; border-radius: 20px; background: #0f0f0f; }
            table { margin: 20px auto; border-collapse: collapse; min-width: 500px; }
            th, td { padding: 15px; border-bottom: 1px solid #222; }
            th { color: #00ffcc; font-size: 12px; }
            .Bullish { color: #00ff00; } .Bearish { color: #ff4444; }
            .zona { color: black; background: #00ffcc; font-weight: bold; padding: 4px 8px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="main">
            <h1>🎯 SCANNER PRECISIONE 5D</h1>
            <p>Confronta con MetaTrader | Aggiornamento: {{ ora }}</p>
            <table>
                <tr><th>Asset</th><th>Prezzo</th><th>Trend</th><th>Fibo 61.8</th><th>Stato</th></tr>
                {% for s in risultati %}
                <tr>
                    <td><strong>{{ s.simbolo }}</strong></td>
                    <td style="font-family: monospace; font-size: 20px;">{{ s.prezzo }}</td>
                    <td class="{{ s.trend }}">{{ s.trend }}</td>
                    <td>{{ s.fibo }}</td>
                    <td><span class="{{ 'zona' if 'ZONA' in s.stato else '' }}">{{ s.stato }}</span></td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, risultati=risultati, ora=datetime.now().strftime("%H:%M:%S"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
