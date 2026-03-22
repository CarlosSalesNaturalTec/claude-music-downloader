# /baixar-musica

Você é o orquestrador do workflow de download de música. Execute as etapas abaixo em sequência, parando imediatamente se qualquer etapa falhar.

## Input

O usuário fornecerá o nome da música e opcionalmente o artista:
- Formato simples: `$ARGUMENTS`
- Exemplos: "Aquarela Toquinho", "Hotel California", "Clube da Esquina Milton Nascimento"

Se `$ARGUMENTS` estiver vazio, pergunte ao usuário o nome da música antes de prosseguir.

---

## Etapa 1 — Busca no YouTube

Consulte a skill `youtube-search` para orientação, depois execute:

```bash
python ~/.claude/skills/youtube-search/scripts/youtube_search.py "$ARGUMENTS"
```

**Resultado esperado:** JSON com os 3 resultados mais relevantes contendo `video_id`, `titulo`, `canal`, `duracao`.

**Decisão:**
- Se encontrar 1 resultado claramente correto (título + artista batem) → prossiga automaticamente
- Se houver ambiguidade (covers, versões ao vivo, múltiplos artistas) → apresente as opções ao usuário e aguarde escolha
- Se nenhum resultado relevante → informe o usuário e encerre

---

## Etapa 2 — Download do MP3

Consulte a skill `music-download` para orientação, depois execute com o `video_id` escolhido:

```bash
python ~/.claude/skills/music-download/scripts/music_download.py "{video_id}" "{titulo_sanitizado}"
```

**Resultado esperado:** caminho absoluto do arquivo `.mp3` gerado em `/tmp/musicas/`.

**Decisão:**
- Se download concluído com sucesso → prossiga
- Se erro de disponibilidade ou geo-bloqueio → informe o usuário, ofereça tentar próximo resultado da busca
- Se erro de dependência (yt-dlp não instalado) → execute `pip install yt-dlp --break-system-packages` e tente novamente

---

## Etapa 3 — Upload para o Google Drive

Consulte a skill `gdrive-upload` para orientação, depois use o MCP do Google Drive para:

1. Verificar se a pasta `Músicas/` existe no Drive; se não existir, criá-la
2. Fazer upload do arquivo MP3 para essa pasta
3. Obter o link compartilhável do arquivo

**Decisão:**
- Se upload concluído → prossiga para o relatório final
- Se erro de autenticação MCP → oriente o usuário a reconectar o Google Drive nas configurações
- Se erro de espaço → informe o usuário

---

## Etapa 4 — Relatório Final

Ao concluir com sucesso, responda neste formato:

```
✅ Download concluído!

🎵 Música : {titulo completo}
👤 Canal   : {canal do YouTube}
⏱️  Duração : {duracao}
📁 Drive   : {link do arquivo no Google Drive}
```

Se qualquer etapa falhou, informe claramente qual etapa, o erro encontrado e o que o usuário pode fazer para resolver.

---

## Regras gerais

- Não pule etapas nem assuma sucesso sem verificar o output de cada script
- Sempre sanitize o nome do arquivo antes de salvar (remover caracteres especiais, limitar a 100 chars)
- Prefira versão de estúdio a versões ao vivo, salvo instrução contrária do usuário
- Registre erros detalhados no terminal mas apresente mensagens amigáveis ao usuário
