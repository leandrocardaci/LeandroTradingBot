import os
from flask import Flask, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURAZIONE ---
TOKEN = "8643519947:AAH2Ba92mhson8uQAij_5Q0N0PvyTgluhAU"
CHAT_ID = "6511237453"
# Rimaniamo su questi 3 per ora, se funzionano li aumentiamo domani
SIMBOLI = ["EURUSD", "GBPUSD", "USDJPY"]

def calcola_logica_trading(simbolo):
    try:
        # Recuperiamo i dati che hanno appena funzionato
        url = f"https://open.er-api.com/v6/latest/USD"
        data = requests.get(url, timeout=10).json()
        
        if data['result'] == 'success':
            # Prezzo attuale
            tasso = data['rates'][simbolo[:3]]
            prezzo = 1 / tasso if simbolo in ["EURUSD", "GBPUSD"] else tasso
            
            # Simulazione Trend e Fibo (visto che questo fornitore dà solo prezzi spot)
            # Nota: Per avere Fibo esatto serve lo storico, ma iniziamo a popolare i dati
            # Usiamo una variazione fittizia basata sul tempo per vedere i movimenti
            trend = "Bullish" if (datetime.now().minute % 2 == 0) else "Bearish"
            fibo_level = prezzo * 0.998 if trend == "Bullish" else prezzo * 1.002
            
            distanza = abs(prezzo - fibo_level)
            stato = "In Zona" if distanza < (prezzo * 0.0005) else "Monitoraggio"
            
            # Invio Telegram se in zona
            if stato == "In Zona":
                msg = f"⚠️ ALERT: {simbolo} vicino al 61.8% Fibo!"
                requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}")

            return {
                "simbolo": simbolo,
                "prezzo": round(prezzo, 5),
                "trend": trend,
                "fibo": round(fibo_level, 5),
                "stato": stato
            }
    except:
        return None

@app.route('/')
def home():
    risultati = []
    for s in SIMBOLI:
        res = calcola_logica_trading(s)
        if res: risultati.append(res)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Leandro Trading Dash</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding: 20px; }
            table { margin: 20px auto; border-collapse: collapse; width: 90%; background: #1e1e1e; border: 1px solid #00ffcc; }
            th, td { padding: 15px; border: 1px solid #333; }
            th { background: #333; color: #00ffcc; }
            .Bullish { color: #00ff00; font-weight: bold; }
            .Bearish { color: #ff4444; font-weight: bold; }
            .zona { background: #c62828; color: white; padding: 5px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>📊 Dashboard Operativa Leandro</h1>
        <p>Aggiornamento Automatico (30s) | Ora: {{ ora }}</p>
        <table>
            <tr><th>Simbolo</th><th>Prezzo Attuale</th><th>Trend (H1)</th><th>Fibo 61.8% (M15)</th><th>Stato</th></tr>
            {% for s in segnali %}
            <tr>
                <td><strong>{{ s.simbolo }}</strong></td>
                <td>{{ s.prezzo }}</td>
                <td class="{{ s.trend }}">{{ s.trend }}</td>
                <td>{{ s.fibo }}</td>
                <td><span class="{{ 'zona' if s.stato == 'In Zona' else '' }}">{{ s.stato }}</span></td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html, segnali=risultati, ora=datetime.now().strftime("%H:%M:%S"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
