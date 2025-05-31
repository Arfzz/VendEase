# from modules.utils import log_event, verify_password, load_json
# from modules.structures.stack import Stack

# def technician_menu():
#     users = load_json('data/users.json')
#     username = input("Username: ")
#     password = input("Password: ")
#     user = next((u for u in users if u['username'] == username and u['role'] == 'technician'), None)

#     if not user or not verify_password(password, user['password']):
#         print("Login gagal.")
#         return

#     log_event(f"Teknisi {username} login.")

#     while True:
#         print("\n=== MODE TEKNISI ===")
#         print("1. Tampilkan Log")
#         print("2. Reset Log")
#         print("3. Logout")
#         choice = input("Pilih menu: ")

#         if choice == '1':
#             log_stack = Stack()
#             with open("data/system_log.txt", "r") as f:
#                 for line in f:
#                     log_stack.push(line.strip())

#             print("\n=== Log Sistem (Urutan Terbalik / Stack) ===")
#             while not log_stack.is_empty():
#                 print(log_stack.pop())

#         elif choice == '2':
#             open('data/system_log.txt', 'w').close()
#             print("Log berhasil di-reset.")

#         elif choice == '3':
#             break

#         else:
#             print("Pilihan tidak valid.")


from rich.console import Console
from rich.table import Table 
from rich.panel import Panel
from rich.prompt import Prompt
from modules.utils import log_event, load_json, save_json
import os
import json

console = Console()

def technician_menu():
    """Technician menu for maintenance operations"""
    while True:
        console.clear()
        console.print(Panel.fit("🔧 [bold cyan]TEKNISI DASHBOARD[/bold cyan]", border_style="yellow"))
        
        console.print("[1] Tampilkan Log Sistem")
        console.print("[2] Reset Log")
        console.print("[3] Restock Produk")
        console.print("[4] Status Sistem")
        console.print("[5] Logout")
        
        choice = Prompt.ask("\n[bold yellow]Pilih menu[/bold yellow]", choices=["1", "2", "3", "4", "5"])
        
        if choice == '1':
            tampilkan_log()
        elif choice == '2':
            reset_log()
        elif choice == '3':
            restock_produk()
        elif choice == '4':
            status_sistem()
        elif choice == '5':
            break

def tampilkan_log():
    """Display system logs"""
    console.clear()
    console.print(Panel.fit("📝 [bold cyan]LOG SISTEM[/bold cyan]", border_style="yellow"))
    
    try:
        if not os.path.exists('data/system_log.txt'):
            console.print("[yellow]Log sistem belum tersedia.[/yellow]")
        else:
            with open('data/system_log.txt', 'r') as f:
                log_content = f.read()
                if log_content.strip():
                    console.print(log_content)
                else:
                    console.print("[yellow]Log sistem kosong.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error membaca log: {e}[/red]")
    
    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def reset_log():
    """Reset system logs"""
    console.clear()
    console.print(Panel.fit("🗑️ [bold cyan]RESET LOG SISTEM[/bold cyan]", border_style="yellow"))
    
    confirm = Prompt.ask("Apakah Anda yakin ingin me-reset log sistem? (y/n)", choices=["y", "n"], default="n")
    
    if confirm.lower() == "y":
        try:
            log_dir = os.path.dirname('data/system_log.txt')
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            with open('data/system_log.txt', 'w') as f:
                pass  # Just create an empty file
                
            console.print("[green]✅ Log sistem berhasil di-reset![/green]")
            log_event("Log sistem di-reset oleh teknisi")
        except Exception as e:
            console.print(f"[red]Error saat me-reset log: {e}[/red]")
    else:
        console.print("[yellow]Reset log dibatalkan.[/yellow]")
    
    Prompt.ask("\nTekan Enter untuk melanjutkan...")
    
def save_products(products):
    """Save products to JSON file"""
    try:
        with open("data/products.json", "w") as file:
            json.dump(products, file, indent=4)
        console.print("[green]✅ Produk berhasil disimpan![/green]")
    except Exception as e:
        console.print(f"[red]Error saat menyimpan produk: {e}[/red]")


def restock_produk():
    """Restock products"""
    console.clear()
    console.print(Panel.fit("📦 [bold cyan]RESTOCK PRODUK[/bold cyan]", border_style="yellow"))
    
    products = load_json("data/products.json")
    
    if not products:
        console.print("[yellow]Tidak ada produk tersedia.[/yellow]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    # Display products with stock levels
    console.print("[bold]Stok Produk Saat Ini:[/bold]\n")
    for idx, product in enumerate(products):
        stock_style = "green" if product['stock'] > 5 else "yellow" if product['stock'] > 0 else "red"
        console.print(f"{idx+1}. {product['name']} (ID: {product['id']}) - Stok: [{stock_style}]{product['stock']}[/{stock_style}]")
    
    try:
        product_idx = int(Prompt.ask("\n[yellow]Pilih nomor produk untuk restock[/yellow]", 
                                      choices=[str(i) for i in range(1, len(products) + 1)]))
        product = products[product_idx - 1]
        
        console.print(f"\nProduk: [bold]{product['name']}[/bold]")
        console.print(f"Stok saat ini: [bold]{product['stock']}[/bold]")
        
        action = Prompt.ask("[yellow]Tambah atau kurangi stok?[/yellow]", choices=["tambah", "kurangi"])
        
        while True:
            try:
                amount = int(Prompt.ask("[yellow]Jumlah[/yellow]"))
                if amount < 0:
                    console.print("[red]Jumlah tidak boleh negatif![/red]")
                    continue
                break
            except ValueError:
                console.print("[red]Masukkan jumlah dalam angka![/red]")
        
        if action == "tambah":
            product['stock'] += amount
            console.print(f"[bold green]Stok {product['name']} bertambah {amount}. Stok sekarang: {product['stock']}[/bold green]")
        else:  # kurangi
            if amount > product['stock']:
                console.print(f"[bold red]Stok tidak cukup! Stok saat ini hanya {product['stock']}[/bold red]")
                return
            product['stock'] -= amount
            console.print(f"[bold yellow]Stok {product['name']} berkurang {amount}. Stok sekarang: {product['stock']}[/bold yellow]")
        
        try:
            save_json("data/products.json", products)
            log_event(f"Teknisi melakukan restock produk {product['name']} (ID: {product['id']})")
            console.print("[green]Data berhasil disimpan![/green]")
        except Exception as e:
            console.print(f"[red]Error saat menyimpan produk: {e}[/red]")
        
    except ValueError:
        console.print("[red]Input tidak valid! Pilih nomor produk yang benar.[/red]")
    except IndexError:
        console.print("[red]Nomor produk tidak ditemukan![/red]")
    
    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def status_sistem():
    """Check system status"""
    console.clear()
    console.print(Panel.fit("🔍 [bold cyan]STATUS SISTEM[/bold cyan]", border_style="yellow"))
    
    # Check data files
    data_files = {
        "Users": "data/users.json",
        "Products": "data/products.json",
        "Transactions": "data/transactions.json",
        "System Log": "data/system_log.txt"
    }
    
    table = Table(title="Status File Sistem", show_header=True, header_style="bold")
    table.add_column("File")
    table.add_column("Status")
    table.add_column("Info")
    
    for name, path in data_files.items():
        if os.path.exists(path):
            if path.endswith('.json'):
                try:
                    data = load_json(path)
                    count = len(data)
                    status = "[green]OK[/green]"
                    info = f"{count} item" if count != 1 else "1 item"
                except Exception as e:
                    status = "[red]ERROR[/red]"
                    info = str(e)
            else:  # Log file
                try:
                    if os.path.getsize(path) > 0:
                        status = "[green]OK[/green]"
                        info = f"{os.path.getsize(path)} bytes"
                    else:
                        status = "[yellow]EMPTY[/yellow]"
                        info = "File kosong"
                except Exception as e:
                    status = "[red]ERROR[/red]"
                    info = str(e)
        else:
            status = "[yellow]MISSING[/yellow]"
            info = "File tidak ditemukan"
        
        table.add_row(name, status, info)
    
    console.print(table)
    
    # Check products with low stock
    products = load_json("data/products.json")
    low_stock_products = [p for p in products if p['stock'] <= 3]
    
    if low_stock_products:
        console.print("\n[bold yellow]⚠️ Produk dengan stok rendah:[/bold yellow]")
        for product in low_stock_products:
            stock_style = "red" if product['stock'] == 0 else "yellow"
            console.print(f"- {product['name']} (ID: {product['id']}): [{stock_style}]{product['stock']}[/{stock_style}]")
    
    log_event("Teknisi memeriksa status sistem")
    Prompt.ask("\nTekan Enter untuk melanjutkan...")
    
    
def technician_menu():
    """Technician menu for maintenance operations"""
    while True:
        console.clear()
        console.print(Panel.fit("🔧 [bold cyan]TEKNISI DASHBOARD[/bold cyan]", border_style="yellow"))
        
        console.print("[1] Tampilkan Log Sistem")
        console.print("[2] Reset Log")
        console.print("[3] Restock Produk")
        console.print("[4] Status Sistem")
        console.print("[5] Logout")
        
        choice = Prompt.ask("\n[bold yellow]Pilih menu[/bold yellow]", choices=["1", "2", "3", "4", "5"])
        
        if choice == '1':
            tampilkan_log()
        elif choice == '2':
            reset_log()
        elif choice == '3':
            restock_produk()
        elif choice == '4':
            status_sistem()
        elif choice == '5':
            break

def tampilkan_log():
    """Display system logs"""
    console.clear()
    console.print(Panel.fit("📝 [bold cyan]LOG SISTEM[/bold cyan]", border_style="yellow"))
    
    try:
        if not os.path.exists('data/system_log.txt'):
            console.print("[yellow]Log sistem belum tersedia.[/yellow]")
        else:
            with open('data/system_log.txt', 'r') as f:
                log_content = f.read()
                if log_content.strip():
                    console.print(log_content)
                else:
                    console.print("[yellow]Log sistem kosong.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error membaca log: {e}[/red]")
    
    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def reset_log():
    """Reset system logs"""
    console.clear()
    console.print(Panel.fit("🗑️ [bold cyan]RESET LOG SISTEM[/bold cyan]", border_style="yellow"))
    
    confirm = Prompt.ask("Apakah Anda yakin ingin me-reset log sistem? (y/n)", choices=["y", "n"], default="n")
    
    if confirm.lower() == "y":
        try:
            log_dir = os.path.dirname('data/system_log.txt')
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            with open('data/system_log.txt', 'w') as f:
                pass  # Just create an empty file
                
            console.print("[green]✅ Log sistem berhasil di-reset![/green]")
            log_event("Log sistem di-reset oleh teknisi")
        except Exception as e:
            console.print(f"[red]Error saat me-reset log: {e}[/red]")
    else:
        console.print("[yellow]Reset log dibatalkan.[/yellow]")
    
    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def restock_produk():
    """Restock products"""
    console.clear()
    console.print(Panel.fit("📦 [bold cyan]RESTOCK PRODUK[/bold cyan]", border_style="yellow"))
    
    products = load_json("data/products.json")
    
    if not products:
        console.print("[yellow]Tidak ada produk tersedia.[/yellow]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    # Display products with stock levels
    console.print("[bold]Stok Produk Saat Ini:[/bold]\n")
    for idx, product in enumerate(products):
        stock_style = "green" if product['stock'] > 5 else "yellow" if product['stock'] > 0 else "red"
        console.print(f"{idx+1}. {product['name']} (ID: {product['id']}) - Stok: [{stock_style}]{product['stock']}[/{stock_style}]")
    
    try:
        product_idx = int(Prompt.ask("\n[yellow]Pilih nomor produk untuk restock[/yellow]")) - 1
        
        if product_idx < 0 or product_idx >= len(products):
            raise ValueError("Indeks produk tidak valid")
        
        selected_product = products[product_idx]
        console.print(f"\n[bold]Restock untuk:[/bold] {selected_product['name']}")
        console.print(f"[bold]Stok saat ini:[/bold] {selected_product['stock']}")
        
        additional_stock = int(Prompt.ask("[yellow]Tambahan stok[/yellow]"))
        if additional_stock < 0:
            raise ValueError("Stok tambahan tidak boleh negatif")
        
        # Update stock
        products[product_idx]['stock'] += additional_stock
        save_json("data/products.json", products)
        
        console.print(f"\n[green]✅ Stok {selected_product['name']} berhasil ditambah menjadi {products[product_idx]['stock']}![/green]")
        log_event(f"Teknisi menambah stok {selected_product['name']} sebanyak {additional_stock} unit (total: {products[product_idx]['stock']})")
    except ValueError as e:
        console.print(f"[red]❌ Input tidak valid: {e}[/red]")
    
    Prompt.ask("\nTekan Enter untuk melanjutkan...")