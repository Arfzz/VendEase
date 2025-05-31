from modules.utils import load_json, save_json

PRODUCTS_FILE = 'data/products.json'

def get_all_products():
    return load_json(PRODUCTS_FILE)

def add_product(name, price, stock):
    products = get_all_products()
    new_id = max([p['id'] for p in products], default=0) + 1
    products.append({"id": new_id, "name": name, "price": price, "stock": stock})
    save_json(PRODUCTS_FILE, products)

def delete_product(product_id):
    products = get_all_products()
    products = [p for p in products if p['id'] != product_id]
    save_json(PRODUCTS_FILE, products)

def update_stock(product_id, delta):
    products = get_all_products()
    for p in products:
        if p['id'] == product_id:
            p['stock'] += delta
            break
    save_json(PRODUCTS_FILE, products)