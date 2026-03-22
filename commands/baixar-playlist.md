# /baixar-playlist

Você é o orquestrador de download de múltiplas músicas em paralelo.
Cada música será processada por um agente independente com seu próprio contexto.

## Input

O usuário fornecerá uma lista de músicas via `$ARGUMENTS`.

Formatos aceitos:
```
# Formato simples (uma por linha):
Aquarela Toquinho
Hotel California Eagles
Clube da Esquina Milton Nascimento

# Formato numerado:
1. Aquarela Toquinho
2. Hotel California Eagles
3. Clube da Esquina Milton Nascimento
```

Se `$ARGUMENTS` estiver vazio, pergunte ao usuário a lista antes de prosseguir.

---

## Etapa 1 — Parsear a lista

Extraia cada música do input e monte um array:

```json
[
  { "id": 1, "query": "Aquarela Toquinho" },
  { "id": 2, "query": "Hotel California Eagles" },
  { "id": 3, "query": "Clube da Esquina Milton Nascimento" }
]
```

Informe o usuário quantas músicas foram identificadas antes de prosseguir:
```
📋 Encontrei 3 músicas na sua lista. Iniciando downloads em paralelo...
```

---

## Etapa 2 — Spawnar um agente por música

Para cada item do array, spawne um agente independente usando a ferramenta
`Task` do Claude Code. Todos os agentes devem ser iniciados **simultaneamente**,
não em sequência.

Cada agente recebe este prompt:

```
Você é um agente de download de música. Execute o workflow completo
para a seguinte música: "{query}"

Siga estas etapas em ordem:

1. Execute o script de busca:
   python ~/.claude/scripts/youtube_search.py "{query}"

2. Avalie o resultado consultando a skill youtube-search.
   - Se encontrar resultado claro: prossiga automaticamente
   - Se ambíguo: escolha o resultado com score "alto" ou o primeiro da lista
   - NÃO pergunte ao usuário — tome a melhor decisão disponível

3. Execute o download:
   python ~/.claude/scripts/music_download.py "{video_id}" "{titulo}"

4. Faça upload para o Google Drive consultando a skill gdrive-upload:
   - Verifique/crie a pasta Músicas/
   - Faça upload do MP3
   - Se já existir arquivo com mesmo nome: substitua automaticamente

5. Retorne APENAS este JSON ao orquestrador (sem texto adicional):
{
  "id": {id},
  "query": "{query}",
  "status": "success" | "error",
  "titulo": "título encontrado",
  "link": "link do Google Drive",
  "erro": "descrição do erro se houver"
}
```

---

## Etapa 3 — Aguardar e consolidar resultados

Aguarde a conclusão de todos os agentes.
À medida que cada agente retornar, exiba progresso em tempo real:

```
⏳ Processando 3 músicas...
  ✅ [1/3] Aquarela - Toquinho → Drive/Músicas/aquarela_toquinho.mp3
  ✅ [2/3] Hotel California - Eagles → Drive/Músicas/hotel_california.mp3
  ⏳ [3/3] Clube da Esquina... aguardando
```

---

## Etapa 4 — Relatório final

Quando todos os agentes concluírem, exiba o relatório consolidado:

```
🎵 Download de playlist concluído!
─────────────────────────────────────────────
✅ Aquarela — Toquinho
   📁 https://drive.google.com/file/d/xxx

✅ Hotel California — Eagles
   📁 https://drive.google.com/file/d/yyy

❌ Clube da Esquina — Milton Nascimento
   ⚠️  Erro: Vídeo indisponível na sua região

─────────────────────────────────────────────
Total: 3 músicas | ✅ 2 concluídas | ❌ 1 com erro
```

Se houver erros, pergunte ao usuário se deseja tentar novamente
apenas as músicas que falharam.

---

## Regras para os agentes

- Cada agente opera de forma **totalmente autônoma** — não faz perguntas ao usuário
- Em caso de ambiguidade, escolhe o melhor resultado disponível automaticamente
- Em caso de erro irrecuperável, retorna JSON com status "error" e encerra
- Cada agente tem seu próprio contexto isolado — não interfere nos demais
- O orquestrador é o único que se comunica com o usuário

---

## Limite de paralelismo

Para evitar sobrecarga de API e rate limiting do YouTube:
- Até 5 músicas: spawne todos os agentes simultaneamente
- Entre 6 e 20 músicas: spawne em lotes de 5, aguarde cada lote concluir
- Acima de 20 músicas: avise o usuário que será processado em lotes de 5
