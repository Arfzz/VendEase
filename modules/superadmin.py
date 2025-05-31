from fpdf import FPDF
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from modules.utils import load_json, save_json, log_event, hash_password
import datetime
import os

console = Console()

def superadmin_menu():
    """Super Admin menu for managing users and system configuration"""
    while True:
        console.clear()
        console.print(Panel.fit("👑 [bold cyan]SUPER ADMIN DASHBOARD[/bold cyan]", border_style="magenta"))
        
        console.print("[1] Kelola Pengguna")
        console.print("[2] Laporan Transaksi Lengkap")
        console.print("[3] Reset Sistem")
        console.print("[4] Lihat Log Sistem")
        console.print("[5] Logout")
        
        choice = Prompt.ask("\n[bold yellow]Pilih menu[/bold yellow]", choices=["1", "2", "3", "4", "5"])
        
        if choice == '1':
            kelola_pengguna()
        elif choice == '2':
            laporan_transaksi_lengkap()
        elif choice == '3':
            reset_sistem()
        elif choice == '4':
            tampilkan_log()
        elif choice == '5':
            break

def kelola_pengguna():
    """Manage system users"""
    while True:
        console.clear()
        console.print(Panel.fit("👥 [bold cyan]KELOLA PENGGUNA[/bold cyan]", border_style="magenta"))
        
        console.print("[1] Lihat Daftar Pengguna")
        console.print("[2] Tambah Pengguna")
        console.print("[3] Edit Pengguna")
        console.print("[4] Hapus Pengguna")
        console.print("[5] Kembali")
        
        choice = Prompt.ask("\n[bold yellow]Pilih menu[/bold yellow]", choices=["1", "2", "3", "4", "5"])
        
        if choice == '1':
            lihat_pengguna()
        elif choice == '2':
            tambah_pengguna()
        elif choice == '3':
            edit_pengguna()
        elif choice == '4':
            hapus_pengguna()
        elif choice == '5':
            break

def lihat_pengguna():
    """View all users"""
    console.clear()
    console.print(Panel.fit("👥 [bold cyan]DAFTAR PENGGUNA[/bold cyan]", border_style="magenta"))
    
    users = load_json("data/users.json")
    
    if not users:
        console.print("[yellow]Tidak ada pengguna terdaftar.[/yellow]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("No")
    table.add_column("Username")
    table.add_column("Role")
    
    for idx, user in enumerate(users):
        role_style = {
            "user": "green",
            "admin": "blue",
            "technician": "yellow",
            "superadmin": "magenta"
        }.get(user['role'], "white")
        
        table.add_row(
            str(idx + 1),
            user['username'],
            f"[{role_style}]{user['role'].upper()}[/{role_style}]"
        )
    
    console.print(table)
    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def tambah_pengguna():
    """Add a new user"""
    console.clear()
    console.print(Panel.fit("➕ [bold cyan]TAMBAH PENGGUNA[/bold cyan]", border_style="magenta"))
    
    users = load_json("data/users.json")
    
    username = Prompt.ask("[yellow]Username[/yellow]")
    
    # Check if username already exists
    if any(user['username'] == username for user in users):
        console.print("[red]❌ Username sudah digunakan![/red]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    password = Prompt.ask("[yellow]Password[/yellow]", password=False)
    
    console.print("\n[bold]Pilih role pengguna:[/bold]")
    console.print("[1] User (Pembeli)")
    console.print("[2] Admin")
    console.print("[3] Teknisi")
    console.print("[4] Super Admin")
    
    role_choice = Prompt.ask("\n[yellow]Pilih role[/yellow]", choices=["1", "2", "3", "4"])
    
    role_map = {
        "1": "user",
        "2": "admin",
        "3": "technician",
        "4": "superadmin"
    }
    
    role = role_map[role_choice]
    
    # Add new user
    users.append({
        "username": username,
        "password": hash_password(password),
        "role": role
    })
    
    save_json("data/users.json", users)
    console.print(f"\n[green]✅ Pengguna '{username}' dengan role {role.upper()} berhasil ditambahkan![/green]")
    log_event(f"Super Admin menambahkan pengguna '{username}' dengan role {role}")
    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def edit_pengguna():
    """Edit an existing user"""
    console.clear()
    console.print(Panel.fit("✏️ [bold cyan]EDIT PENGGUNA[/bold cyan]", border_style="magenta"))
    
    users = load_json("data/users.json")
    
    if not users:
        console.print("[yellow]Tidak ada pengguna terdaftar.[/yellow]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    # Display users
    table = Table(show_header=True, header_style="bold")
    table.add_column("No")
    table.add_column("Username")
    table.add_column("Role")
    
    for idx, user in enumerate(users):
        role_style = {
            "user": "green",
            "admin": "blue",
            "technician": "yellow",
            "superadmin": "magenta"
        }.get(user['role'], "white")
        
        table.add_row(
            str(idx + 1),
            user['username'],
            f"[{role_style}]{user['role'].upper()}[/{role_style}]"
        )
    
    console.print(table)
    
    # Get user index to edit
    try:
        user_idx = int(Prompt.ask("\n[yellow]Pilih nomor pengguna yang akan diedit[/yellow]")) - 1
        
        if user_idx < 0 or user_idx >= len(users):
            raise ValueError("Indeks pengguna tidak valid")
        
        user = users[user_idx]
        console.print(f"\n[bold]Edit pengguna:[/bold] {user['username']}")
        
        # Change username
        new_username = Prompt.ask("[yellow]Username baru[/yellow]", default=user['username'])
        
        # Check if new username already exists (if changed)
        if new_username != user['username'] and any(u['username'] == new_username for u in users):
            console.print("[red]❌ Username sudah digunakan![/red]")
            Prompt.ask("\nTekan Enter untuk melanjutkan...")
            return
        
        # Change password?
        change_password = Prompt.ask("Ubah password? (y/n)", choices=["y", "n"], default="n")
        new_password = None
        
        if change_password.lower() == "y":
            new_password = Prompt.ask("[yellow]Password baru[/yellow]", password=False)
        
        # Change role
        console.print("\n[bold]Role saat ini:[/bold] " + user['role'].upper())
        console.print("[bold]Pilih role baru:[/bold]")
        console.print("[1] User (Pembeli)")
        console.print("[2] Admin")
        console.print("[3] Teknisi")
        console.print("[4] Super Admin")
        console.print("[5] Tidak berubah")
        
        role_choice = Prompt.ask("\n[yellow]Pilih role[/yellow]", choices=["1", "2", "3", "4", "5"])
        
        role_map = {
            "1": "user",
            "2": "admin",
            "3": "technician",
            "4": "superadmin",
            "5": user['role']
        }
        
        new_role = role_map[role_choice]
        
        # Confirm changes
        console.print("\n[bold]Perubahan yang akan dilakukan:[/bold]")
        if new_username != user['username']:
            console.print(f"- Username: {user['username']} -> {new_username}")
        if new_password:
            console.print("- Password: [diubah]")
        if new_role != user['role']:
            console.print(f"- Role: {user['role'].upper()} -> {new_role.upper()}")
        
        confirm = Prompt.ask("\nSimpan perubahan? (y/n)", choices=["y", "n"], default="n")
        
        if confirm.lower() == "y":
            old_username = user['username']
            users[user_idx]['username'] = new_username
            
            if new_password:
                users[user_idx]['password'] = hash_password(new_password)
            
            users[user_idx]['role'] = new_role
            
            save_json("data/users.json", users)
            console.print(f"\n[green]✅ Pengguna berhasil diperbarui![/green]")
            log_event(f"Super Admin mengedit pengguna dari '{old_username}' menjadi '{new_username}' dengan role {new_role}")
        else:
            console.print("\n[yellow]Pengeditan dibatalkan.[/yellow]")
    except ValueError as e:
        console.print(f"[red]❌ Input tidak valid: {e}[/red]")
    
    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def hapus_pengguna():
    """Delete a user"""
    console.clear()
    console.print(Panel.fit("🗑️ [bold cyan]HAPUS PENGGUNA[/bold cyan]", border_style="magenta"))
    
    users = load_json("data/users.json")
    
    if not users:
        console.print("[yellow]Tidak ada pengguna terdaftar.[/yellow]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    # Display users
    table = Table(show_header=True, header_style="bold")
    table.add_column("No")
    table.add_column("Username")
    table.add_column("Role")
    
    for idx, user in enumerate(users):
        role_style = {
            "user": "green",
            "admin": "blue",
            "technician": "yellow",
            "superadmin": "magenta"
        }.get(user['role'], "white")
        
        table.add_row(
            str(idx + 1),
            user['username'],
            f"[{role_style}]{user['role'].upper()}[/{role_style}]"
        )
    
    console.print(table)
    
    # Get user index to delete
    try:
        user_idx = int(Prompt.ask("\n[yellow]Pilih nomor pengguna yang akan dihapus[/yellow]")) - 1
        
        if user_idx < 0 or user_idx >= len(users):
            raise ValueError("Indeks pengguna tidak valid")
        
        user = users[user_idx]
        
        # Check if this is the last superadmin
        if user['role'] == "superadmin" and sum(1 for u in users if u['role'] == "superadmin") <= 1:
            console.print("[red]❌ Tidak dapat menghapus Super Admin terakhir![/red]")
            Prompt.ask("\nTekan Enter untuk melanjutkan...")
            return
        
        # Confirm deletion
        confirm = Prompt.ask(f"\nApakah Anda yakin ingin menghapus pengguna '{user['username']}'? (y/n)", choices=["y", "n"], default="n")
        
        if confirm.lower() == "y":
            deleted_user = users.pop(user_idx)
            save_json("data/users.json", users)
            console.print(f"\n[green]✅ Pengguna '{deleted_user['username']}' berhasil dihapus![/green]")
            log_event(f"Super Admin menghapus pengguna '{deleted_user['username']}' dengan role {deleted_user['role']}")
        else:
            console.print("\n[yellow]Penghapusan dibatalkan.[/yellow]")
    except ValueError as e:
        console.print(f"[red]❌ Input tidak valid: {e}[/red]")
    
    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def laporan_transaksi_lengkap():
    """Generate detailed transaction reports"""
    console.clear()
    console.print(Panel.fit("📊 [bold cyan]LAPORAN TRANSAKSI LENGKAP[/bold cyan]", border_style="magenta"))
    
    transactions = load_json("data/transactions.json")
    
    if not transactions:
        console.print("[yellow]Belum ada transaksi tercatat.[/yellow]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    # Display summary
    total_sales = sum(t.get('total_price', t.get('total', 0)) for t in transactions)
    total_transactions = len(transactions)
    
    console.print(f"[bold]Total Transaksi:[/bold] {total_transactions}")
    console.print(f"[bold]Total Pendapatan:[/bold] Rp{total_sales:,}")
    
    # Product-based summary
    products = {}
    for t in transactions:
        product_name = t.get('product_name', t.get('produk', 'Unknown'))
        quantity = t.get('quantity', 1)
        products[product_name] = products.get(product_name, 0) + quantity
    
    console.print("\n[bold]Ringkasan per Produk:[/bold]")
    
    product_table = Table(show_header=True, header_style="bold")
    product_table.add_column("Produk")
    product_table.add_column("Jumlah Terjual")
    product_table.add_column("Persentase")
    
    total_quantity = sum(products.values())
    for product, count in sorted(products.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_quantity) * 100 if total_quantity else 0
        product_table.add_row(
            product,
            str(count),
            f"{percentage:.1f}%"
        )
    
    console.print(product_table)
    
    # Display full transaction data
    console.print("\n[bold]Detail Semua Transaksi:[/bold]")
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim", width=12)
    table.add_column("Waktu", width=20)
    table.add_column("Produk")
    table.add_column("Harga (Rp)")
    table.add_column("Uang Masuk (Rp)")
    table.add_column("Kembalian (Rp)")
    
    for t in transactions:
        table.add_row(
            t.get('id', 'N/A'),
            t.get('timestamp', t.get('datetime', 'N/A')),
            t.get('product_name', t.get('produk', 'N/A')),
            f"{t.get('total_price', t.get('total', 0)):,}",
            f"{t.get('payment_amount', t.get('money_input', 0)):,}",
            f"{t.get('change_amount', t.get('change', 0)):,}"
        )
    
    console.print(table)
    log_event("Super Admin mengakses laporan transaksi lengkap")
    Prompt.ask("\nTekan Enter untuk melanjutkan...")


def reset_sistem():
    """Reset system data"""
    console.clear()
    console.print(Panel.fit("🔄 [bold cyan]RESET SISTEM[/bold cyan]", border_style="magenta"))
    
    console.print("[bold red]⚠️ PERINGATAN: Ini akan menghapus semua data sistem kecuali akun pengguna![/bold red]")
    console.print("Data yang akan dihapus:")
    console.print("- Semua data transaksi")
    console.print("- Reset stok produk ke nilai default")
    console.print("- Log sistem")
    
    confirm = Prompt.ask("\nApakah Anda YAKIN ingin mereset sistem? (ketik 'RESET' untuk konfirmasi)")
    
    if confirm == "RESET":
        # Reset transactions
        save_json("data/transactions.json", [])
        
        # Reset products to default
        default_products = [
            {
                "id": "A1",
                "name": "Mineral Water",
                "price": 5000,
                "stock": 20
            },
            {
                "id": "B2",
                "name": "Soda",
                "price": 8000,
                "stock": 15
            },
            {
                "id": "C3",
                "name": "Coffee",
                "price": 10000,
                "stock": 10
            }
        ]
        save_json("data/products.json", default_products)
        
        # Reset log
        log_event("Super Admin melakukan reset sistem")
        with open('data/system_log.txt', 'w') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Sistem di-reset oleh Super Admin\n")
        
        console.print("\n[bold green]✅ Sistem berhasil di-reset![/bold green]")
    else:
        console.print("\n[yellow]Reset sistem dibatalkan.[/yellow]")
    
    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def tampilkan_log():
    """Display system logs for Super Admin"""
    console.clear()
    console.print(Panel.fit("📝 [bold cyan]LOG SISTEM[/bold cyan]", border_style="magenta"))
    
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