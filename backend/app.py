import json
import os
import re
import smtplib
import sqlite3
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

from flask import Flask, jsonify, request, Response


app = Flask(__name__)

EMAIL_PATTERN = re.compile(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_PATH = Path(__file__).resolve().parent / "messages.jsonl"
NEWSLETTER_PATH = Path(__file__).resolve().parent / "newsletter.jsonl"
FORUM_PATH = Path(__file__).resolve().parent / "forum_topics.jsonl"
METRICS_PATH = Path(__file__).resolve().parent / "metrics.jsonl"
NEWS_PATH = BASE_DIR / "news.json"
BLOG_PATH = BASE_DIR / "blog.json"
DB_PATH = Path(__file__).resolve().parent / "dev.db"
USE_SQLITE = os.getenv("USE_SQLITE", "").lower() in {"1", "true", "yes"}


def _corsify(response):
    response.headers["Access-Control-Allow-Origin"] = os.getenv("ALLOWED_ORIGIN", "*")
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response


@app.after_request
def add_cors_headers(response):
    return _corsify(response)


def _append_jsonl(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def _load_json(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_jsonl(path, limit=50):
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    items = [json.loads(line) for line in lines[-limit:]]
    return list(reversed(items))


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
        CREATE TABLE IF NOT EXISTS forum_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS forum_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            message TEXT NOT NULL,
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


@app.route("/api/forum/topics", methods=["GET", "POST", "OPTIONS"])
def forum_topics():
    if request.method == "OPTIONS":
        return _corsify(app.response_class(status=204))

    if request.method == "GET":
        if USE_SQLITE:
            conn = _db()
            rows = conn.execute(
                "SELECT id, title, author, message, created_at FROM forum_topics ORDER BY id DESC LIMIT 50"
            ).fetchall()
            conn.close()
            return jsonify([dict(row) for row in rows])
        return jsonify(_load_jsonl(FORUM_PATH))

    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    author = str(data.get("author", "")).strip()
    message_text = str(data.get("message", "")).strip()

    if not title or not author or not message_text:
        return jsonify({"error": "Campos obrigatorios."}), 400

    payload = {
        "title": title,
        "author": author,
        "message": message_text,
        "created_at": datetime.now(timezone.utc).strftime("%d/%m/%Y")
    }

    if USE_SQLITE:
        conn = _db()
        conn.execute(
            "INSERT INTO forum_topics (title, author, message, created_at) VALUES (?, ?, ?, ?)",
            (title, author, message_text, payload["created_at"])
        )
        conn.commit()
        conn.close()
    else:
        _append_jsonl(FORUM_PATH, payload)
    return jsonify({"ok": True})


@app.route("/api/forum/comments", methods=["GET", "POST", "OPTIONS"])
def forum_comments():
    if request.method == "OPTIONS":
        return _corsify(app.response_class(status=204))

    if request.method == "GET":
        topic_id = request.args.get("topic_id", "").strip()
        if USE_SQLITE and topic_id.isdigit():
            conn = _db()
            rows = conn.execute(
                "SELECT id, topic_id, author, message, created_at FROM forum_comments WHERE topic_id = ? ORDER BY id DESC",
                (int(topic_id),)
            ).fetchall()
            conn.close()
            return jsonify([dict(row) for row in rows])
        return jsonify([])

    data = request.get_json(silent=True) or {}
    topic_id = str(data.get("topic_id", "")).strip()
    author = str(data.get("author", "")).strip()
    message_text = str(data.get("message", "")).strip()

    if not topic_id.isdigit() or not author or not message_text:
        return jsonify({"error": "Campos obrigatorios."}), 400

    payload = {
        "topic_id": int(topic_id),
        "author": author,
        "message": message_text,
        "created_at": datetime.now(timezone.utc).strftime("%d/%m/%Y")
    }

    if USE_SQLITE:
        conn = _db()
        conn.execute(
            "INSERT INTO forum_comments (topic_id, author, message, created_at) VALUES (?, ?, ?, ?)",
            (payload["topic_id"], author, message_text, payload["created_at"])
        )
        conn.commit()
        conn.close()
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
            (username, email, password, datetime.now(timezone.utc).isoformat())
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
        "SELECT id FROM users WHERE username = ? AND password = ?",
        (username, password)
    ).fetchone()
    conn.close()

    if not row:
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
    items = []
    entries = []
    for item in items:
        title = item.get("title", "Atualizacao")
        desc = item.get("summary") or item.get("excerpt", "")
        date = item.get("date", "01/01/2025")
        entries.append(
            f\"\"\"\n    <item>\n      <title>{title}</title>\n      <link>https://victordmitry.xyz/news.html</link>\n      <pubDate>{date}</pubDate>\n      <description>{desc}</description>\n    </item>\"\"\"\n        )

    content = \"\"\"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<rss version=\"2.0\">\n  <channel>\n    <title>Noticias · Victor Dmitry</title>\n    <link>https://victordmitry.xyz/news.html</link>\n    <description>Atualizacoes sobre IA, seguranca e software engineering.</description>\n    <language>pt-br</language>\n{entries}\n  </channel>\n</rss>\n\"\"\".format(entries=\"\".join(entries))

    return Response(content, mimetype="application/rss+xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
