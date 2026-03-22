#!/usr/bin/env python3
"""
music_download.py
Faz download de áudio MP3 do YouTube via yt-dlp.
Uso: python music_download.py "VIDEO_ID" "nome_do_arquivo"
"""

import sys
import json
import os
import re
import time
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env da home do usuário
load_dotenv(os.path.join(os.path.expanduser("~"), ".env"))

# ── Configuração ──────────────────────────────────────────────────────────────

def pasta_destino() -> Path:
    """Retorna pasta temporária para salvar os MP3s."""
    if sys.platform == "win32":
        base = Path(os.environ.get("TEMP", "C:/Users/Public/Temp"))
    else:
        base = Path("/tmp")
    pasta = base / "musicas"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def sanitizar_nome(titulo: str) -> str:
    """
    Sanitiza título para uso seguro como nome de arquivo no Windows e Linux.
    """
    # Remove caracteres proibidos no Windows
    nome = re.sub(r'[\\/:*?"<>|]', "", titulo)
    # Substitui espaços e traços por underscore
    nome = re.sub(r"[\s\-]+", "_", nome)
    # Remove caracteres não-ASCII problemáticos
    nome = re.sub(r"[^\w.]", "", nome, flags=re.UNICODE)
    # Lowercase
    nome = nome.lower()
    # Remove underscores duplicados
    nome = re.sub(r"_+", "_", nome).strip("_")
    # Limita tamanho
    nome = nome[:80]
    return nome


# ── Download ──────────────────────────────────────────────────────────────────

def baixar_mp3(video_id: str, titulo_param: str) -> dict:
    """
    Faz download do áudio e converte para MP3 via yt-dlp.
    Retorna dict com status e detalhes.
    """

    # Verifica se yt-dlp está instalado
    try:
        import yt_dlp
    except ImportError:
        return {
            "status": "error",
            "codigo": "YTDLP_NOT_FOUND",
            "mensagem": "yt-dlp não está instalado. Execute: pip install yt-dlp --break-system-packages"
        }

    url = f"https://www.youtube.com/watch?v={video_id}"
    pasta = pasta_destino()
    nome_sanitizado = sanitizar_nome(titulo_param)
    caminho_saida = pasta / f"{nome_sanitizado}.mp3"

    # Opções do yt-dlp
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",  # VBR melhor qualidade
            },
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
            {
                "key": "EmbedThumbnail",
            },
        ],
        "outtmpl": str(pasta / f"{nome_sanitizado}.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "writethumbnail": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extrai informações antes do download
            info = ydl.extract_info(url, download=False)
            titulo_real = info.get("title", titulo_param)
            duracao_seg = info.get("duration", 0)
            minutos = duracao_seg // 60
            segundos = duracao_seg % 60
            duracao_fmt = f"{minutos}:{segundos:02d}"

            # Executa o download
            ydl.download([url])

        # Verifica se o arquivo foi gerado
        if not caminho_saida.exists():
            # yt-dlp às vezes gera com nome diferente — procura o mais recente
            arquivos = sorted(pasta.glob(f"{nome_sanitizado}*.mp3"), key=os.path.getmtime, reverse=True)
            if arquivos:
                caminho_saida = arquivos[0]
            else:
                return {
                    "status": "error",
                    "codigo": "FILE_NOT_GENERATED",
                    "mensagem": "Download concluído mas arquivo MP3 não encontrado."
                }

        tamanho_mb = round(caminho_saida.stat().st_size / (1024 * 1024), 2)

        return {
            "status": "success",
            "arquivo": str(caminho_saida),
            "titulo": titulo_real,
            "tamanho_mb": tamanho_mb,
            "duracao": duracao_fmt,
            "qualidade": "mp3 VBR q0"
        }

    except yt_dlp.utils.DownloadError as e:
        mensagem = str(e)

        if "Video unavailable" in mensagem or "unavailable" in mensagem.lower():
            codigo = "VIDEO_UNAVAILABLE"
            msg_amigavel = "Vídeo indisponível ou removido do YouTube."
        elif "geo" in mensagem.lower() or "not available in your country" in mensagem.lower():
            codigo = "GEO_RESTRICTED"
            msg_amigavel = "Vídeo bloqueado na sua região."
        elif "ffmpeg" in mensagem.lower():
            codigo = "FFMPEG_NOT_FOUND"
            msg_amigavel = "ffmpeg não encontrado. Instale via: winget install ffmpeg"
        elif "network" in mensagem.lower() or "connection" in mensagem.lower():
            # Retentar uma vez
            time.sleep(5)
            return baixar_mp3(video_id, titulo_param)
        else:
            codigo = "DOWNLOAD_ERROR"
            msg_amigavel = mensagem

        return {
            "status": "error",
            "codigo": codigo,
            "mensagem": msg_amigavel
        }

    except OSError as e:
        if e.errno == 28:  # No space left on device
            return {
                "status": "error",
                "codigo": "DISK_FULL",
                "mensagem": "Sem espaço em disco disponível."
            }
        return {
            "status": "error",
            "codigo": "OS_ERROR",
            "mensagem": str(e)
        }

    except Exception as e:
        return {
            "status": "error",
            "codigo": "UNKNOWN_ERROR",
            "mensagem": str(e)
        }


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({
            "status": "error",
            "codigo": "INVALID_ARGS",
            "mensagem": "Uso: python music_download.py VIDEO_ID TITULO"
        }))
        sys.exit(1)

    video_id = sys.argv[1].strip()
    titulo = " ".join(sys.argv[2:]).strip()

    resultado = baixar_mp3(video_id, titulo)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
