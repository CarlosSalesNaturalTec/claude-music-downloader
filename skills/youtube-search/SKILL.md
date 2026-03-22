---
name: youtube-search
description: >
  Orientação para busca de músicas no YouTube via YouTube Data API v3.
  Use esta skill sempre que precisar localizar um vídeo de música no YouTube
  a partir de um nome de faixa ou artista, avaliar relevância dos resultados,
  lidar com ambiguidades (covers, versões ao vivo, remixes) e selecionar
  o resultado mais adequado para download. Acione também quando o usuário
  mencionar "procurar música", "encontrar no YouTube", "qual é o link", ou
  qualquer busca de áudio/vídeo musical.
---

# youtube-search

Skill para localizar músicas no YouTube com alta precisão, priorizando
versões oficiais e de estúdio, e tratando corretamente ambiguidades.

---

## Script de execução

O script principal está em `~/.claude/skills/youtube-search/scripts/youtube_search.py`.
Sempre execute-o via bash e capture o JSON de saída.

```bash
python ~/.claude/skills/youtube-search/scripts/youtube_search.py "QUERY"
```

---

## Como construir a query de busca

A query deve ser montada de forma inteligente a partir do input do usuário.

**Regras de montagem:**

1. Se o usuário forneceu artista + música → `"{musica} {artista} official audio"`
2. Se forneceu só o nome da música → `"{musica} official audio"`
3. Nunca inclua palavras como "download", "mp3", "baixar" na query
4. Limite a query a 80 caracteres

**Exemplos:**
```
Input: "Aquarela Toquinho"
Query: "Aquarela Toquinho official audio"

Input: "Hotel California"
Query: "Hotel California official audio"

Input: "Clube da Esquina Milton Nascimento"
Query: "Clube da Esquina Milton Nascimento official audio"
```

---

## Critérios de avaliação dos resultados

Para cada resultado retornado pela API, avalie os seguintes critérios
em ordem de prioridade:

### 1. Relevância do título (peso alto)
- ✅ Título contém nome da música E nome do artista
- ✅ Palavras "official audio", "official music video", "letra", "lyric"
- ⚠️  Título contém só a música sem o artista (pode ser cover)
- ❌ Título contém "cover", "karaokê", "instrumental", "tribute"

### 2. Credibilidade do canal (peso alto)
- ✅ Canal verificado (nome do artista ou gravadora conhecida)
- ✅ Canal com sufixo "VEVO", "Records", "Music"
- ⚠️  Canal genérico sem verificação
- ❌ Canal com nome suspeito ou não relacionado ao artista

### 3. Duração (peso médio)
- ✅ Entre 2:00 e 7:00 minutos → provável versão de estúdio
- ⚠️  Entre 7:00 e 15:00 → pode ser versão ao vivo ou extended
- ❌ Acima de 15:00 → provavelmente compilação ou show completo

### 4. Preferência de formato
- Preferir "official audio" sobre "official music video"
- Preferir versão de estúdio sobre versão ao vivo
- Salvo instrução explícita do usuário em contrário

---

## Tomada de decisão após busca

### Caso A — Resultado claro (prosseguir automaticamente)
Critérios: resultado #1 tem título + artista corretos, canal credível, duração normal.
→ Selecione automaticamente e informe o usuário qual foi escolhido.

### Caso B — Ambiguidade (aguardar escolha do usuário)
Ocorre quando:
- Existem múltiplas versões plausíveis (estúdio, ao vivo, acústica)
- O artista não foi especificado e há covers relevantes
- Os 3 primeiros resultados são de canais diferentes sem clara hierarquia

Apresente as opções neste formato:
```
Encontrei 3 versões. Qual você prefere?

1. "Aquarela" - Toquinho (Canal: ToquinhoVEVO | 4:32 | Official Audio)
2. "Aquarela" - Toquinho ao vivo no Olympia (Canal: SomLivre | 6:14 | Show)
3. "Aquarela" - cover por João Silva (Canal: joaoviolao | 3:58)
```

### Caso C — Nenhum resultado relevante
Ocorre quando nenhum dos 3 resultados contém o nome da música no título.
→ Informe o usuário e sugira reformular o pedido com mais detalhes.

---

## Formato de saída esperado do script

O script `youtube_search.py` deve retornar JSON neste formato:

```json
{
  "status": "found",
  "resultados": [
    {
      "posicao": 1,
      "video_id": "abc123xyz",
      "titulo": "Aquarela - Toquinho (Official Audio)",
      "canal": "ToquinhoVEVO",
      "duracao": "4:32",
      "url": "https://youtube.com/watch?v=abc123xyz",
      "score": "alto"
    }
  ]
}
```

Se nenhum resultado relevante: `{ "status": "not_found", "resultados": [] }`

---

## Erros comuns e como tratar

| Erro | Causa provável | Ação |
|---|---|---|
| `quotaExceeded` | Limite diário da API atingido | Informe o usuário, sugira tentar amanhã |
| `keyInvalid` | API key inválida ou não configurada | Oriente configurar `YOUTUBE_API_KEY` no ambiente |
| `videoNotFound` | ID retornado mas vídeo removido | Tente o próximo resultado da lista |
| Timeout | Conexão lenta | Retentar 1x antes de reportar erro |

---

## Dependências e configuração

- **YouTube Data API v3** — requer chave de API configurada como variável de ambiente:
  ```bash
  export YOUTUBE_API_KEY="sua_chave_aqui"
  ```
- **Biblioteca Python:** `google-api-python-client`
  ```bash
  pip install google-api-python-client --break-system-packages
  ```

Consulte `references/youtube_search.py` para o script completo de execução.
