from flask import Flask, render_template, request
from data import load_products
from models import simulate_cart, parse_discount_grammar

app = Flask(__name__)

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