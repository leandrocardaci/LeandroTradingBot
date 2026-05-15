import os
from flask import Flask, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

# Configurazione Telegram
TOKEN = "8643519947:AAH2Ba92mhson8uQAij_5Q0N0PvyTgluhAU"
CHAT_ID = "6511237453"

# Asset da monitorare
SIMBOLI = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCHF"]

def prendi_prezzo_forex(simbolo):
    try:
        # Sistema ultra-rapido per prezzi reali 5 decimali
        url = f"https://api.exchangerate-api.com/v4/latest/USD"
        data = requests.get(url, timeout=10).json()
        
        base = data['rates'][simbolo[:3]]
        target = data['rates'][simbolo[3:]]
        
        # Calcolo incrociato per avere il prezzo Forex reale
        if simbolo == "USDJPY": prezzo = target
        elif simbolo == "USDCHF": prezzo = target
        else: prezzo = target / base
            
        # Trend e Fibo simulati per test operativo immediato
        trend = "Bullish" if (datetime.now().second % 10 > 5) else "Bearish"
        fibo_618 = prezzo * 0.9992 if trend == "Bullish" else prezzo * 1.0008
        
        distanza = abs(prezzo - fibo_618)
        stato = "IN ZONA 🎯" if distanza < (prezzo * 0.0004) else "Monitoraggio"
        
        if stato == "IN ZONA 🎯":
            requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text=🔔 {simbolo} in ZONA!")

        return {
            "simbolo": simbolo,
            "prezzo": round(prezzo, 5),
            "trend": trend,
            "fibo": round(fibo_618, 5),
            "stato": stato
        }
    except: return None

@app.route('/')
def home():
    risultati = [prendi_prezzo_forex(s) for s in SIMBOLI if prendi_prezzo_forex(s)]
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Leandro Live Dash</title>
        <meta http-equiv="refresh" content="10">
        <style>
            body { background: #050505; color: white; font-family: 'Courier New', monospace; text-align: center; }
            .box { border: 2px solid #00ffcc; display: inline-block; padding: 20px; margin-top: 50px; background: #111; border-radius: 15px; }
            table { margin: 20px auto; border-collapse: collapse; }
            th, td { padding: 15px 30px; border-bottom: 1px solid #333; }
            th { color: #00ffcc; text-decoration: underline; }
            .Bullish { color: #00ff00; } .Bearish { color: #ff4444; }
            .zona { color: black; background: #00ffcc; font-weight: bold; padding: 5px; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>📊 LEANDRO LIVE SCANNER</h1>
            <p>Aggiornamento ogni 10 secondi | {{ ora }}</p>
            <table>
                <tr><th>Asset</th><th>Prezzo Real-Time</th><th>Trend</th><th>Target Fibo</th><th>Stato</th></tr>
                {% for s in risultati %}
                <tr>
                    <td>{{ s.simbolo }}</td>
                    <td><strong>{{ s.prezzo }}</strong></td>
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
