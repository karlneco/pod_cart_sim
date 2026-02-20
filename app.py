import json
import os
from data import load_products, save_products, product_file_path
from models import simulate_cart, parse_discount_grammar
from flask import Flask, render_template, request, redirect, flash
from dotenv import load_dotenv, find_dotenv

# Load .env if present; skip quietly when missing (e.g., clean checkouts).
dotenv_path = find_dotenv(filename=".env", usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(32).hex()


def _parse_price(value):
    if value is None:
        return None
    cleaned = value.strip().replace("$", "").replace(",", "")
    if cleaned == "":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_qty(value):
    if value is None:
        return 0
    try:
        qty = int(str(value).strip())
    except ValueError:
        return 0
    return qty if qty > 0 else 0


@app.route("/", methods=["GET", "POST"])
def index():
    products = load_products()
    updated_products = {key: dict(item) for key, item in products.items()}
    result_a = None
    result_b = None
    cart = {}
    discount_text_a = "free_shipping:75"
    discount_text_b = "free_shipping:75"

    if request.method == "POST":
        for key in products:
            raw_price = request.form.get(f"price_{key}")
            parsed_price = _parse_price(raw_price)
            if parsed_price is not None:
                updated_products[key]["price"] = parsed_price

        if request.form.get("action") == "save_prices":
            saved_path = save_products(updated_products)
            flash(f"Prices saved to {saved_path}.", "success")

        for key in products:
            qty = _parse_qty(request.form.get(f"qty_{key}", 0))
            if qty > 0:
                cart[key] = qty

        discount_text_a = request.form.get("discount_text_a", "").strip()
        discount_text_b = request.form.get("discount_text_b", "").strip()

        discount_rules_a = parse_discount_grammar(discount_text_a)
        discount_rules_b = parse_discount_grammar(discount_text_b)

        result_a = simulate_cart(cart, updated_products, discount_rules_a)
        result_b = simulate_cart(cart, updated_products, discount_rules_b)

    return render_template("index.html", products=updated_products, result_a=result_a, result_b=result_b,
                           cart=cart, discount_text_a=discount_text_a, discount_text_b=discount_text_b)


@app.route("/edit-products", methods=["GET", "POST"])
def edit_products():
    # Ensure configured product file exists before read/edit.
    load_products()

    if request.method == "POST":
        new_json = request.form.get("json_data", "").strip()
        try:
            # Validate it
            parsed = json.loads(new_json)
            save_products(parsed)
            flash("Product data saved!", "success")
        except Exception as e:
            flash(f"Error: {e}", "error")
            return render_template("edit_products.html", json_data=new_json, product_file=product_file_path())
        return redirect("/")

    with open(product_file_path()) as f:
        json_data = f.read()
    return render_template("edit_products.html", json_data=json_data, product_file=product_file_path())


@app.route("/healthz", methods=["GET"])
def healthz():
    return {"ok": True}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5002"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")
