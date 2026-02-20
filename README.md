# Pod Cart Sim

Shopping cart simulator for testing pricing, shipping, COGS, and discount grammar rules.

## Local run (port 5002)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

App URL: `http://127.0.0.1:5002`  
Health check: `http://127.0.0.1:5002/healthz`

## Docker run

```bash
docker compose up --build
```

Default app data path:

- `~/Documents/kozakura/apps_data/pod_cart_sim`

The compose file expects env vars at:

- `~/Documents/kozakura/apps_data/pod_cart_sim/.env`

## Docker dev (hot reload, no rebuild on code changes)

```bash
# first run
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# later runs after code/template/CSS changes
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This bind-mounts the repo into `/app` and runs Flask in debug mode for fast feedback.

## Production-like predeploy check

```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml --profile test up --build --abort-on-container-exit --exit-code-from smoke-test smoke-test
```

This waits for `/healthz` and then verifies `/` returns HTTP 200.

## Auto-deploy CI (Gitea)

This repo now follows the same deploy workflow pattern as your other pod apps:

- Workflow: `.gitea/workflows/deploy.yml`
- Deploy compose: `docker-compose.deploy.yml`
- Deploy script: `scripts/deploy_compose.sh`

Deployment behavior:

- triggers on push to `main` (and manual dispatch)
- reads `.env` from app data directory on the deploy host
- rebuilds and deploys container via Docker Compose
- checks `http://127.0.0.1:5002/healthz`
- attempts rollback to previous image if health check fails

### Expected deploy host app data path

- `/Volumes/necodata/karl/kozakura/apps_data/pod_cart_sim`

Put `.env` there before first deploy.
