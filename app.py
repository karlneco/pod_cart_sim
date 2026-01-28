import json
from data import load_products
from models import simulate_cart, parse_discount_grammar
from flask import Flask, render_template, request, redirect, flash
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load .env if present; skip quietly when missing (e.g., clean checkouts).
dotenv_path = find_dotenv(filename=".env", usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path)

PRODUCT_FILE = Path("products.json")


app = Flask(__name__)
app.secret_key = "super-secret-key-change-this"

@app.route("/", methods=["GET", "POST"])
def index():
    products = load_products()
    result_a = None
    result_b = None
    cart = {}
    discount_text_a = "free_shipping:75"
    discount_text_b = "free_shipping:75"


    if request.method == "POST":
        for key in products:
            qty = int(request.form.get(f"qty_{key}", 0))
            if qty > 0:
                cart[key] = qty

        discount_text_a = request.form.get("discount_text_a", "").strip()
        discount_text_b = request.form.get("discount_text_b", "").strip()

        discount_rules_a = parse_discount_grammar(discount_text_a)
        discount_rules_b = parse_discount_grammar(discount_text_b)

        result_a = simulate_cart(cart, products, discount_rules_a)
        result_b = simulate_cart(cart, products, discount_rules_b)

    return render_template("index.html", products=products, result_a=result_a, result_b=result_b,
                           cart=cart, discount_text_a=discount_text_a, discount_text_b=discount_text_b)


@app.route("/edit-products", methods=["GET", "POST"])
def edit_products():
    if request.method == "POST":
        new_json = request.form.get("json_data", "").strip()
        try:
            # Validate it
            parsed = json.loads(new_json)
            with open(PRODUCT_FILE, "w") as f:
                json.dump(parsed, f, indent=2)
            flash("Product data saved!", "success")
        except Exception as e:
            flash(f"Error: {e}", "error")
            return render_template("edit_products.html", json_data=new_json)
        return redirect("/")

    with open(PRODUCT_FILE) as f:
        json_data = f.read()
    return render_template("edit_products.html", json_data=json_data)
