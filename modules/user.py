from modules.product_manager import get_all_products, update_stock
from modules.transaction_manager import record_transaction
from modules.utils import log_event, load_json, save_json
from modules.structures.queue import Queue
from modules.structures.stack import TransactionStack
import time
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from modules.utils import load_json, save_json, log_event
import time, os
from datetime import datetime
import uuid
import random

# Inisialisasi console untuk output yang lebih baik
console = Console()

timestamp = datetime.now()
# Global variable untuk menyimpan user yang sedang login
CURRENT_USER = None
transaction_stack = TransactionStack()
console = Console()
stack_uang = []

def hitung_kembalian_greedy(jumlah_kembalian):
    """
    Menghitung kembalian dengan algoritma greedy
    Return: dictionary berisi pecahan uang dan jumlahnya
    """
    # Definisikan pecahan uang Rupiah (dalam rupiah)
    pecahan = [100000, 50000, 20000, 10000, 5000, 2000, 1000, 500, 200, 100]
    hasil = {}
    
    # Algoritma greedy untuk menghitung kembalian
    sisa = jumlah_kembalian
    for nilai in pecahan:
        if sisa >= nilai:
            jumlah = sisa // nilai
            hasil[nilai] = jumlah
            sisa = sisa % nilai
    
    return hasil

def tampilkan_rincian_kembalian(kembalian):
    """Menampilkan rincian kembalian dalam bentuk pecahan mata uang"""
    console.print("\n[bold cyan]Rincian Kembalian:[/bold cyan]")
    
    # Hitung kembalian dengan algoritma greedy
    hasil_kembalian = hitung_kembalian_greedy(kembalian)
    
    # Tampilkan rincian kembalian
    if hasil_kembalian:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Pecahan", style="yellow")
        table.add_column("Jumlah", style="green", justify="right")
        table.add_column("Total", style="cyan", justify="right")
        
        for pecahan, jumlah in sorted(hasil_kembalian.items(), reverse=True):
            total = pecahan * jumlah
            table.add_row(
                f"Rp {pecahan:,}".replace(',', '.'),
                str(jumlah),
                f"Rp {total:,}".replace(',', '.')
            )
        
        console.print(table)
    else:
        console.print("[yellow]Tidak ada kembalian.[/yellow]")
def generate_transaction_id():
    """Generate unique transaction ID"""
    # Format: TX-YYYYMMDD-RANDOM
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices('0123456789', k=4))
    return f"TX-{date_part}-{random_part}"

def confirm_prompt(message):
    """Custom confirmation prompt"""
    while True:
        response = Prompt.ask(f"{message} (y/n)").lower()
        if response in ('y', 'yes'):
            return True
        elif response in ('n', 'no'):
            return False
        console.print("[red]Masukkan y atau n![/red]")

def tampilkan_produk(hide_id=False):
    """Menampilkan daftar produk yang tersedia"""
    console.clear()
    console.print(Panel.fit("🛒 [bold cyan]KATALOG PRODUK[/bold cyan]", border_style="yellow"))
    
    products = load_json("data/products.json")
    
    if not products:
        console.print("[yellow]Tidak ada produk tersedia.[/yellow]")
        return []
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("No.", style="cyan", width=5)
    if not hide_id:
        table.add_column("ID", style="cyan")
    table.add_column("Nama Produk", style="green")
    table.add_column("Harga (Rp)", style="yellow", justify="right")
    table.add_column("Stok", style="magenta", justify="center")
    
    for idx, product in enumerate(products, 1):
        stock_style = "green" if product['stock'] > 5 else "yellow" if product['stock'] > 0 else "red"
        stock_text = f"[{stock_style}]{str(product['stock'])}[/{stock_style}]"
        
        # Buat baris untuk ditambahkan ke tabel
        row = [str(idx)]
        if not hide_id:
            row.append(str(product['id']))
        row.extend([
            str(product['name']),
            f"{int(product['price']):,}".replace(',', '.'),
            stock_text
        ])
        
        # Tambahkan baris ke tabel
        table.add_row(*row)
    
    console.print(table)
    console.print()
    return products  # Mengembalikan daftar produk untuk digunakan fungsi lain

def user_menu(username):
    console.print(f"\n[cyan]Selamat datang, {username}![/cyan]")
    while True:
        console.clear()
        console.print(Panel.fit("🛒 [bold cyan]MODE PEMBELI[/bold cyan]", border_style="green"))

        console.print("[1] Lihat Produk")
        console.print("[2] Beli Produk")
        console.print("[3] Kembali ke Menu Utama")

        choice = Prompt.ask("\n[bold yellow]Pilih menu[/bold yellow]", choices=["1", "2", "3"])

        if choice == '1':
            tampilkan_produk()
            Prompt.ask("\nTekan Enter untuk melanjutkan...")
        elif choice == '2':
            beli_produk(username)
        elif choice == '3':
            break

def beli_produk(username):
    """Fungsi untuk membeli produk dengan fitur undo dan algoritma greedy"""
    console.clear()
    console.print(Panel.fit("🛍️ [bold cyan]BELI PRODUK[/bold cyan]", border_style="yellow"))

    # Bersihkan stack transaksi sementara
    transaction_stack.clear()

    # Tampilkan daftar produk (sembunyikan ID)
    products = tampilkan_produk(hide_id=True)
    if not products:
        console.print("[yellow]Tidak ada produk tersedia untuk dibeli.[/yellow]")
        Prompt.ask("\nTekan Enter untuk kembali...")
        return
    
    # Tambahkan opsi kembali
    console.print("[blue]Ketik 'kembali' untuk membatalkan pembelian[/blue]")
    
    # Meminta input berdasarkan nomor produk bukan ID
    nomor_input = Prompt.ask("\n[yellow]Masukkan nomor produk yang ingin dibeli[/yellow]")
    
    # Cek jika pengguna ingin kembali
    if nomor_input.lower() == 'kembali':
        console.print("[yellow]Pembelian dibatalkan.[/yellow]")
        Prompt.ask("\nTekan Enter untuk kembali...")
        return
    
    try:
        nomor = int(nomor_input)
        if nomor < 1 or nomor > len(products):
            console.print("[bold red]Nomor produk tidak valid![/bold red]")
            Prompt.ask("\nTekan Enter untuk kembali...")
            return
        
        # Ambil produk berdasarkan nomor (indeks)
        product_found = products[nomor - 1]
        
        # Simpan pilihan produk ke stack
        transaction_stack.push({
            "step": "product_selection",
            "product": product_found
        })
        
    except ValueError:
        console.print("[bold red]Masukkan nomor produk dalam bentuk angka![/bold bold]")
        Prompt.ask("\nTekan Enter untuk kembali...")
        return

    if product_found['stock'] <= 0:
        console.print("[bold red]Maaf, stok produk habis![/bold red]")
        Prompt.ask("\nTekan Enter untuk kembali...")
        return

    console.print(f"\n[bold]Detail Produk:[/bold]")
    console.print(f"Nama: [green]{product_found['name']}[/green]")
    console.print(f"Harga: [yellow]Rp {int(product_found['price']):,}[/yellow]".replace(',', '.'))
    console.print(f"Stok tersedia: [cyan]{product_found['stock']}[/cyan]")

    # Tambahkan opsi untuk kembali saat input jumlah
    console.print("\n[blue]Ketik '0' untuk membatalkan pembelian[/blue]")
    console.print("[blue]Ketik 'undo' untuk kembali ke pilihan produk[/blue]")
    
    # Loop utama untuk proses pembelian
    while True:  # Main transaction loop
        # === INPUT JUMLAH ===
        while True:
            jumlah_input = Prompt.ask("[yellow]Jumlah yang ingin dibeli[/yellow]")
                
            # Cek jika pengguna ingin kembali
            if jumlah_input == '0':
                console.print("[yellow]Pembelian dibatalkan.[/yellow]")
                Prompt.ask("\nTekan Enter untuk kembali...")
                return
            
            # Fitur undo dengan stack
            if jumlah_input.lower() == 'undo':
                transaction_stack.pop()  # Hapus pemilihan produk
                return beli_produk(username)  # Mulai ulang proses
            
            try:
                jumlah = int(jumlah_input)
                if jumlah <= 0:
                    console.print("[red]Jumlah harus lebih dari 0![/red]")
                    continue
                if jumlah > product_found['stock']:
                    console.print(f"[red]Stok tidak cukup! Stok tersedia: {product_found['stock']}[/red]")
                    continue
                
                # Simpan jumlah pembelian ke stack
                transaction_stack.push({
                    "step": "quantity_selection",
                    "quantity": jumlah
                })
                break
            except ValueError:
                console.print("[red]Masukkan jumlah dalam angka![/red]")

        total_harga = jumlah * product_found['price']

        console.print(f"\n[bold]Total Harga: [yellow]Rp {total_harga:,}[/yellow][/bold]".replace(',', '.'))
        
        # === INPUT PEMBAYARAN ===
        console.print("\n[blue]Ketik 'batal' untuk membatalkan pembelian[/blue]")
        console.print("[blue]Ketik 'undo' untuk mengubah jumlah pembelian[/blue]")
        
        # Flag untuk melacak apakah perlu kembali ke input jumlah
        kembali_ke_jumlah = False
        
        # Input jumlah uang
        while True:
            if kembali_ke_jumlah:
                break  # Keluar dari loop pembayaran untuk kembali ke loop jumlah
                
            uang_input = Prompt.ask("[yellow]Masukkan jumlah uang[/yellow]")
                
            # Cek jika pengguna ingin kembali
            if uang_input.lower() == 'batal':
                console.print("[yellow]Pembelian dibatalkan.[/yellow]")
                Prompt.ask("\nTekan Enter untuk kembali...")
                return
            
            # Fitur undo untuk kembali ke input jumlah
            if uang_input.lower() == 'undo':
                transaction_stack.pop()  # Hapus jumlah pembelian
                
                # Ambil kembali produk dari stack
                product_data = transaction_stack.peek()
                product_found = product_data['product']
                
                console.print(f"\n[bold]Detail Produk:[/bold]")
                console.print(f"Nama: [green]{product_found['name']}[/green]")
                console.print(f"Harga: [yellow]Rp {int(product_found['price']):,}[/yellow]".replace(',', '.'))
                console.print(f"Stok tersedia: [cyan]{product_found['stock']}[/cyan]")
                
                # Kembali ke input jumlah
                console.print("\n[blue]Ketik '0' untuk membatalkan pembelian[/blue]")
                console.print("[blue]Ketik 'undo' untuk kembali ke pilihan produk[/blue]")
                kembali_ke_jumlah = True  # Set flag untuk kembali ke input jumlah
                break  # Keluar dari loop pembayaran
                
            try:
                uang = int(uang_input)
                if uang < total_harga:
                    console.print(f"[red]Uang tidak cukup! Total harga: Rp {total_harga:,}[/red]".replace(',', '.'))
                    continue
                    
                # Simpan jumlah uang ke stack
                transaction_stack.push({
                    "step": "payment",
                    "amount": uang
                })
                break
            except ValueError:
                console.print("[red]Masukkan jumlah uang dalam angka![/red]")
        
        # Jika perlu kembali ke input jumlah, lanjutkan loop utama
        if kembali_ke_jumlah:
            continue
        
        # Hitung kembalian
        kembalian = uang - total_harga
        
        # Tampilkan detail pembayaran
        console.print(f"\n[bold]Uang Anda: [yellow]Rp {uang:,}[/yellow][/bold]".replace(',', '.'))
        console.print(f"[bold]Total Harga: [yellow]Rp {total_harga:,}[/yellow][/bold]".replace(',', '.'))
        console.print(f"[bold]Kembalian: [yellow]Rp {kembalian:,}[/yellow][/bold]".replace(',', '.'))
        
        # Tampilkan rincian kembalian menggunakan algoritma greedy
        tampilkan_rincian_kembalian(kembalian)
        
        # === KONFIRMASI FINAL ===
        console.print("\n[blue]Ketik 'y' untuk konfirmasi, 'n' untuk batal, atau 'undo' untuk mengubah jumlah uang[/blue]")
        konfirmasi = Prompt.ask("Konfirmasi pembelian?", choices=["y", "n", "undo"], default="n")

        if konfirmasi.lower() == "undo":
            # Hapus pembayaran dari stack
            transaction_stack.pop()
            
            # Ambil kembali jumlah pembelian dan produk dari stack
            quantity_data = transaction_stack.peek()
            jumlah = quantity_data['quantity']
            
            # Ambil produk lagi
            product_data = transaction_stack.items[0]
            product_found = product_data['product']
            
            total_harga = jumlah * product_found['price']
            
            console.print(f"\n[bold]Total Harga: [yellow]Rp {total_harga:,}[/yellow][/bold]".replace(',', '.'))
            
            # Kembali ke input pembayaran
            console.print("\n[blue]Ketik 'batal' untuk membatalkan pembelian[/blue]")
            console.print("[blue]Ketik 'undo' untuk mengubah jumlah pembelian[/blue]")
            continue  # Kembali ke awal loop utama untuk melanjutkan dengan pembayaran baru
            
        elif konfirmasi.lower() == "y":
            try:
                # Ambil data dari stack
                payment_data = transaction_stack.pop()
                quantity_data = transaction_stack.pop()
                product_data = transaction_stack.pop()
                
                uang = payment_data['amount']
                jumlah = quantity_data['quantity']
                product_found = product_data['product']
                
                # Kurangi stok
                product_found['stock'] -= jumlah
                save_json("data/products.json", products)

                # Detail kembalian dalam bentuk pecahan
                detail_kembalian = hitung_kembalian_greedy(kembalian)
                
                # Catat transaksi
                transaction = {
                    "id": str(int(time.time())),
                    "username": username,
                    "product_id": product_found["id"],
                    "product_name": product_found["name"],
                    "quantity": jumlah,
                    "total_price": total_harga,
                    "payment_amount": uang,
                    "change_amount": kembalian,
                    "change_details": detail_kembalian,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                transactions = load_json("data/transactions.json")
                if transactions is None:
                    transactions = []
                transactions.append(transaction)
                save_json("data/transactions.json", transactions)

                console.print("[bold green]Pembelian berhasil![/bold green]")
                log_event(f"User {username} membeli {jumlah} {product_found['name']}")
                break  # Keluar dari loop utama setelah transaksi selesai
                
            except Exception as e:
                console.print(f"[bold red]Terjadi kesalahan: {str(e)}[/bold red]")
                break  # Keluar dari loop utama jika ada kesalahan
        else:
            console.print("[yellow]Pembelian dibatalkan.[/yellow]")
            break  # Keluar dari loop utama jika transaksi dibatalkan

    Prompt.ask("\nTekan Enter untuk kembali...")