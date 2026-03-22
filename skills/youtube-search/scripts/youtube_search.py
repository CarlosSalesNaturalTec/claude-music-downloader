#!/usr/bin/env python3
"""
youtube_search.py
Busca músicas no YouTube via Data API v3 e retorna JSON ranqueado.
Uso: python youtube_search.py "Aquarela Toquinho"
"""

import sys
import json
import os
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ── Configuração ─────────────────────────────────────────────────────────────

API_KEY = os.environ.get("YOUTUBE_API_KEY")
MAX_RESULTS = 5

# ── Helpers ───────────────────────────────────────────────────────────────────

def montar_query(input_usuario: str) -> str:
    """Monta query otimizada para busca de música oficial."""
    texto = input_usuario.strip()
    if not texto:
        raise ValueError("Query vazia.")
    query = f"{texto} official audio"
    return query[:80]


def parsear_duracao(iso_duracao: str) -> str:
    """Converte PT4M32S → '4:32'."""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duracao)
    if not match:
        return "?"
    horas = int(match.group(1) or 0)
    minutos = int(match.group(2) or 0)
    segundos = int(match.group(3) or 0)
    if horas:
        return f"{horas}:{minutos:02d}:{segundos:02d}"
    return f"{minutos}:{segundos:02d}"


def duracao_em_segundos(iso_duracao: str) -> int:
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duracao)
    if not match:
        return 0
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    return h * 3600 + m * 60 + s


def calcular_score(titulo: str, canal: str, segundos: int) -> str:
    """
    Pontua relevância do resultado.
    Retorna 'alto', 'medio' ou 'baixo'.
    """
    pontos = 0
    titulo_lower = titulo.lower()
    canal_lower = canal.lower()

    # Título tem indicadores de versão oficial
    if any(p in titulo_lower for p in ["official audio", "official music", "letra", "lyric"]):
        pontos += 3

    # Canal é VEVO ou gravadora conhecida
    if any(p in canal_lower for p in ["vevo", "records", "music", "som livre", "universal", "sony", "warner"]):
        pontos += 3

    # Duração típica de estúdio (2~7 min)
    if 120 <= segundos <= 420:
        pontos += 2
    elif 420 < segundos <= 900:
        pontos += 1

    # Penaliza covers, ao vivo, karaokê
    if any(p in titulo_lower for p in ["cover", "karaok", "instrumental", "tribute", "ao vivo", "live", "remix"]):
        pontos -= 3

    if pontos >= 5:
        return "alto"
    elif pontos >= 2:
        return "medio"
    return "baixo"


# ── Busca principal ───────────────────────────────────────────────────────────

def buscar_musica(input_usuario: str) -> dict:
    if not API_KEY:
        return {
            "status": "error",
            "erro": "YOUTUBE_API_KEY não configurada no ambiente.",
            "resultados": []
        }

    query = montar_query(input_usuario)

    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)

        # Busca ids
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=MAX_RESULTS,
            type="video",
            videoCategoryId="10"  # categoria Música
        ).execute()

        ids = [item["id"]["videoId"] for item in search_response.get("items", [])]

        if not ids:
            return {"status": "not_found", "resultados": []}

        # Busca detalhes (duração, etc.)
        videos_response = youtube.videos().list(
            part="contentDetails,snippet",
            id=",".join(ids)
        ).execute()

        resultados = []
        for i, item in enumerate(videos_response.get("items", []), start=1):
            vid_id = item["id"]
            titulo = item["snippet"]["title"]
            canal = item["snippet"]["channelTitle"]
            iso_dur = item["contentDetails"]["duration"]
            duracao = parsear_duracao(iso_dur)
            segundos = duracao_em_segundos(iso_dur)
            score = calcular_score(titulo, canal, segundos)

            resultados.append({
                "posicao": i,
                "video_id": vid_id,
                "titulo": titulo,
                "canal": canal,
                "duracao": duracao,
                "url": f"https://youtube.com/watch?v={vid_id}",
                "score": score
            })

        # Ordena: alto > medio > baixo, mantendo posição original como desempate
        ordem = {"alto": 0, "medio": 1, "baixo": 2}
        resultados.sort(key=lambda r: (ordem[r["score"]], r["posicao"]))

        # Reatribui posição após ordenação
        for i, r in enumerate(resultados, start=1):
            r["posicao"] = i

        return {"status": "found", "query_usada": query, "resultados": resultados}

    except HttpError as e:
        erro = json.loads(e.content).get("error", {})
        return {
            "status": "error",
            "erro": erro.get("message", str(e)),
            "codigo": erro.get("code"),
            "resultados": []
        }
    except Exception as e:
        return {"status": "error", "erro": str(e), "resultados": []}


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "erro": "Informe o nome da música.", "resultados": []}))
        sys.exit(1)

    input_usuario = " ".join(sys.argv[1:])
    resultado = buscar_musica(input_usuario)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
