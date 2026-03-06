import json
import os
from pathlib import Path

SEED_PRODUCT_FILE = Path(__file__).with_name("products.seed.json")
LEGACY_PRODUCT_FILE = Path(__file__).with_name("products.json")
LOCAL_PRODUCT_FILE = Path("data/products.json")

# Allowed values for each metric display mode
DISPLAY_MODES = {"USD", "CAD", "SWAP"}

# Defaults — matches data/display_config.json
_DISPLAY_CONFIG_DEFAULTS = {
    "original_price":         "USD",
    "total_discount":         "SWAP",
    "order_total":            "SWAP",
    "store_shipping_charged": "SWAP",
    "customer_pays":          "SWAP",
    "cogs":                   "SWAP",
    "real_shipping_cost":     "SWAP",
    "cogs_tax":               "SWAP",
    "cogs_total":             "SWAP",
    "store_fees":             "SWAP",
    "store_payout":           "SWAP",
    "total_expenses":         "SWAP",
    "profit_loss":            "SWAP",
}


def _product_file() -> Path:
    return Path(os.getenv("PRODUCT_FILE", str(LOCAL_PRODUCT_FILE)))


def _ensure_product_file():
    product_file = _product_file()
    if product_file.exists():
        return
    product_file.parent.mkdir(parents=True, exist_ok=True)
    source_file = LEGACY_PRODUCT_FILE if LEGACY_PRODUCT_FILE.exists() else SEED_PRODUCT_FILE
    with open(source_file, "r") as source:
        default_products = json.load(source)
    with open(product_file, "w") as target:
        json.dump(default_products, target, indent=2)


def product_file_path() -> Path:
    _ensure_product_file()
    return _product_file()


def load_products():
    _ensure_product_file()
    with open(_product_file(), "r") as f:
        return json.load(f)


def save_products(products: dict) -> Path:
    _ensure_product_file()
    target_path = _product_file()
    with open(target_path, "w") as target:
        json.dump(products, target, indent=2)
    return target_path


def _display_config_file() -> Path:
    # Always sits next to products.json (works locally and in Docker)
    return _product_file().parent / "display_config.json"


def _normalize_display_mode(value, default: str) -> str:
    if isinstance(value, str):
        normalized = value.strip().upper()
        if normalized in DISPLAY_MODES:
            return normalized
    return default


def load_display_config() -> dict:
    """Load display_config.json, seeding it from defaults if absent.
    Unknown keys in the file are ignored; missing keys fall back to defaults.
    Invalid mode values are silently replaced with the default."""
    cfg_path = _display_config_file()
    if not cfg_path.exists():
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cfg_path, "w") as f:
            json.dump(_DISPLAY_CONFIG_DEFAULTS, f, indent=2)
        return dict(_DISPLAY_CONFIG_DEFAULTS)

    with open(cfg_path, "r") as f:
        raw = json.load(f)
    raw = raw if isinstance(raw, dict) else {}

    result = dict(_DISPLAY_CONFIG_DEFAULTS)
    for key, default in _DISPLAY_CONFIG_DEFAULTS.items():
        result[key] = _normalize_display_mode(raw.get(key), default)
    return result
