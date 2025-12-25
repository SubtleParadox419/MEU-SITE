import json
import os
import re
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage

from flask import Flask, jsonify, request


app = Flask(__name__)

EMAIL_PATTERN = re.compile(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")
STORAGE_PATH = os.path.join(os.path.dirname(__file__), "messages.jsonl")


def _corsify(response):
    response.headers["Access-Control-Allow-Origin"] = os.getenv("ALLOWED_ORIGIN", "*")
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response


@app.after_request
def add_cors_headers(response):
    return _corsify(response)


@app.route("/api/message", methods=["POST", "OPTIONS"])
def message():
    if request.method == "OPTIONS":
        return _corsify(app.response_class(status=204))

    data = request.get_json(silent=True) or {}
    name = str(data.get("nome", "")).strip()
    email = str(data.get("email", "")).strip()
    message_text = str(data.get("mensagem", "")).strip()

    if not name or not email or not message_text:
        return jsonify({"error": "Campos obrigatorios."}), 400

    if not EMAIL_PATTERN.match(email):
        return jsonify({"error": "Email invalido."}), 400

    payload = {
        "nome": name,
        "email": email,
        "mensagem": message_text,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    recipient = os.getenv("CONTACT_EMAIL")

    if smtp_host and smtp_user and smtp_pass and recipient:
        msg = EmailMessage()
        msg["Subject"] = f"Nova mensagem de {name}"
        msg["From"] = smtp_user
        msg["To"] = recipient
        msg.set_content(
            f"Nome: {name}\\nEmail: {email}\\n\\nMensagem:\\n{message_text}"
        )

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    else:
        with open(STORAGE_PATH, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\\n")

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
