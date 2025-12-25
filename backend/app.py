import json
import os
import re
import smtplib
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

    _append_jsonl(NEWSLETTER_PATH, payload)
    return jsonify({"ok": True})


@app.route("/api/forum/topics", methods=["GET", "POST", "OPTIONS"])
def forum_topics():
    if request.method == "OPTIONS":
        return _corsify(app.response_class(status=204))

    if request.method == "GET":
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

    _append_jsonl(FORUM_PATH, payload)
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
    news_items = _load_json(NEWS_PATH)
    blog_items = _load_json(BLOG_PATH)
    items = news_items + blog_items

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
