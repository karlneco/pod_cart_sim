import os
from flask import Flask, render_template
from dotenv import load_dotenv, find_dotenv


dotenv_path = find_dotenv(filename=".env", usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(32).hex()


@app.get("/")
def index():
    cards = [
        {
            "title": "Workflow Hub",
            "description": "Drop in your first route and keep the app shell consistent across projects.",
            "href": "#",
        },
        {
            "title": "Data-Backed Page",
            "description": "Use /data mounts for editable runtime files and keep git history clean.",
            "href": "#",
        },
        {
            "title": "Deploy Ready",
            "description": "Gitea workflow and deploy script are included for fast internal shipping.",
            "href": "#",
        },
    ]
    return render_template("index.html", cards=cards, app_title=os.getenv("APP_TITLE", "Flask Starter"))


@app.get("/healthz")
def healthz():
    return {"ok": True}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")
