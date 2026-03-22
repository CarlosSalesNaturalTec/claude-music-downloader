---
name: music-download
description: >
  Orientação para download de áudio MP3 a partir de URLs do YouTube usando yt-dlp 2026.3.17.
  Use esta skill sempre que precisar baixar áudio de um vídeo do YouTube,
  converter para MP3, definir qualidade de áudio, sanitizar nome de arquivo,
  tratar erros de disponibilidade, geo-bloqueio ou dependências ausentes.
  Acione também quando o usuário mencionar "baixar música", "extrair áudio",
  "converter para mp3", "salvar áudio" ou qualquer variação de download de mídia.
---

# music-download

Skill para download de áudio MP3 do YouTube com qualidade consistente,
nomenclatura padronizada e tratamento robusto de erros.

**Versão do yt-dlp:** `2026.3.17`

---

## Script de execução

O script principal está em `~/.claude/skills/music-download/scripts/music_download.py`.
Sempre execute via bash capturando o JSON de saída.

```bash
python ~/.claude/skills/music-download/scripts/music_download.py "{video_id}" "{titulo_sanitizado}"
```

---

## Parâmetros de entrada

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `video_id` | string | ID do vídeo YouTube (ex: `dQw4w9WgXcQ`) |
| `titulo_sanitizado` | string | Nome do arquivo sem caracteres especiais |

---

## Sanitização do nome do arquivo

Antes de chamar o script, sanitize o título seguindo estas regras:

1. Remover caracteres proibidos no Windows: `\ / : * ? " < > |`
2. Substituir espaços por underscores
3. Converter para lowercase
4. Limitar a 80 caracteres
5. Garantir extensão `.mp3` no final

**Exemplos:**
```
"Aquarela - Toquinho (Official Audio)"  →  "aquarela_toquinho_official_audio.mp3"
"Hotel California (2013 Remaster)"      →  "hotel_california_2013_remaster.mp3"
"Clube da Esquina Nº 2"                 →  "clube_da_esquina_n_2.mp3"
```

---

## Configurações de qualidade

Use sempre estas flags do yt-dlp para garantir melhor qualidade de áudio:

```bash
--extract-audio
--audio-format mp3
--audio-quality 0        # melhor qualidade disponível (VBR)
--embed-thumbnail        # capa do álbum embutida no MP3
--add-metadata           # título, artista, álbum nos metadados ID3
```

---

## Pasta de destino

Sempre salve em pasta temporária:

```
Windows : C:\Users\SeuUsuario\AppData\Local\Temp\musicas\
Linux/Mac: /tmp/musicas/
```

O script cria a pasta automaticamente se não existir.

---

## Formato de saída esperado do script

Sucesso:
```json
{
  "status": "success",
  "arquivo": "C:\\Users\\SeuUsuario\\AppData\\Local\\Temp\\musicas\\aquarela_toquinho.mp3",
  "titulo": "Aquarela - Toquinho",
  "tamanho_mb": 4.2,
  "duracao": "4:32",
  "qualidade": "mp3 VBR q0"
}
```

Falha:
```json
{
  "status": "error",
  "codigo": "VIDEO_UNAVAILABLE",
  "mensagem": "Vídeo não disponível nesta região."
}
```

---

## Erros comuns e como tratar

| Código | Causa | Ação |
|---|---|---|
| `VIDEO_UNAVAILABLE` | Vídeo removido ou privado | Tentar próximo resultado da busca |
| `GEO_RESTRICTED` | Bloqueio regional | Informar usuário, sugerir VPN |
| `YTDLP_NOT_FOUND` | yt-dlp não instalado | Executar `pip install yt-dlp --break-system-packages` e repetir |
| `FFMPEG_NOT_FOUND` | ffmpeg ausente (necessário para conversão) | Orientar instalação do ffmpeg |
| `DISK_FULL` | Sem espaço em disco | Informar usuário |
| `NETWORK_ERROR` | Falha de conexão | Retentar 1x após 5 segundos |

---

## Verificação de dependências

Antes do primeiro download, confirme que ambas estão instaladas:

```bash
# yt-dlp
pip install yt-dlp --break-system-packages

# ffmpeg (necessário para conversão para MP3)
# Windows: baixar em https://ffmpeg.org/download.html
#          e adicionar ao PATH
# ou via winget:
winget install ffmpeg
```

---

## Dependências Python

```bash
pip install yt-dlp==2026.3.17 python-dotenv --break-system-packages
```

---

Consulte `scripts/music_download.py` para o script completo de execução.
