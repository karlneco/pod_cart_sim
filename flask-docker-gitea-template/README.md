# Flask + Docker + Gitea Template

Starter template for internal Flask apps with:

- consistent Kozakura visual language (header/cards/typography)
- Docker run/dev/deploy/test compose files
- Gitea Actions auto-deploy workflow
- deploy script with rollback and health checks

## What to customize first

1. App title in `.env` (`APP_TITLE`).
2. Port if needed (`5000` defaults in compose + app).
3. Data path in compose/workflow:
   - `docker-compose.yml`
   - `docker-compose.dev.yml`
   - `.gitea/workflows/deploy.yml`

## Local run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

App URL: `http://127.0.0.1:5000`  
Health: `http://127.0.0.1:5000/healthz`

## Docker run

```bash
docker compose up --build
```

## Docker dev (hot reload)

```bash
# first run
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# later runs
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Production-like smoke check

```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml --profile test up --build --abort-on-container-exit --exit-code-from smoke-test smoke-test
```

## Gitea deploy flow

Workflow file: `.gitea/workflows/deploy.yml`

Before first deploy, create app data dir and `.env` on the deploy host path configured in that workflow.
