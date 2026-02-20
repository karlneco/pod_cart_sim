import json
import os
from pathlib import Path

DEFAULT_PRODUCT_FILE = Path(__file__).with_name("products.json")


def _product_file() -> Path:
    return Path(os.getenv("PRODUCT_FILE", str(DEFAULT_PRODUCT_FILE)))


def _ensure_product_file():
    product_file = _product_file()
    if product_file.exists():
        return
    product_file.parent.mkdir(parents=True, exist_ok=True)
    with open(DEFAULT_PRODUCT_FILE, "r") as source:
        default_products = json.load(source)
    with open(product_file, "w") as target:
        json.dump(default_products, target, indent=2)


def load_products():
    _ensure_product_file()
    with open(_product_file(), "r") as f:
        return json.load(f)
