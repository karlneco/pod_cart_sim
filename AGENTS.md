# Repository Guidelines

## Project Structure & Module Organization
- `app.py` is the Flask entry point and HTTP routes.
- `models.py` contains cart simulation logic and discount application.
- `discounts/` holds discount “plugins” (each file defines `VERB`, `parse`, `apply`).
- `data.py` loads product data from `products.json`.
- `templates/` contains Jinja2 HTML templates (`index.html`, `edit_products.html`).
- `products.json` is the editable product catalog used by the UI.

## Build, Test, and Development Commands
- `python app.py` — start the local Flask server.
- `FLASK_ENV=development python app.py` — run with debug-friendly settings (if desired).
- `python -m flask run` — alternative runner if you set `FLASK_APP=app.py`.

## Coding Style & Naming Conventions
- Python, 4-space indentation, PEP 8-ish conventions.
- Modules use `snake_case.py` (e.g., `type_discount.py`).
- Discount plugins must define `VERB` and register via `register(globals())`.
- Use explicit, descriptive variable names for pricing/COGS math.

## Testing Guidelines
- No automated tests are present.
- If you add tests, place them under `tests/` and name files `test_*.py`.
- Prefer `pytest` for new tests; document any required fixtures.

## Commit & Pull Request Guidelines
- Commit messages in history are short and free-form; no strict convention enforced.
- Keep commits focused and describe the behavior change.
- PRs should include:
  - A brief summary and manual test notes.
  - Screenshots for UI changes (if applicable).
  - Any new discount verbs and example input lines.

## Configuration & Data Notes
- Product data lives in `products.json`; the `/edit-products` UI writes back to this file.
- Pricing knobs are environment variables in `models.py` (e.g., `EXCHANGE_RATE`, `COGS_TAX_RATE`).
- Optional: copy `.env.example` to `.env` to override pricing defaults locally.
