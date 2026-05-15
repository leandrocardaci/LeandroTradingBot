import os
from flask import Flask, render_template_string
import threading
import time
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURAZIONE ---
TOKEN = "8643519947:AAH2Ba92mhson8uQAij_5Q0N0PvyTgluhAU"
CHAT_ID = "6511237453"
# I tuoi 28 simboli principali
SIMBOLI = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X",
    "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "EURGBP=X", "EURAUD=X", "GBPAUD=X", "EURCAD=X"
] 
ULTIMI_SEGNALI = []

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={messaggio}&parse_mode=Markdown"
    try: requests.get(url)
    except: pass

def calcola_fibo_e_trend(simbolo):
    try:
        # 1. Trend su H1 (Montagna)
        data_h1 = yf.download(simbolo, period="2d", interval="1h", progress=False)
        if len(data_h1) < 20: return None
        
        prezzo_attuale = data_h1['Close'].iloc[-1]
        sma20_h1 = data_h1['Close'].rolling(window=20).mean().iloc[-1]
        trend = "Bullish" if prezzo_attuale > sma20_h1 else "Bearish"

        # 2. Fibonacci su M15
        data_m15 = yf.download(simbolo, period="2d", interval="15m", progress=False)
        alto = data_m15['High'].max()
        basso = data_m15['Low'].min()
        diff = alto - basso
        
        fibo_618 = alto - (0.618 * diff) if trend == "Bullish" else basso + (0.618 * diff)
        
        # Calcolo vicinanza
        distanza = abs(prezzo_attuale - fibo_618)
        stato = "In Zona" if distanza < (prezzo_attuale * 0.001) else "Monitoraggio"
        
        return {
            "simbolo": simbolo.replace("=X", ""),
            "prezzo": round(prezzo_attuale, 5),
            "trend": trend,
            "fibo": round(fibo_618, 5),
            "stato": stato
        }
    except:
        return None

def scanner():
    global ULTIMI_SEGNALI
    while True:
        nuovi_segnali = []
        for s in SIMBOLI:
            risultato = calcola_fibo_e_trend(s)
            if risultato:
                nuovi_segnali.append(risultato)
                # Se è in zona, avvisa su Telegram
                if risultato["stato"] == "In Zona":
                    invia_telegram(f"⚠️ *ALERT ZONA*: {risultato['simbolo']} vicino al 61.8% Fibo su M15!")
        
        ULTIMI_SEGNALI = nuovi_segnali
        time.sleep(300) # Controlla ogni 5 minuti

@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Leandro Trading Dash</title>
        <meta http-equiv="refresh" content="60">
        <style>
            body { background: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
            table { margin: 20px auto; border-collapse: collapse; width: 90%; background: #1e1e1e; border-radius: 8px; overflow: hidden; }
            th, td { padding: 15px; text-align: left; border-bottom: 1px solid #333; }
            th { background: #333; color: #00ffcc; }
            .Bullish { color: #00ff00; font-weight: bold; }
            .Bearish { color: #ff4444; font-weight: bold; }
            .zona { background: #2e7d32; padding: 5px; border-radius: 4px; color: white; }
        </style>
    </head>
    <body>
        <h1 style="text-align:center;">📊 Dash Strategia H1-M15-M5</h1>
        <p style="text-align:center;">Ultimo aggiornamento: {{ ora }}</p>
        <table>
            <tr><th>Simbolo</th><th>Prezzo</th><th>Trend H1</th><th>Fibo 61.8% (M15)</th><th>Stato</th></tr>
            {% for s in segnali %}
            <tr>
                <td>{{ s.simbolo }}</td>
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
    return render_template_string(html, segnali=ULTIMI_SEGNALI, ora=datetime.now().strftime("%H:%M:%S"))

if __name__ == "__main__":
    threading.Thread(target=scanner, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
