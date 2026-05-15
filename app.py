import os
from flask import Flask, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURAZIONE ---
TOKEN = "8643519947:AAH2Ba92mhson8uQAij_5Q0N0PvyTgluhAU"
CHAT_ID = "6511237453"
# Usiamo solo EURUSD per testare se il tubo si sblocca
SIMBOLI = ["EURUSD", "GBPUSD", "USDJPY"]

def prendi_prezzo(simbolo):
    try:
        # Usiamo un servizio alternativo (ExchangeRate-API) molto leggero
        url = f"https://open.er-api.com/v6/latest/USD"
        data = requests.get(url, timeout=10).json()
        
        if data['result'] == 'success':
            tasso = data['rates'][simbolo[:3]]
            # Se siamo qui, il dato è passato!
            prezzo = 1 / tasso if simbolo == "EURUSD" or simbolo == "GBPUSD" else tasso
            
            return {
                "simbolo": simbolo,
                "prezzo": round(prezzo, 5),
                "trend": "Analisi...",
                "fibo": "Calcolo...",
                "stato": "Dato Ricevuto ✅"
            }
    except Exception as e:
        return None

@app.route('/')
def home():
    risultati = []
    for s in SIMBOLI:
        res = prendi_prezzo(s)
        if res: risultati.append(res)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Leandro Dash</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding-top: 50px; }
            table { margin: 20px auto; border-collapse: collapse; width: 80%; background: #1e1e1e; border: 2px solid #00ffcc; }
            th, td { padding: 15px; border: 1px solid #333; }
            th { background: #333; color: #00ffcc; }
        </style>
    </head>
    <body>
        <h1>📊 TEST CONNESSIONE DATI</h1>
        <p>Ora Server: {{ ora }}</p>
        {% if segnali %}
            <table>
                <tr><th>Simbolo</th><th>Prezzo</th><th>Trend</th><th>Fibo</th><th>Stato</th></tr>
                {% for s in segnali %}
                <tr>
                    <td>{{ s.simbolo }}</td>
                    <td>{{ s.prezzo }}</td>
                    <td>{{ s.trend }}</td>
                    <td>{{ s.fibo }}</td>
                    <td style="color: #00ff00;">{{ s.stato }}</td>
                </tr>
                {% endfor %}
            </table>
        {% else %}
            <h2 style="color: #ff4444;">ERRORE: I dati sono ancora bloccati dal server.</h2>
            <p>Se vedi questo, dobbiamo cambiare strategia e lanciarlo dal tuo PC.</p>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html, segnali=risultati, ora=datetime.now().strftime("%H:%M:%S"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
