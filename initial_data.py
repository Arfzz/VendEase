import os
import json
import hashlib
from datetime import datetime

DATA_DIR = "data"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"📁 Folder '{DATA_DIR}' dibuat.")
    else:
        print(f"📂 Folder '{DATA_DIR}' sudah ada.")

def create_users():
    users = [
        {
            "username": "admin",
            "password": hash_password("password"),
            "role": "admin"
        },
        {
            "username": "teknisi",
            "password": hash_password("password"),
            "role": "technician"
        },
        {
            "username": "user",
            "password": hash_password("password"),
            "role": "user"
        },
        {
            "username": "superadmin",
            "password": hash_password("password"),
            "role": "superadmin"
        }
    ]
    with open(os.path.join(DATA_DIR, "users.json"), "w") as f:
        json.dump(users, f, indent=4)
    print("✅ users.json dibuat.")

def create_products():
    products = [
        {"id": 1, "name": "Air Mineral", "price": 5000, "stock": 20},
        {"id": 2, "name": "Teh Botol", "price": 7000, "stock": 15},
        {"id": 3, "name": "Chitato", "price": 10000, "stock": 10}
    ]
    with open(os.path.join(DATA_DIR, "products.json"), "w") as f:
        json.dump(products, f, indent=4)
    print("✅ products.json dibuat.")

def create_transactions():
    transactions = [
        {
            "product_id": 1,
            "quantity": 2,
            "total_price": 10000,
            "timestamp": "2024-04-15T10:30:00"
        },
        {
            "product_id": 3,
            "quantity": 1,
            "total_price": 10000,
            "timestamp": "2024-04-15T11:00:00"
        }
    ]
    with open(os.path.join(DATA_DIR, "transactions.json"), "w") as f:
        json.dump(transactions, f, indent=4)
    print("✅ transactions.json dibuat.")

def create_log():
    log_lines = [
        f"[{datetime.now().isoformat()}] Admin admin login.",
        f"[{datetime.now().isoformat()}] Admin admin menambah produk Teh Pucuk.",
        f"[{datetime.now().isoformat()}] User membeli 2 x Air Mineral.",
        f"[{datetime.now().isoformat()}] Teknisi teknisi login."
    ]
    with open(os.path.join(DATA_DIR, "system_log.txt"), "w") as f:
        f.write("\n".join(log_lines) + "\n")
    print("✅ system_log.txt dibuat.")

def main():
    create_dir()
    create_users()
    create_products()
    create_transactions()
    create_log()
    print("\n🎉 Inisialisasi data selesai!")

if __name__ == "__main__":
    main()
