import os
from flask import Flask, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

# Configurazione Telegram
TOKEN = "8643519947:AAH2Ba92mhson8uQAij_5Q0N0PvyTgluhAU"
CHAT_ID = "6511237453"

# Simboli Forex corretti
SIMBOLI = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF"]

def prendi_dati_reali(simbolo):
    try:
        # Usiamo un fornitore di dati Forex più preciso
        url = f"https://api.twelvedata.com/price?symbol={simbolo}&apikey=8618e76f626c4573852028682898745c"
        response = requests.get(url, timeout=8)
        data = response.json()
        
        if 'price' in data:
            prezzo = float(data['price'])
            
            # Simuliamo il Trend e il Fibo basandoci sul prezzo attuale per il test di stasera
            # (Domani aggiungeremo le candele storiche per il calcolo matematico perfetto)
            trend = "Bullish" if (datetime.now().second % 10 > 5) else "Bearish"
            fibo_618 = prezzo * 0.9995 if trend == "Bullish" else prezzo * 1.0005
            
            distanza = abs(prezzo - fibo_618)
            # Soglia di vicinanza molto stretta per il Forex
            stato = "IN ZONA 🎯" if distanza < (prezzo * 0.0003) else "Monitoraggio"
            
            if stato == "IN ZONA 🎯":
                msg = f"⚠️ {simbolo} PREZZO: {prezzo} - Vicino al 61.8% Fibo!"
                requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}")

            return {
                "simbolo": simbolo,
                "prezzo": round(prezzo, 5),
                "trend": trend,
                "fibo": round(fibo_618, 5),
                "stato": stato
            }
    except:
        return None

@app.route('/')
def home():
    risultati = []
    for s in SIMBOLI:
        dati = prendi_dati_reali(s)
        if dati: risultati.append(dati)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Leandro Trading Dash</title>
        <meta http-equiv="refresh" content="15">
        <style>
            body { background: #0a0a0a; color: #f0f0f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; }
            .container { padding: 30px; }
            table { margin: 20px auto; border-collapse: collapse; width: 95%; background: #161616; border-radius: 10px; overflow: hidden; }
            th { background: #222; color: #00ffcc; padding: 15px; text-transform: uppercase; font-size: 14px; }
            td { padding: 15px; border-bottom: 1px solid #2a2a2a; font-size: 18px; }
            .Bullish { color: #00ff00; }
            .Bearish { color: #ff4444; }
            .zona { background: #ff9800; color: black; padding: 5px 10px; border-radius: 5px; font-weight: bold; animation: blink 1s infinite; }
            @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏛️ Leandro Premium Scanner</h1>
            <p>Dati Real-Time da Mercato Forex | Aggiornamento: {{ ora }}</p>
            <table>
                <tr><th>Asset</th><th>Prezzo MetaTrader</th><th>Trend H1</th><th>Target Fibo</th><th>Stato</th></tr>
                {% for s in segnali %}
                <tr>
                    <td><strong>{{ s.simbolo }}</strong></td>
                    <td style="font-family: monospace;">{{ s.prezzo }}</td>
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
    return render_template_string(html, segnali=risultati, ora=datetime.now().strftime("%H:%M:%S"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
