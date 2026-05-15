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

# Lista simboli ottimizzata per evitare blocchi
SIMBOLI = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X",
    "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "EURGBP=X", "EURAUD=X", "GBPAUD=X", "EURCAD=X"
] 
ULTIMI_SEGNALI = []

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={messaggio}&parse_mode=Markdown"
    try:
        requests.get(url, timeout=10)
    except:
        pass

def calcola_fibo_e_trend(simbolo):
    try:
        # 1. Trend su H1 (Montagna) - Prendiamo 5 giorni per sicurezza
        data_h1 = yf.download(simbolo, period="5d", interval="1h", progress=False)
        if data_h1.empty or len(data_h1) < 20:
            return None
        
        prezzo_attuale = float(data_h1['Close'].iloc[-1])
        sma20_h1 = float(data_h1['Close'].rolling(window=20).mean().iloc[-1])
        trend = "Bullish" if prezzo_attuale > sma20_h1 else "Bearish"

        # 2. Fibonacci su M15
        data_m15 = yf.download(simbolo, period="2d", interval="15m", progress=False)
        if data_m15.empty:
            return None
            
        alto = float(data_m15['High'].max())
        basso = float(data_m15['Low'].min())
        diff = alto - basso
        
        # Livello 61.8%
        if trend == "Bullish":
            fibo_618 = alto - (0.618 * diff)
        else:
            fibo_618 = basso + (0.618 * diff)
        
        # Calcolo vicinanza (se il prezzo è entro lo 0.05% dal livello)
        distanza = abs(prezzo_attuale - fibo_618)
        soglia = prezzo_attuale * 0.0005 
        stato = "In Zona" if distanza < soglia else "Monitoraggio"
        
        return {
            "simbolo": simbolo.replace("=X", ""),
            "prezzo": round(prezzo_attuale, 5),
            "trend": trend,
            "fibo": round(fibo_618, 5),
            "stato": stato
        }
    except Exception as e:
        print(f"Errore tecnico su {simbolo}: {e}")
        return None

def scanner():
    global ULTIMI_SEGNALI
    while True:
        nuovi_segnali = []
        print(f"Inizio scansione: {datetime.now()}")
        
        for s in SIMBOLI:
            risultato = calcola_fibo_e_trend(s)
            if risultato:
                nuovi_segnali.append(risultato)
                if risultato["stato"] == "In Zona":
                    invia_telegram(f"⚠️ *ALERT ZONA*: {risultato['simbolo']} vicino al 61.8% Fibo su M15!")
            
            # Aspetta 2 secondi tra un simbolo e l'altro per non farsi bloccare da Yahoo
            time.sleep(2) 
        
        if nuovi_segnali:
            ULTIMI_SEGNALI = nuovi_segnali
        
        print(f"Scansione completata. Trovati {len(nuovi_segnali)} simboli.")
        # Aspetta 5 minuti prima della prossima scansione totale
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
            body { background: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; }
            h1 { color: #00ffcc; text-shadow: 2px 2px #000; }
            table { margin: 20px auto; border-collapse: collapse; width: 95%; background: #1e1e1e; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }
            th, td { padding: 12px; text-align: center; border-bottom: 1px solid #333; }
            th { background: #333; color: #00ffcc; text-transform: uppercase; font-size: 14px; }
            tr:hover { background: #252525; }
            .Bullish { color: #00ff00; font-weight: bold; }
            .Bearish { color: #ff4444; font-weight: bold; }
            .zona { background: #c62828; color: white; padding: 5px 10px; border-radius: 4px; animation: blink 1s infinite; }
            @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }
            .info { color: #888; font-size: 0.9em; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1 style="text-align:center;">📊 Dash Strategia H1-M15-M5</h1>
        <div class="info" style="text-align:center;">
            Aggiornato: {{ ora }} | Stato: Operativo | Scan ogni 5 min
        </div>
        <table>
            <tr><th>Simbolo</th><th>Prezzo Attuale</th><th>Trend (H1)</th><th>Fibo 61.8% (M15)</th><th>Stato Operativo</th></tr>
            {% if segnali %}
                {% for s in segnali %}
                <tr>
                    <td><strong>{{ s.simbolo }}</strong></td>
                    <td>{{ s.prezzo }}</td>
                    <td class="{{ s.trend }}">{{ s.trend }}</td>
                    <td>{{ s.fibo }}</td>
                    <td><span class="{{ 'zona' if s.stato == 'In Zona' else '' }}">{{ s.stato }}</span></td>
                </tr>
                {% endfor %}
            {% else %}
                <tr><td colspan="5" style="padding: 50px;">Caricamento dati in corso... Attendere 60 secondi.</td></tr>
            {% endif %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html, segnali=ULTIMI_SEGNALI, ora=datetime.now().strftime("%H:%M:%S"))

if __name__ == "__main__":
    # Avvio scanner
    t = threading.Thread(target=scanner, daemon=True)
    t.start()
    
    # Avvio Web Server
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
