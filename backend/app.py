import json
import os
import re
import smtplib
import sqlite3
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

from flask import Flask, jsonify, request, Response
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

EMAIL_PATTERN = re.compile(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")
BASE_DIR = Path(__file__).resolve().parent.parent
# Data directory defaults to /tmp to avoid writing to read-only repo mounts in cloud hosts
DATA_DIR = Path(os.getenv("DATA_DIR", "/tmp/meu-site"))
STORAGE_PATH = DATA_DIR / "messages.jsonl"
NEWSLETTER_PATH = DATA_DIR / "newsletter.jsonl"
METRICS_PATH = DATA_DIR / "metrics.jsonl"
RSS_PATH = BASE_DIR / "rss.xml"
DB_PATH = Path(__file__).resolve().parent / "dev.db"
USE_SQLITE = os.getenv("USE_SQLITE", "").lower() in {"1", "true", "yes"}


def _corsify(response):
    response.headers["Access-Control-Allow-Origin"] = os.getenv("ALLOWED_ORIGIN", "*")
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.after_request
def add_cors_headers(response):
    return _corsify(response)


def _append_jsonl(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def _load_rss_from_file():
    if not RSS_PATH.exists():
        return None
    return RSS_PATH.read_text(encoding="utf-8")

def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    if not USE_SQLITE:
        return
    conn = _db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS newsletter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


_init_db()


@app.route("/api/health", methods=["GET", "OPTIONS"])
def health():
    if request.method == "OPTIONS":
        return _corsify(app.response_class(status=204))

    return jsonify(
        {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "storage": str(DATA_DIR),
        }
    )


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
        _append_jsonl(STORAGE_PATH, payload)

    return jsonify({"ok": True})


@app.route("/api/newsletter", methods=["POST", "OPTIONS"])
def newsletter():
    if request.method == "OPTIONS":
        return _corsify(app.response_class(status=204))

    data = request.get_json(silent=True) or {}
    name = str(data.get("nome", "")).strip()
    email = str(data.get("email", "")).strip()

    if not email or not EMAIL_PATTERN.match(email):
        return jsonify({"error": "Email invalido."}), 400

    payload = {
        "nome": name,
        "email": email,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    if USE_SQLITE:
        conn = _db()
        conn.execute(
            "INSERT INTO newsletter (name, email, created_at) VALUES (?, ?, ?)",
            (name, email, payload["created_at"])
        )
        conn.commit()
        conn.close()
    else:
        _append_jsonl(NEWSLETTER_PATH, payload)
    return jsonify({"ok": True})


@app.route("/api/auth/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return _corsify(app.response_class(status=204))

    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip()
    password = str(data.get("password", "")).strip()

    if not USE_SQLITE:
        return jsonify({"error": "Cadastro desativado."}), 400

    if not username or not email or not password:
        return jsonify({"error": "Campos obrigatorios."}), 400

    conn = _db()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)",
            (
                username,
                email,
                generate_password_hash(password, method="pbkdf2:sha256"),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Usuario ja existe."}), 400
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/auth/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return _corsify(app.response_class(status=204))

    if not USE_SQLITE:
        return jsonify({"error": "Login desativado."}), 400

    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if not username or not password:
        return jsonify({"error": "Campos obrigatorios."}), 400

    conn = _db()
    row = conn.execute(
        "SELECT id, password FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()

    if not row or not check_password_hash(row["password"], password):
        return jsonify({"error": "Credenciais invalidas."}), 401

    return jsonify({"ok": True})


@app.route("/api/metrics", methods=["POST", "OPTIONS"])
def metrics():
    if request.method == "OPTIONS":
        return _corsify(app.response_class(status=204))

    data = request.get_json(silent=True) or {}
    event = str(data.get("event", "")).strip()
    page = str(data.get("page", "")).strip()

    if not event:
        return jsonify({"error": "Evento obrigatorio."}), 400

    payload = {
        "event": event,
        "page": page,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    _append_jsonl(METRICS_PATH, payload)
    return jsonify({"ok": True})


@app.route("/api/rss", methods=["GET"])
def rss():
    file_content = _load_rss_from_file()
    if file_content:
        return Response(file_content, mimetype="application/rss+xml")

    minimal = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\\n"
        "<rss version=\"2.0\">\\n"
        "  <channel>\\n"
        "    <title>Noticias · Victor Dmitry</title>\\n"
        "    <link>https://victordmitry.xyz</link>\\n"
        "    <description>RSS temporario enquanto nenhuma fonte foi configurada.</description>\\n"
        "    <language>pt-br</language>\\n"
        "  </channel>\\n"
        "</rss>\\n"
    )
    return Response(minimal, mimetype="application/rss+xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
