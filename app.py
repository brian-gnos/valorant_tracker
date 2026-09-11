from flask import Flask, request
from dotenv import load_dotenv
from urllib.parse import quote
import requests
import os

load_dotenv()
app = Flask(__name__)

CHAVE = os.getenv("CHAVE")

def buscar_jogador(nick, tag):
    nick_url = quote(nick, safe = "")
    tag_url = quote(tag, safe="")
    url = f"https://api.henrikdev.xyz/valorant/v1/account/{nick_url}/{tag_url}"
    chave = {"Authorization": CHAVE}
    resposta = requests.get(url, headers=chave)
    return resposta.json()

def buscar_rank(nick, tag, regiao):
    nick_url = quote(nick, safe = "")
    tag_url = quote(tag, safe="")
    url = f"https://api.henrikdev.xyz/valorant/v2/mmr/{regiao}/{nick_url}/{tag_url}"
    chave = {"Authorization": CHAVE}
    return requests.get(url, headers=chave).json()

def buscar_partidas(nick, tag, regiao):
    nick_url = quote(nick, safe = "")
    tag_url = quote(tag, safe="")
    url = f"https://api.henrikdev.xyz/valorant/v3/matches/{regiao}/{nick_url}/{tag_url}?size=5"
    chave = {"Authorization": CHAVE}
    return requests.get(url, headers=chave).json()

def buscar_imagem_agente(nome_agente):
    url = "https://valorant-api.com/v1/agents?isPlayableCharacter=true"
    resposta = requests.get(url).json()
    for agente in resposta["data"]:
        if agente["displayName"].lower() == nome_agente.lower():
            return agente["displayIcon"]
    return ""

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
                if deaths != 0:
                    kda = (kills + assists)/deaths
                else:
                    kda = kills + assists
                if jogador in partida["players"]["red"]:
                    time = "red"
                else:
                    time = "blue"
                vencedor = partida["teams"][time]["has_won"]
                resultado = "VITÓRIA" if vencedor else "DERROTA"
                classe = "vitoria" if vencedor else "derrota"
                imagem = buscar_imagem_agente(agente)
                html += f"""
                <div class="partida {classe}">
                    <img src="{imagem}" width="40" height="40">
                    <span class="resultado">{resultado}</span>
                    <span>{mapa} | {modo}</span>
                    <span>{agente}</span>
                    <span>{kills}/{deaths}/{assists}</span>
                    <span>KDA: {kda:.2f}</span>
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

            form {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            h1 {  
                font-size: 3em; 
                margin-bottom: 20px; 
            }

            .valorant {
                color: #ff4655;
            }

            .tracker {
                color: #ffffff;
            }

            .tag-input {
                position: relative;
            }
            
            input {
                color: white;
                padding: 10px;
                margin: 5px;
                border: none;
                border-radius: 5px;
                font-size: 1em;
                background: #1f2f3d;
            }
            
            input:focus {
                outline: 2px solid #ff4655;
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
            
            button:hover { 
                background: #6B0000; 
            }
        </style>
    </head>
    <body>
        <h1>
            <span class="valorant">VALORANT</span>
            <span class="tracker">TRACKER</span>
        </h1>
        <form action="/buscar">
            <input type="text" name="nick" placeholder="Nick">
            <div class = "tag-input">
                <span>#</span>
                <input type="text" name="tag" placeholder="Tag">
            </div>
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
        info = conta["data"]

        if "errors" in conta:
            print(f"ERRO CONTA: {conta["errors"]}")
            return "Jogador não encontrado!"

        regiao = info["region"]

        rank = buscar_rank(nick, tag, regiao)
        mmr = rank["data"]
        if "errors" in rank:
            print(f"ERRO RANK: {rank["errors"]}")

        partidas = buscar_partidas(nick, tag, regiao)
        if "errors" in partidas:
            print(f"ERRO PARTIDA: {partidas["errors"]}")

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
                
                h1 {{ 
                    color: #ff4655; 
                }}
                
                p {{ 
                    font-size: 1.1em; 
                    margin: 8px 0; 
                }}
                
                a {{
                    color: #ff4655;
                    text-decoration: none;
                    margin-top: 10px;
                    display: inline-block;
                }}
                
                .partidas {{ 
                    width: 650px; 
                }}
                
                .partidas h2 {{ 
                    color: #ff4655;
                }}
                
                .partida {{
                    background: #1f2f3d;
                    padding: 12px 16px;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    display: flex;
                    justify-content: space-between;
                }}
                
                .partida.vitoria {{
                    border-left: 4px solid #2ecc71;
                }}
                
                .partida.derrota {{
                    border-left: 4px solid #e74c3c;
                }}
                
                .partida.vitoria .resultado {{
                    color: #2ecc71;
                    font-weight: bold;
                }}
                
                .partida.derrota .resultado {{
                    color: #e74c3c;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>{info['name']}#{info['tag']}</h1>
                <p>Nível: {info['account_level']}</p>
                <p>Região: {info['region'].upper()}</p>
                <p>Rank: {mmr['current_data']['currenttierpatched']}</p>
                <p>RR: {mmr['current_data']['ranking_in_tier']}</p>
                <a href="/">← Voltar</a>
            </div>
            <div class="partidas">
                <h2>Últimas 5 partidas</h2>
                {html_partidas}
            </div>
        </body>
        </html>
        """
    except Exception as e:
        import traceback
        traceback.print_exc()
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    background: #0f1923;
                    color: white;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 100px;
                }

                h1 {
                    color: #ff4655;
                }

                a {
                    color: #ff4655;
                }
            </style>
        </head>
        
        <body>
            <h1>Ocorreu um erro!</h1>
            <p>Tente novamente mais tarde</p>
            <a href="/">← Voltar</a>
        </body>
        </html>
        """

app.run()