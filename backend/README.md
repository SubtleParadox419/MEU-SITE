# Backend (Python)

Backend simples para receber mensagens do formulario e newsletter, com fallback em JSONL. Opcionalmente usa SQLite local para testes.

## Rodar local

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

Para testar com SQLite (nao recomendado em prod):

```powershell
$env:USE_SQLITE = "1"
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
- `POST /api/metrics`: registra evento simples.
- `GET /api/rss`: RSS (usa rss.xml se presente, senao responde vazio).
- `POST /api/auth/register`: cadastro simples (somente em SQLite).
- `POST /api/auth/login`: login simples (somente em SQLite).
- `GET /api/health`: liveness; se `HEALTH_TOKEN` estiver definido, exige cabecalho `X-Health-Token` ou query `token`.
