# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A shopping cart simulator for testing POD (print-on-demand) pricing, shipping, COGS, and discount grammar rules. It is a Flask web app that lets you configure quantities and compare two discount rule sets side-by-side, showing profit/margin math in CAD.

## Commands

### Local dev

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

App: `http://127.0.0.1:5002` — Health check: `http://127.0.0.1:5002/healthz`

### Docker dev (hot reload, no rebuild needed on code/template changes)

```bash
# first run
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
# subsequent runs
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Pre-deploy smoke test

```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml --profile test up --build --abort-on-container-exit --exit-code-from smoke-test smoke-test
```

## Architecture

### Core flow

1. `app.py` — Flask routes. The `POST /` handler reads qty/price form fields, parses two discount text blocks (A/B), calls `simulate_cart` for each, and passes results to the template for side-by-side comparison.
2. `data.py` — Loads/saves product catalog from `PRODUCT_FILE` (default `data/products.json`). Auto-seeds from `products.seed.json` on first run. The `/edit-products` UI allows live JSON edits.
3. `models.py` — `simulate_cart()` accumulates merchandise totals, COGS, and shipping, then calls `apply_discounts()` and `apply_shipping_discounts()` before computing profit in both USD and CAD.
4. `discounts/` — Plugin system auto-discovered at startup via `load_all()`.

### Discount plugin system

Each file in `discounts/` is a plugin. Every plugin must define:

- `VERB` (str) — the keyword used in the discount grammar textarea
- `CATEGORY` (str) — `"price"` or `"shipping"` (controls which apply loop runs it)
- `parse(line: str) -> dict` — parses a grammar line like `"verb: arg1,arg2"`
- `apply(cart, products, rule) -> float | tuple[float, str]` — returns USD discount amount (and optional label)
- `apply_shipping(...)` — optional; shipping plugins should implement this instead of `apply`
- `register(globals())` at the bottom — registers the plugin in `REGISTRY`

Unknown verbs in the grammar textarea are silently ignored, so you can leave experiments there.

### Product data schema

Each product key in `products.json` has:
```json
{
  "name": "...", "type": "...", "price": 0.00, "cogs": 0.00,
  "real_shipping_first": 0.00, "real_shipping_additional": 0.00,
  "store_shipping": 0.00, "use_real_shipping": true, "kind": "..."
}
```
`type` and `kind` are both used by discount plugins to match product categories.

### Economics knobs (env vars)

All override defaults in `models.py`:

| Var | Default | Meaning |
|-----|---------|---------|
| `EXCHANGE_RATE` | 1.44 | USD → CAD |
| `COGS_TAX_RATE` | 0.07 | Tax on COGS + shipping |
| `FEE_PCT_1` | 0.035 | Store platform fee % (first pass) |
| `FEE_FIXED` | 0.30 | Store platform fixed fee |
| `FEE_PCT_2` | 0.02 | Store platform fee % (second pass) |
| `PRODUCT_FILE` | `data/products.json` | Runtime product data path |
| `PORT` | 5002 | Flask port |

## Discount grammar

Lines in the textarea follow `verb: args` format. Current plugins:

| Verb | Example | Notes |
|------|---------|-------|
| `free_shipping` | `free_shipping: 75` | Free shipping when order ≥ $75 |
| `bogo` | `bogo: tee,2,1` | Buy X get Y free for a type (blank = any) |
| `type_discount` | `type_discount: g64k,10` | % off all items of a `type` |
| `type_tier_discount` | see file | Tiered % by type |
| `whole_order` | `whole_order: 10` | % off entire order |
| `min_total` | `min_total: 100,15` | % off when order ≥ min |
| `cart_quantity_discount` | see file | Discount based on total cart qty |
| `buy_x_get_1off` | see file | Buy X items, get 1 at a discount |
| `buy_type_get_type_discount` | see file | Cross-type discount |
| `free_shipping_type_qty` | see file | Free shipping based on type + qty |
