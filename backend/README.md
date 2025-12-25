# Backend (Python)

Backend simples para receber mensagens do formulario, newsletter e forum, com fallback em JSONL.

## Rodar local

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

## Configuracao de email (opcional)

Defina variaveis de ambiente para enviar email real:

- `SMTP_HOST`
- `SMTP_PORT` (padrao 587)
- `SMTP_USER`
- `SMTP_PASS`
- `CONTACT_EMAIL` (destino)

Se nao configurar SMTP, as mensagens vao para `backend/messages.jsonl`.

## Endpoints

- `POST /api/message`: mensagem do formulario.
- `POST /api/newsletter`: cadastro de newsletter (email).
- `GET /api/forum/topics`: lista de topicos.
- `POST /api/forum/topics`: cria topico.
- `POST /api/metrics`: registra evento simples.
- `GET /api/rss`: RSS gerado a partir de `news.json` e `blog.json`.
