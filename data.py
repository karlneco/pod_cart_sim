import json
import os
from pathlib import Path

SEED_PRODUCT_FILE = Path(__file__).with_name("products.seed.json")
LEGACY_PRODUCT_FILE = Path(__file__).with_name("products.json")
LOCAL_PRODUCT_FILE = Path("data/products.json")


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
