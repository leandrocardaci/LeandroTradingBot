import os
from flask import Flask, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURAZIONE ---
TOKEN = "8643519947:AAH2Ba92mhson8uQAij_5Q0N0PvyTgluhAU"
CHAT_ID = "6511237453"
# Usiamo i nomi corretti per il nuovo fornitore
SIMBOLI = ["EUR/USD", "GBP/USD", "USD/JPY"]

def prendi_prezzo_reale(coppia):
    try:
        # Usiamo un'API pubblica che non richiede chiavi complicate per ora
        url = f"https://api.twelvedata.com/quote?symbol={coppia}&apikey=8618e76f626c4573852028682898745c"
        data = requests.get(url).json()
        
        prezzo = float(data['close'])
        alto = float(data['high'])
        basso = float(df['low']) # Usiamo i dati del giorno per semplicità ora
        
        # Trend veloce (basato su apertura/chiusura)
        trend = "Bullish" if prezzo > float(data['open']) else "Bearish"
        
        # Fibo 61.8 semplice del range giornaliero
        fibo = alto - (0.618 * (alto - basso)) if trend == "Bullish" else basso + (0.618 * (alto - basso))
        
        return {
            "simbolo": coppia,
            "prezzo": round(prezzo, 5),
            "trend": trend,
            "fibo": round(fibo, 5),
            "stato": "In Zona" if abs(prezzo - fibo) < 0.0005 else "Monitoraggio"
        }
    except:
        return None

@app.route('/')
def home():
    risultati = []
    for s in SIMBOLI:
        res = prendi_prezzo_reale(s)
        if res: risultati.append(res)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Leandro Dash</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding: 50px; }
            table { margin: 20px auto; border-collapse: collapse; width: 80%; background: #1e1e1e; }
            th, td { padding: 15px; border: 1px solid #333; }
            .Bullish { color: #00ff00; font-weight: bold; }
            .Bearish { color: #ff4444; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>📊 Dashboard Trading Leandro</h1>
        <p>Ultimo aggiornamento: {{ ora }}</p>
        <table>
            <tr><th>Simbolo</th><th>Prezzo</th><th>Trend</th><th>Fibo 61.8</th><th>Stato</th></tr>
            {% for s in risultati %}
            <tr>
                <td>{{ s.simbolo }}</td>
                <td>{{ s.prezzo }}</td>
                <td class="{{ s.trend }}">{{ s.trend }}</td>
                <td>{{ s.fibo }}</td>
                <td>{{ s.stato }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html, risultati=risultati, ora=datetime.now().strftime("%H:%M:%S"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
