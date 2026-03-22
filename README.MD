# 🎵 claude-music-downloader

Workflow de download de músicas via WhatsApp integrado ao Claude Code.
O usuário envia o nome de uma música, o sistema busca no YouTube e faz o download em MP3.

---

## Arquitetura

```
Usuário WhatsApp
      ↓ "baixa Aquarela do Toquinho"
Gateway WhatsApp (Baileys)
      ↓ detecta intenção
Claude Code CLI
      ↓ executa /baixar-musica
      ├── youtube_search.py   → busca no YouTube
      └── music_download.py   → download via yt-dlp
            ↓
      Arquivo MP3 em /tmp/musicas/ → Usuário WhatsApp
```

---

## Pré-requisitos

### Sistema
- Python 3.10+
- Node.js 18+
- ffmpeg

### Windows
```bash
winget install ffmpeg
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install -y ffmpeg
```

### Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

---

## Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seuusuario/claude-music-downloader.git
cd claude-music-downloader
```

### 2. Instale as dependências Python
```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

Edite o `.env` com suas chaves:
```env
ANTHROPIC_API_KEY=sua_chave_anthropic
YOUTUBE_API_KEY=sua_chave_youtube
```

### 4. Copie os arquivos para o Claude Code

**Windows:**
```bash
# Slash commands
copy commands\baixar-musica.md %USERPROFILE%\.claude\commands\
copy commands\baixar-playlist.md %USERPROFILE%\.claude\commands\

# Skills (inclui scripts dentro de cada skill)
xcopy /E /I skills %USERPROFILE%\.claude\skills
```

**Linux/Mac:**
```bash
# Slash commands
cp commands/* ~/.claude/commands/

# Skills (inclui scripts dentro de cada skill)
cp -r skills/* ~/.claude/skills/
```

---

## Obter chaves de API

### Anthropic API Key
1. Acesse [console.anthropic.com](https://console.anthropic.com)
2. Vá em **API Keys → Create Key**
3. Copie e cole no `.env`

### YouTube Data API v3
1. Acesse [console.cloud.google.com](https://console.cloud.google.com)
2. Crie um projeto ou selecione um existente
3. Vá em **APIs e Serviços → Biblioteca**
4. Busque `YouTube Data API v3` e ative
5. Vá em **Credenciais → Criar credencial → Chave de API**
6. Copie e cole no `.env`

---

## Uso

### Música única
```
/baixar-musica Aquarela Toquinho
/baixar-musica Hotel California Eagles
/baixar-musica Clube da Esquina
```

### Playlist
```
/baixar-playlist
Aquarela Toquinho
Hotel California Eagles
Clube da Esquina Milton Nascimento
```

---

## Estrutura do repositório

```
claude-music-downloader/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── commands/                        ← slash commands do Claude Code
│   ├── baixar-musica.md             ← workflow música única
│   └── baixar-playlist.md           ← workflow playlist com agentes paralelos
│
└── skills/                          ← skills do Claude Code (scripts dentro de cada skill)
    ├── youtube-search/
    │   ├── SKILL.md                 ← busca e avaliação de resultados
    │   └── scripts/
    │       └── youtube_search.py   ← integração YouTube Data API v3
    ├── music-download/
        ├── SKILL.md                 ← download via yt-dlp
        └── scripts/
            └── music_download.py   ← download e conversão MP3
    
```

---

## Testando isoladamente

Antes de usar o workflow completo, valide cada script individualmente:

### Testar busca no YouTube
```bash
python skills/youtube-search/scripts/youtube_search.py "Aquarela Toquinho"
```

Saída esperada:
```json
{
  "status": "found",
  "query_usada": "Aquarela Toquinho official audio",
  "resultados": [
    {
      "posicao": 1,
      "video_id": "abc123",
      "titulo": "Aquarela - Toquinho (Official Audio)",
      "canal": "ToquinhoVEVO",
      "duracao": "4:32",
      "score": "alto"
    }
  ]
}
```

### Testar download MP3
```bash
python skills/music-download/scripts/music_download.py "VIDEO_ID" "aquarela_toquinho"
```

Saída esperada:
```json
{
  "status": "success",
  "arquivo": "C:\\Users\\...\\Temp\\musicas\\aquarela_toquinho.mp3",
  "titulo": "Aquarela - Toquinho",
  "tamanho_mb": 4.2,
  "duracao": "4:32",
  "qualidade": "mp3 VBR q0"
}
```

### Testar workflow completo no Claude Code
```bash
claude
/baixar-musica Aquarela Toquinho
```

---

## Integração WhatsApp (Baileys)

Para integrar com o Baileys em uma VM, consulte a seção de integração
no arquivo [`docs/baileys-integration.md`](docs/baileys-integration.md).

---

## Troubleshooting

### `YOUTUBE_API_KEY não configurada`
Verifique se o `.env` está na home do usuário e se `python-dotenv` está instalado.

### `yt-dlp not found`
```bash
pip install yt-dlp --break-system-packages
```

### `ffmpeg not found`
```bash
# Windows
winget install ffmpeg

# Linux
sudo apt-get install -y ffmpeg
```

### Vídeo indisponível ou geo-bloqueado
O workflow tentará automaticamente o próximo resultado da busca.
Se todos falharem, tente reformular o pedido com mais detalhes.

### yt-dlp com erro após atualização do YouTube
```bash
pip install -U yt-dlp
```

---

## Roadmap

- [ ] Integração completa com Baileys (WhatsApp)
- [ ] Suporte a download de playlists do YouTube
- [ ] Upload opcional para bucket no GCP
- [ ] Notificação de progresso em tempo real no WhatsApp
- [ ] Suporte a outros formatos além de MP3 (FLAC, WAV)

---

## Licença

MIT
