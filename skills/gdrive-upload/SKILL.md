---
name: gdrive-upload
description: >
  Orientação para upload de arquivos MP3 para o Google Drive via MCP.
  Use esta skill sempre que precisar enviar um arquivo local para o Google Drive,
  verificar ou criar pastas no Drive, obter links compartilháveis, ou gerenciar
  arquivos de mídia em nuvem. Acione também quando o usuário mencionar
  "salvar no Drive", "enviar para o Google Drive", "disponibilizar na nuvem",
  "compartilhar arquivo" ou qualquer variação de upload para o Google Drive.
---

# gdrive-upload

Skill para upload de arquivos MP3 para o Google Drive via MCP,
com verificação de pasta destino, tratamento de duplicatas e
geração de link compartilhável.

---

## Pré-requisito: MCP Google Drive

Esta skill depende exclusivamente do MCP do Google Drive.
**Não use Google Drive API diretamente** — o MCP já gerencia
autenticação OAuth2, tokens e permissões.

Verifique se o MCP está ativo antes de prosseguir:
- No Claude Code: o MCP `Google Drive` deve estar listado e conectado
- Se não estiver conectado: oriente o usuário a reconectar em
  Configurações → Integrações → Google Drive

---

## Fluxo de execução

Execute as etapas abaixo em ordem usando as ferramentas MCP disponíveis.

### Etapa 1 — Verificar/criar pasta destino

Busque a pasta `Músicas` no Google Drive do usuário:

```
MCP: gdrive_search
query: "Músicas" type:folder
```

**Decisão:**
- Pasta encontrada → use o `folder_id` retornado
- Pasta não encontrada → crie com:
  ```
  MCP: gdrive_create_folder
  name: "Músicas"
  parent: root
  ```

---

### Etapa 2 — Verificar duplicata

Antes de fazer upload, verifique se já existe arquivo com o mesmo nome
na pasta destino:

```
MCP: gdrive_search
query: "{nome_arquivo}" parents:"{folder_id}"
```

**Decisão:**
- Arquivo não existe → prossiga para upload
- Arquivo já existe → pergunte ao usuário:
  ```
  ⚠️ "{nome_arquivo}" já existe no Drive.
  O que deseja fazer?
  1. Substituir o arquivo existente
  2. Manter ambos (salvar com sufixo _novo)
  3. Cancelar
  ```

---

### Etapa 3 — Upload do arquivo

```
MCP: gdrive_upload_file
file_path: "{caminho_local_mp3}"
name: "{nome_arquivo}.mp3"
parent_folder_id: "{folder_id}"
mime_type: "audio/mpeg"
```

Aguarde confirmação de sucesso antes de prosseguir.

---

### Etapa 4 — Obter link compartilhável

Após upload bem-sucedido, obtenha o link:

```
MCP: gdrive_get_file_link
file_id: "{file_id_retornado_no_upload}"
permission: "anyone_with_link"
```

---

### Etapa 5 — Limpeza local (opcional)

Após confirmação do upload, remova o arquivo temporário local:

```bash
python -c "import os; os.remove('{caminho_local_mp3}')"
```

Só execute esta etapa se o upload foi confirmado com sucesso.
Em caso de dúvida, não delete — o usuário pode verificar manualmente.

---

## Formato de saída esperado

Sucesso:
```json
{
  "status": "success",
  "arquivo": "aquarela_toquinho.mp3",
  "folder": "Músicas",
  "file_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs",
  "link": "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs/view",
  "tamanho_mb": 4.2
}
```

Falha:
```json
{
  "status": "error",
  "codigo": "MCP_AUTH_ERROR",
  "mensagem": "MCP do Google Drive não está autenticado."
}
```

---

## Erros comuns e como tratar

| Código | Causa | Ação |
|---|---|---|
| `MCP_AUTH_ERROR` | MCP não conectado ou token expirado | Orientar reconexão nas configurações |
| `STORAGE_QUOTA` | Google Drive sem espaço | Informar usuário — Drive lotado |
| `FILE_NOT_FOUND` | Arquivo local não existe no caminho informado | Verificar se download foi concluído |
| `FOLDER_CREATE_ERROR` | Sem permissão para criar pasta | Usar pasta raiz do Drive como fallback |
| `UPLOAD_TIMEOUT` | Arquivo grande ou conexão lenta | Retentar 1x antes de reportar erro |

---

## Estrutura de pastas recomendada no Drive

```
Google Drive/
└── Músicas/                ← pasta criada automaticamente pelo workflow
    ├── aquarela_toquinho.mp3
    ├── hotel_california.mp3
    └── clube_da_esquina.mp3
```

Se quiser organizar por artista no futuro, basta ajustar
o slash command para passar o artista como subpasta:
`Músicas/Toquinho/aquarela.mp3`

---

## Nota sobre permissões do link

O link gerado na Etapa 4 usa permissão `anyone_with_link` —
qualquer pessoa com o link pode ouvir/baixar o arquivo.

Se preferir manter o arquivo privado (só você acessa),
instrua o Claude a não definir permissão pública e apenas
retornar o link direto do Drive sem compartilhamento.
