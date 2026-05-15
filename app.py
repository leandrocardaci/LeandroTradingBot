import os
from flask import Flask, render_template_string
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURAZIONE ---
TOKEN = "8643519947:AAH2Ba92mhson8uQAij_5Q0N0PvyTgluhAU"
CHAT_ID = "6511237453"
SIMBOLI = ["EURUSD=X", "GBPUSD=X", "USDJPY=X"] 

def calcola_singolo(simbolo):
    try:
        df = yf.download(simbolo, period="5d", interval="1h", progress=False)
        if df.empty: return None
        prezzo = float(df['Close'].iloc[-1])
        sma20 = float(df['Close'].rolling(window=20).mean().iloc[-1])
        trend = "Bullish" if prezzo > sma20 else "Bearish"
        alto, basso = float(df['High'].max()), float(df['Low'].min())
        fibo = alto - (0.618 * (alto - basso)) if trend == "Bullish" else basso + (0.618 * (alto - basso))
        stato = "In Zona" if abs(prezzo - fibo) < (prezzo * 0.0005) else "Monitoraggio"
        return {"simbolo": simbolo.replace("=X", ""), "prezzo": round(prezzo, 5), "trend": trend, "fibo": round(fibo, 5), "stato": stato}
    except: return None

@app.route('/')
def home():
    # Il bot lavora SOLO quando carichi la pagina: niente blocchi di Render!
    risultati = []
    for s in SIMBOLI:
        res = calcola_singolo(s)
        if res: risultati.append(res)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Leandro Dash</title>
        <meta http-equiv="refresh" content="60">
        <style>
            body { background: #121212; color: white; font-family: sans-serif; text-align: center; }
            table { margin: 20px auto; border-collapse: collapse; width: 80%; background: #1e1e1e; }
            th, td { padding: 12px; border: 1px solid #333; }
            .Bullish { color: #00ff00; } .Bearish { color: #ff4444; }
        </style>
    </head>
    <body>
        <h1>📊 Dashboard Real-Time</h1>
        <p>Ultimo controllo: {{ ora }}</p>
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
