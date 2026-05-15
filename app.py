import os
from flask import Flask, render_template_string
import threading
import time
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURAZIONE ---
TOKEN = "8643519947:AAH2Ba92mhson8uQAij_5Q0N0PvyTgluhAU"
CHAT_ID = "6511237453"

# Partiamo con solo 3 simboli per non sovraccaricare il server gratuito
SIMBOLI = ["EURUSD=X", "GBPUSD=X", "USDJPY=X"] 
ULTIMI_SEGNALI = []
STATO_BOT = "Inizializzazione..."

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={messaggio}&parse_mode=Markdown"
    try:
        import requests
        requests.get(url, timeout=5)
    except:
        pass

def calcola_fibo_e_trend(simbolo):
    try:
        # Scarichiamo dati minimi indispensabili
        df = yf.download(simbolo, period="5d", interval="1h", progress=False)
        if df.empty or len(df) < 20: return None
        
        prezzo = float(df['Close'].iloc[-1])
        sma20 = float(df['Close'].rolling(window=20).mean().iloc[-1])
        trend = "Bullish" if prezzo > sma20 else "Bearish"
        
        alto = float(df['High'].max())
        basso = float(df['Low'].min())
        diff = alto - basso
        fibo = alto - (0.618 * diff) if trend == "Bullish" else basso + (0.618 * diff)
        
        distanza = abs(prezzo - fibo)
        stato = "In Zona" if distanza < (prezzo * 0.0005) else "Monitoraggio"
        
        return {"simbolo": simbolo.replace("=X", ""), "prezzo": round(prezzo, 5), "trend": trend, "fibo": round(fibo, 5), "stato": stato}
    except Exception as e:
        print(f"Errore {simbolo}: {e}")
        return None

def scanner():
    global ULTIMI_SEGNALI, STATO_BOT
    while True:
        STATO_BOT = f"Scansione avviata alle {datetime.now().strftime('%H:%M:%S')}"
        nuovi = []
        for s in SIMBOLI:
            res = calcola_fibo_e_trend(s)
            if res:
                nuovi.append(res)
                if res["stato"] == "In Zona":
                    invia_telegram(f"🔔 {res['simbolo']} in zona!")
            time.sleep(3) # Pausa generosa tra i simboli
        
        if nuovi:
            ULTIMI_SEGNALI = nuovi
        STATO_BOT = f"Ultima scansione ok alle {datetime.now().strftime('%H:%M:%S')}"
        time.sleep(300)

@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Leandro Trading Dash</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body { background: #121212; color: #e0e0e0; font-family: sans-serif; text-align: center; padding: 20px; }
            table { margin: 20px auto; border-collapse: collapse; width: 80%; background: #1e1e1e; }
            th, td { padding: 12px; border: 1px solid #333; }
            .Bullish { color: #00ff00; } .Bearish { color: #ff4444; }
            .bot-status { color: #00ffcc; font-style: italic; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>📊 Dashboard Leandro</h1>
        <div class="bot-status">Stato Bot: {{ stato }}</div>
        <table>
            <tr><th>Simbolo</th><th>Prezzo</th><th>Trend</th><th>Fibo 61.8</th><th>Stato</th></tr>
            {% for s in segnali %}
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
    return render_template_string(html, segnali=ULTIMI_SEGNALI, stato=STATO_BOT)

if __name__ == "__main__":
    threading.Thread(target=scanner, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
