from flask import Flask, request
from dotenv import load_dotenv
import requests
import os

load_dotenv()
app = Flask(__name__)

CHAVE = os.getenv("CHAVE")

def buscar_jogador(nick, tag):
    url = f"https://api.henrikdev.xyz/valorant/v1/account/{nick}/{tag}"
    chave = {"Authorization": CHAVE}
    return requests.get(url, headers=chave).json()

def buscar_rank(nick, tag):
    url = f"https://api.henrikdev.xyz/valorant/v2/mmr/na/{nick}/{tag}"
    chave = {"Authorization": CHAVE}
    return requests.get(url, headers=chave).json()

def buscar_partidas(nick, tag):
    url = f"https://api.henrikdev.xyz/valorant/v3/matches/na/{nick}/{tag}?size=5"
    chave = {"Authorization": CHAVE}
    return requests.get(url, headers=chave).json()

def montar_partidas(partidas, nick):
    html = ""
    for partida in partidas["data"]:
        mapa = partida["metadata"]["map"]
        modo = partida["metadata"]["mode"]
        for jogador in partida["players"]["all_players"]:
            if jogador["name"].lower() == nick.lower():
                agente = jogador["character"]
                kills = jogador["stats"]["kills"]
                deaths = jogador["stats"]["deaths"]
                assists = jogador["stats"]["assists"]
                time = jogador["team"].upper()
                vencedor = partida["teams"][time.lower()]["has_won"]
                resultado = "VITÓRIA" if vencedor else "DERROTA"
                classe = "vitoria" if vencedor else "derrota"
                html += f"""
                <div class="partida {classe}">
                    <span class="resultado">{resultado}</span>
                    <span>{mapa} | {modo}</span>
                    <span>{agente}</span>
                    <span>{kills}/{deaths}/{assists}</span>
                </div>
                """
    return html

@app.route("/")
def inicio():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Valorant Tracker</title>
        <style>
            body {
                background-color: #0f1923;
                color: white;
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            h1 { color: #ff4655; font-size: 3em; margin-bottom: 20px; }
            input {
                padding: 10px;
                margin: 5px;
                border: none;
                border-radius: 5px;
                background: #1f2f3d;
                color: white;
                font-size: 1em;
            }
            button {
                padding: 10px 20px;
                background: #ff4655;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 1em;
                cursor: pointer;
            }
            button:hover { background: #cc0011; }
        </style>
    </head>
    <body>
        <h1>VALORANT TRACKER 🎮</h1>
        <form action="/buscar">
            <input type="text" name="nick" placeholder="Nick">
            <input type="text" name="tag" placeholder="Tag">
            <button type="submit">Buscar</button>
        </form>
    </body>
    </html>
    """

@app.route("/buscar")
def buscar():
    nick = request.args.get("nick")
    tag = request.args.get("tag")
    try:
        conta = buscar_jogador(nick, tag)
        rank = buscar_rank(nick, tag)
        partidas = buscar_partidas(nick, tag)
        info = conta["data"]
        mmr = rank["data"]
        html_partidas = montar_partidas(partidas, nick)
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{info['name']}#{info['tag']}</title>
            <style>
                body {{
                    background-color: #0f1923;
                    color: white;
                    font-family: Arial, sans-serif;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding: 40px;
                    margin: 0;
                }}
                .card {{
                    background: #1f2f3d;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                    width: 400px;
                    margin-bottom: 20px;
                }}
                h1 {{ color: #ff4655; }}
                p {{ font-size: 1.1em; margin: 8px 0; }}
                a {{
                    color: #ff4655;
                    text-decoration: none;
                    margin-top: 10px;
                    display: inline-block;
                }}
                .partidas {{ width: 400px; }}
                .partidas h2 {{ color: #ff4655; }}
                .partida {{
                    background: #1f2f3d;
                    padding: 12px 16px;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    display: flex;
                    justify-content: space-between;
                }}
                .vitoria {{
                    border-left: 4px solid #2ecc71;
                }}
                .vitoria .resultado {{
                    color: #2ecc71;
                    font-weight: bold;
                }}
                .derrota {{
                    border-left: 4px solid #e74c3c;
                }}
                .derrota .resultado {{
                    color: #e74c3c;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>{info['name']}#{info['tag']}</h1>
                <p>🎮 Nível: {info['account_level']}</p>
                <p>🌍 Região: {info['region'].upper()}</p>
                <p>🏆 Rank: {mmr['current_data']['currenttierpatched']}</p>
                <p>⭐ RR: {mmr['current_data']['ranking_in_tier']}</p>
                <a href="/">← Voltar</a>
            </div>
            <div class="partidas">
                <h2>Últimas 5 partidas</h2>
                {html_partidas}
            </div>
        </body>
        </html>
        """
    except:
        return """
        <!DOCTYPE html>
        <html>
        <body style="background:#0f1923; color:white; font-family:Arial; text-align:center; padding:100px">
            <h1 style="color:#ff4655">Jogador não encontrado!</h1>
            <p>Verifique o nick e a tag e tente novamente.</p>
            <a href="/" style="color:#ff4655">← Voltar</a>
        </body>
        </html>
        """

app.run()