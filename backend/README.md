# Backend (Python)

Backend simples para receber mensagens do formulario e enviar por email (SMTP) ou salvar localmente.

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
