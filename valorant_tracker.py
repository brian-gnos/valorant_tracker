import requests

CHAVE = "HDEV-445a1ee3-eeaa-4dfe-ac69-77b6bd33cfab"

def buscar_jogador(nick, tag):
    url = f"https://api.henrikdev.xyz/valorant/v1/account/{nick}/{tag}"
    chave = {"Authorization": CHAVE}
    resposta = requests.get(url, headers=chave)
    return resposta.json()

def buscar_rank(nick, tag):
    url = f"https://api.henrikdev.xyz/valorant/v2/mmr/na/{nick}/{tag}"
    chave = {"Authorization": CHAVE}
    resposta = requests.get(url, headers=chave)
    return resposta.json()

def buscar_partidas(nick, tag):
    url = f"https://api.henrikdev.xyz/valorant/v3/matches/na/{nick}/{tag}?size=5"
    chave = {"Authorization": CHAVE}
    resposta = requests.get(url, headers=chave)
    return resposta.json()

def mostrar_jogador(dados, rank):
    info = dados["data"]
    mmr = rank["data"]
    print("=== VALORANT TRACKER ===")
    print(f"Jogador : {info['name']}#{info['tag']}")
    print(f"Nível   : {info['account_level']}")
    print(f"Região  : {info['region'].upper()}")
    print(f"Rank    : {mmr['current_data']['currenttierpatched']}")
    print(f"RR      : {mmr['current_data']['ranking_in_tier']}")
    print(f"Último update: {info['last_update']}")

def mostrar_partidas(partidas, nick):
    print("\n=== ÚLTIMAS 5 PARTIDAS ===")
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
                print(f"{resultado} | {mapa} | {modo} | {agente} | {kills}/{deaths}/{assists}")

nick = input("Digite o nick: ")
tag = input("Digite a tag: ")

try:
    conta = buscar_jogador(nick, tag)
    rank = buscar_rank(nick, tag)
    partidas = buscar_partidas(nick, tag)
    mostrar_jogador(conta, rank)
    mostrar_partidas(partidas, nick)
except:
    print("Jogador não encontrado! Verifique o nick e a tag.")