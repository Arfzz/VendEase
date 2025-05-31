from fpdf import FPDF
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.prompt import Confirm
from rich.markdown import Markdown
from modules.structures.queue import TransactionQueue, NotificationQueue
from modules.utils import load_json, save_json, log_event
from modules.structures.linkedList import TransactionNode, TransactionList
from modules.transaction_manager import get_transactions_as_linkedlist, filter_transactions_by_date
from modules.queue_manager import (
    init_queues, transaction_queue, notification_queue, 
    check_stock_levels, process_transaction_queue, get_notification_count
)
import datetime
import os

console = Console()

def get_next_product_id(products):
    """Generates the next auto-incremented product ID."""
    if not products:
        return 1
    max_id = 0
    for product in products:
        try:
            current_id = int(product.get('id', 0))
            if current_id > max_id:
                max_id = current_id
        except ValueError:
            # Handle cases where an ID might not be a valid integer, though ideally they should be
            console.print(f"[yellow]Peringatan: ID produk '{product.get('id')}' tidak valid dan akan diabaikan dalam penentuan ID otomatis.[/yellow]")
            continue
    return max_id + 1

def admin_menu():
    """Admin dashboard for managing products and viewing transactions"""
    # Initialize queues when entering admin dashboard
    init_queues()
    
    while True:
        console.clear()
        
        # Check stock levels and get unread notification count
        check_stock_levels()
        unread_count = get_notification_count()
        
        # Show notification badge if there are unread notifications
        notification_badge = f" [bold red]({unread_count})[/bold red]" if unread_count > 0 else ""
        
        console.print(Panel.fit("👨‍💼 [bold cyan]ADMIN DASHBOARD[/bold cyan]", border_style="blue"))
        
        console.print("[1] Lihat Produk")
        console.print("[2] Tambah Produk")
        console.print("[3] Edit Produk")
        console.print("[4] Hapus Produk")
        console.print("[5] Laporan Transaksi")
        console.print(f"[6] Notifikasi{notification_badge}")
        console.print("[7] Kelola Antrian Transaksi")
        console.print("[8] Logout")
        
        choice = Prompt.ask("\n[bold yellow]Pilih menu[/bold yellow]", 
                         choices=["1", "2", "3", "4", "5", "6", "7", "8"])
        
        if choice == '1':
            lihat_produk()
        elif choice == '2':
            tambah_produk()
        elif choice == '3':
            edit_produk()
        elif choice == '4':
            hapus_produk()
        elif choice == '5':
            laporan_transaksi()
        elif choice == '6':
            manage_notifications()
        elif choice == '7':
            manage_transaction_queue()
        elif choice == '8':
            break

def lihat_produk():
    """Display all products in a table"""
    console.clear()
    console.print(Panel.fit("📋 [bold cyan]DAFTAR PRODUK[/bold cyan]", border_style="blue"))
    
    products = load_json("data/products.json")
    
    if not products:
        console.print("[yellow]Tidak ada produk tersedia saat ini.[/yellow]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Nama Produk")
    table.add_column("Harga (Rp)")
    table.add_column("Stok")
    table.add_column("Status")
    
    for product in products:
        stock = int(product['stock'])
        if stock <= 0:
            stock_style = "red"
            status = "[bold red]Habis[/bold red]"
        elif stock <= 5:
            stock_style = "yellow"
            status = "[bold yellow]Menipis[/bold yellow]"
        else:
            stock_style = "green"
            status = "[bold green]Tersedia[/bold green]"
            
        table.add_row(
            str(product['id']),
            product['name'],
            f"{product['price']:,}",
            f"[{stock_style}]{stock}[/{stock_style}]",
            status
        )
    
    console.print(table)
    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def tambah_produk():
    """Add a new product with auto-incremented ID"""
    console.clear()
    console.print(Panel.fit("➕ [bold cyan]TAMBAH PRODUK[/bold cyan]", border_style="blue"))

    products = load_json("data/products.json")

    # Generate new product ID automatically
    pid = get_next_product_id(products)
    console.print(f"[info]ID Produk otomatis: {pid}[/info]")

    name = Prompt.ask("[yellow]Nama Produk[/yellow]")
    if not name.strip():
        console.print("[red]❌ Nama Produk tidak boleh kosong.[/red]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return

    try:
        price = int(Prompt.ask("[yellow]Harga (Rp)[/yellow]"))
        if price <= 0:
            raise ValueError("Harga harus lebih dari 0")

        stock = int(Prompt.ask("[yellow]Stok[/yellow]"))
        if stock < 0:
            raise ValueError("Stok tidak boleh negatif")
    except ValueError as e:
        console.print(f"[red]❌ Input tidak valid: {e}[/red]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return

    # Add new product
    products.append({
        "id": pid, # Store ID as integer
        "name": name,
        "price": price,
        "stock": stock
    })

    save_json("data/products.json", products)
    console.print(f"\n[green]✅ Produk '{name}' (ID: {pid}) berhasil ditambahkan![/green]")
    log_event(f"Admin menambahkan produk {name} (ID: {pid}) dengan harga Rp{price} dan stok {stock}")

    # Check if stock is low and add notification
    if stock <= 5:
        from modules.queue_manager import notification_queue, save_queues # Keep import local if only used here
        notification_queue.add_stock_notification(str(pid), name, stock, 5) # Ensure ID is string for notification if needed by that function
        save_queues()
        console.print(f"[yellow]⚠️ Peringatan: Stok produk ini menipis ({stock} tersisa)[/yellow]")

    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def edit_produk():
    """Edit an existing product"""
    console.clear()
    console.print(Panel.fit("✏️ [bold cyan]EDIT PRODUK[/bold cyan]", border_style="blue"))
    
    products = load_json("data/products.json")
    
    if not products:
        console.print("[yellow]Tidak ada produk tersedia untuk diedit.[/yellow]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    # Display products
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Nama Produk")
    table.add_column("Harga (Rp)")
    table.add_column("Stok")
    
    for product in products:
        stock_style = "green" if int(product['stock']) > 0 else "red"
        table.add_row(
            str(product['id']),
            product['name'],
            f"{product['price']:,}",
            f"[{stock_style}]{product['stock']}[/{stock_style}]"
        )
    
    console.print(table)
    
    # Get product ID to edit
    pid = Prompt.ask("\n[yellow]Masukkan ID produk yang akan diedit[/yellow]")
    
    # Find product
    product_index = None
    for idx, product in enumerate(products):
        if str(product['id']) == str(pid):
            product_index = idx
            break
    
    if product_index is None:
        console.print("[red]❌ Produk tidak ditemukan![/red]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    # Get new values
    product = products[product_index]
    console.print(f"\n[bold]Edit Produk: {product['name']}[/bold]")
    
    name = Prompt.ask("[yellow]Nama Produk[/yellow]", default=product['name'])
    
    try:
        price = int(Prompt.ask(f"[yellow]Harga (Rp)[/yellow]", default=str(product['price'])))
        if price <= 0:
            raise ValueError("Harga harus lebih dari 0")
            
        old_stock = int(product['stock'])
        stock = int(Prompt.ask(f"[yellow]Stok[/yellow]", default=str(old_stock)))
        if stock < 0:
            raise ValueError("Stok tidak boleh negatif")
    except ValueError as e:
        console.print(f"[red]❌ Input tidak valid: {e}[/red]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    # Update product
    old_name = product['name']
    products[product_index] = {
        "id": pid,
        "name": name,
        "price": price,
        "stock": stock
    }
    
    save_json("data/products.json", products)
    console.print(f"\n[green]✅ Produk berhasil diperbarui![/green]")
    log_event(f"Admin mengedit produk dari '{old_name}' menjadi '{name}' (ID: {pid}) dengan harga Rp{price} dan stok {stock}")
    
    # Check if stock level changed and add notification if it became low
    if old_stock > 5 and stock <= 5:
        from modules.queue_manager import notification_queue, save_queues
        notification_queue.add_stock_notification(pid, name, stock, 5)
        save_queues()
        console.print(f"[yellow]⚠️ Peringatan: Stok produk ini menipis ({stock} tersisa)[/yellow]")
    
    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def hapus_produk():
    """Delete a product and re-index remaining product IDs."""
    console.clear()
    console.print(Panel.fit("🗑️ [bold cyan]HAPUS PRODUK[/bold cyan]", border_style="blue"))
    products = load_json("data/products.json")
    if not products:
        console.print("[yellow]Tidak ada produk tersedia untuk dihapus.[/yellow]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim", justify="right"); table.add_column("Nama Produk")
    table.add_column("Harga (Rp)", justify="right"); table.add_column("Stok", justify="right")
    for product in products:
        stock_style = "green" if int(product['stock']) > 0 else "red"
        table.add_row(str(product['id']), product['name'], f"{product['price']:,}",
                      f"[{stock_style}]{product['stock']}[/{stock_style}]")
    console.print(table)

    try:
        pid_to_delete = int(Prompt.ask("\n[yellow]Masukkan ID produk yang akan dihapus[/yellow]"))
    except ValueError:
        console.print("[red]❌ ID Produk harus berupa angka.[/red]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return

    product_to_delete = next((p for p in products if int(p['id']) == pid_to_delete), None)
    if not product_to_delete:
        console.print("[red]❌ Produk tidak ditemukan![/red]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return

    console.print("\n[bold red]PERINGATAN PENTING:[/bold red]")
    console.print("Menghapus produk dan mengurutkan ulang ID dapat mempengaruhi integritas data jika ID ini digunakan di tempat lain (misalnya, dalam riwayat transaksi).")
    confirm = Confirm.ask(f"\nApakah Anda yakin ingin menghapus '{product_to_delete['name']}' (ID: {pid_to_delete}) dan mengurutkan ulang semua ID produk? ", default=False)

    if confirm:
        # Hapus produk yang dipilih
        products = [p for p in products if int(p['id']) != pid_to_delete]
        
        # Urutkan ulang ID produk yang tersisa
        if products:
            console.print("[info]Menyusun ulang ID produk...[/info]")
            id_changes_log = []
            for index, product_in_list in enumerate(products):
                new_id = index + 1
                if int(product_in_list['id']) != new_id:
                    id_changes_log.append(f"Produk '{product_in_list['name']}' ID diubah dari {product_in_list['id']} ke {new_id}")
                product_in_list['id'] = new_id # ID sekarang integer
            
            if id_changes_log:
                log_event(f"Pengurutan ulang ID produk setelah penghapusan ID asal {pid_to_delete}: " + "; ".join(id_changes_log))
        
        save_json("data/products.json", products)
        console.print(f"\n[green]✅ Produk '{product_to_delete['name']}' berhasil dihapus dan ID produk telah disusun ulang![/green]")
        log_event(f"Admin menghapus produk '{product_to_delete['name']}' (ID asal: {pid_to_delete}) dan semua ID produk disusun ulang.")
    else:
        console.print("\n[yellow]Penghapusan dibatalkan.[/yellow]")
    
    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def laporan_transaksi():
    """View transaction reports using linked list"""
    console.clear()
    console.print(Panel.fit("📊 [bold cyan]LAPORAN TRANSAKSI[/bold cyan]", border_style="blue"))
    
    # Use the transaction manager to get transactions as linked list
    transaction_list = get_transactions_as_linkedlist()
    
    if not transaction_list or not transaction_list.head:
        console.print("[yellow]Belum ada transaksi tercatat.[/yellow]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    # Display transactions
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim", width=12)
    table.add_column("Waktu", width=20)
    table.add_column("Produk")
    table.add_column("Harga (Rp)")
    table.add_column("Uang Masuk (Rp)")
    table.add_column("Kembalian (Rp)")
    
    # Calculate total sales while traversing the linked list
    total_sales = 0
    current = transaction_list.head
    
    while current:
        table.add_row(
            current.transaction_id,
            current.datetime,
            current.product_name,
            f"{current.price:,}",
            f"{current.money_input:,}",
            f"{current.change:,}"
        )
        total_sales += current.price
        current = current.next
    
    console.print(table)
    console.print(f"\n[bold]Total Pendapatan:[/bold] Rp{total_sales:,}")
    
    # Offer filter options
    console.print("\n[bold]Filter Laporan:[/bold]")
    console.print("[1] Semua Transaksi")
    console.print("[2] Filter berdasarkan Produk")
    console.print("[3] Filter berdasarkan Tanggal")
    console.print("[4] Lihat Transaksi Terbaru ke Lama")
    console.print("[5] Lihat Transaksi Lama ke Terbaru")
    
    filter_choice = Prompt.ask("\n[bold yellow]Pilih filter[/bold yellow]", choices=["1", "2", "3", "4", "5"], default="1")
    
    if filter_choice == "2":
        product_name = Prompt.ask("[yellow]Masukkan nama produk[/yellow]")
        filtered_list = transaction_list.filter_by_product(product_name)
        display_filtered_transactions(filtered_list, f"Transaksi untuk Produk: {product_name}")
    elif filter_choice == "3":
        # Filter by date range
        try:
            today = datetime.datetime.now()
            default_start = today.strftime("%Y-%m-%d")
            
            start_date = Prompt.ask("[yellow]Tanggal Mulai (YYYY-MM-DD)[/yellow]", default=default_start)
            end_date = Prompt.ask("[yellow]Tanggal Akhir (YYYY-MM-DD)[/yellow]", default=default_start)
            
            # Create new linked list from filtered transactions
            filtered_data = filter_transactions_by_date(start_date, end_date)
            filtered_list = TransactionList()
            
            for t in filtered_data:
                filtered_list.append(
                    t.get('id', 'N/A'),
                    t.get('datetime', 'N/A'),
                    t.get('product_name', t.get('produk', 'Unknown')),
                    t.get('total', t.get('price', 0) * t.get('quantity', 1)),
                    t.get('money_input', 0),
                    t.get('change', 0)
                )
            
            display_filtered_transactions(filtered_list, f"Transaksi {start_date} sampai {end_date}")
        except ValueError as e:
            console.print(f"[red]Format tanggal tidak valid: {e}[/red]")
            Prompt.ask("\nTekan Enter untuk melanjutkan...")
    elif filter_choice == "4":
        # Newest to oldest (already in this order)
        display_filtered_transactions(transaction_list, "Transaksi (Terbaru ke Lama)")
    elif filter_choice == "5":
        # Reverse to get oldest to newest
        reversed_list = transaction_list.reverse()
        display_filtered_transactions(reversed_list, "Transaksi (Lama ke Terbaru)")
    
    # Ask if user wants to export the report
    if Confirm.ask("\nApakah Anda ingin mengekspor laporan ini?", default=False):
        export_transactions_report(transaction_list)
    
    Prompt.ask("\nTekan Enter untuk melanjutkan...")

def display_filtered_transactions(transaction_list, title):
    """Display filtered transactions"""
    console.clear()
    console.print(Panel.fit(f"📊 [bold cyan]{title}[/bold cyan]", border_style="blue"))
    
    if not transaction_list or not transaction_list.head:
        console.print("[yellow]Tidak ada transaksi yang sesuai dengan filter.[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim", width=12)
    table.add_column("Waktu", width=20)
    table.add_column("Produk")
    table.add_column("Harga (Rp)")
    table.add_column("Uang Masuk (Rp)")
    table.add_column("Kembalian (Rp)")
    
    total_sales = 0
    count = 0
    current = transaction_list.head
    
    while current:
        table.add_row(
            current.transaction_id,
            current.datetime,
            current.product_name,
            f"{current.price:,}",
            f"{current.money_input:,}",
            f"{current.change:,}"
        )
        total_sales += current.price
        count += 1
        current = current.next
    
    console.print(table)
    console.print(f"\n[bold]Jumlah Transaksi:[/bold] {count}")
    console.print(f"[bold]Total Pendapatan:[/bold] Rp{total_sales:,}")

def export_transactions_report(transaction_list):
    """Export transactions to a CSV file"""
    from datetime import datetime
    import csv
    import os
    
    # Ensure the exports directory exists
    if not os.path.exists("exports"):
        os.makedirs("exports")
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exports/transaksi_{timestamp}.csv"
    
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['ID', 'Waktu', 'Produk', 'Harga (Rp)', 'Uang Masuk (Rp)', 'Kembalian (Rp)'])
            
            # Write data
            current = transaction_list.head
            while current:
                writer.writerow([
                    current.transaction_id,
                    current.datetime,
                    current.product_name,
                    current.price,
                    current.money_input,
                    current.change
                ])
                current = current.next
        
        console.print(f"\n[green]✅ Laporan berhasil diekspor ke [bold]{filename}[/bold][/green]")
        log_event(f"Admin mengekspor laporan transaksi ke {filename}")
    except Exception as e:
        console.print(f"\n[red]❌ Gagal mengekspor laporan: {e}[/red]")

def manage_notifications():
    """Manage system notifications"""
    console.clear()
    console.print(Panel.fit("🔔 [bold cyan]NOTIFIKASI SISTEM[/bold cyan]", border_style="blue"))
    
    # Get notifications
    notifications = notification_queue.items
    
    if not notifications:
        console.print("[yellow]Tidak ada notifikasi saat ini.[/yellow]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    # Display notifications
    table = Table(show_header=True, header_style="bold")
    table.add_column("#", style="dim", width=5)
    table.add_column("Waktu", width=20)
    table.add_column("Jenis")
    table.add_column("Pesan")
    table.add_column("Status")
    
    for idx, notification in enumerate(notifications):
        # Format notification message based on type
        if notification['type'] == 'low_stock':
            message = f"Stok {notification['product_name']} tinggal {notification['current_stock']} (di bawah batas {notification['threshold']})"
            notif_type = "Stok Menipis"
        else:
            message = notification.get('message', 'Notifikasi sistem')
            notif_type = notification.get('type', 'Sistem').capitalize()
        
        # Format timestamp
        timestamp = notification.get('timestamp', 'N/A')
        
        # Status (read/unread)
        status = "[green]Dibaca[/green]" if notification.get('read', False) else "[yellow]Belum dibaca[/yellow]"
        
        table.add_row(
            str(idx + 1),
            timestamp,
            notif_type,
            message,
            status
        )
    
    console.print(table)
    
    # Options
    console.print("\n[bold]Opsi:[/bold]")
    console.print("[1] Tandai semua sebagai dibaca")
    console.print("[2] Tandai satu notifikasi sebagai dibaca")
    console.print("[3] Hapus semua notifikasi")
    console.print("[4] Kembali")
    
    choice = Prompt.ask("\n[bold yellow]Pilih opsi[/bold yellow]", choices=["1", "2", "3", "4"], default="4")
    
    if choice == "1":
        notification_queue.mark_all_as_read()
        console.print("[green]✅ Semua notifikasi ditandai sebagai dibaca[/green]")
        log_event("Admin menandai semua notifikasi sebagai dibaca")
    elif choice == "2":
        if notifications:
            try:
                index = int(Prompt.ask("[yellow]Masukkan nomor notifikasi[/yellow]")) - 1
                if 0 <= index < len(notifications):
                    notification_queue.mark_as_read(index)
                    console.print("[green]✅ Notifikasi ditandai sebagai dibaca[/green]")
                    log_event(f"Admin menandai notifikasi #{index+1} sebagai dibaca")
                else:
                    console.print("[red]❌ Nomor notifikasi tidak valid[/red]")
            except ValueError:
                console.print("[red]❌ Input harus berupa angka[/red]")
    elif choice == "3":
        if Confirm.ask("Apakah Anda yakin ingin menghapus semua notifikasi?", default=False):
            notification_queue.clear()
            console.print("[green]✅ Semua notifikasi dihapus[/green]")
            log_event("Admin menghapus semua notifikasi")
    
    # Save updated notifications
    from modules.queue_manager import save_queues
    save_queues()
    
    if choice != "4":
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        manage_notifications()  # Refresh the notifications screen
        
def manage_transaction_queue():
    """Manage pending transactions in the queue"""
    console.clear()
    console.print(Panel.fit("🔄 [bold cyan]ANTRIAN TRANSAKSI[/bold cyan]", border_style="blue"))
    
    # Get transactions in queue
    queue_items = transaction_queue.items
    
    if not queue_items:
        console.print("[yellow]Tidak ada transaksi dalam antrian saat ini.[/yellow]")
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        return
    
    # Display queued transactions
    table = Table(show_header=True, header_style="bold")
    table.add_column("#", style="dim", width=5)
    table.add_column("Waktu", width=20)
    table.add_column("Produk")
    table.add_column("Harga (Rp)")
    table.add_column("Uang Masuk (Rp)")
    table.add_column("Status")
    
    for idx, transaction in enumerate(queue_items):
        # Extract transaction details
        product_name = transaction.get('product_name', 'Unknown')
        price = transaction.get('price', 0)
        money_input = transaction.get('money_input', 0)
        timestamp = transaction.get('timestamp', 'N/A')
        status = transaction.get('status', 'Pending')
        
        status_display = "[yellow]Menunggu[/yellow]" if status == "Pending" else f"[blue]{status}[/blue]"
        
        table.add_row(
            str(idx + 1),
            timestamp,
            product_name,
            f"{price:,}",
            f"{money_input:,}",
            status_display
        )
    
    console.print(table)
    
    # Options
    console.print("\n[bold]Opsi:[/bold]")
    console.print("[1] Proses Semua Transaksi")
    console.print("[2] Proses Satu Transaksi")
    console.print("[3] Hapus Transaksi dari Antrian")
    console.print("[4] Kosongkan Antrian")
    console.print("[5] Kembali")
    
    choice = Prompt.ask("\n[bold yellow]Pilih opsi[/bold yellow]", choices=["1", "2", "3", "4", "5"], default="5")
    
    if choice == "1":
        # Process all transactions
        processed_count = process_transaction_queue()
        console.print(f"[green]✅ {processed_count} transaksi berhasil diproses[/green]")
        log_event(f"Admin memproses {processed_count} transaksi dari antrian")
    elif choice == "2":
        # Process single transaction
        if queue_items:
            try:
                index = int(Prompt.ask("[yellow]Masukkan nomor transaksi[/yellow]")) - 1
                if 0 <= index < len(queue_items):
                    transaction = queue_items[index]
                    # Remove from queue and process
                    transaction_queue.items.pop(index)
                    
                    # Process the transaction (simplified version of what process_transaction_queue does)
                    products = load_json("data/products.json")
                    transactions = load_json("data/transactions.json")
                    
                    # Get product details
                    product_id = transaction.get('product_id')
                    product_found = False
                    
                    for p in products:
                        if str(p['id']) == str(product_id):
                            product_found = True
                            # Ensure there's still stock (might have changed since queue was created)
                            if int(p['stock']) > 0:
                                # Update stock
                                p['stock'] = int(p['stock']) - 1
                                
                                # Add transaction to history
                                transaction['status'] = 'Completed'
                                transactions.append(transaction)
                                
                                # Save changes
                                save_json("data/products.json", products)
                                save_json("data/transactions.json", transactions)
                                
                                console.print(f"[green]✅ Transaksi untuk {transaction.get('product_name')} berhasil diproses[/green]")
                                log_event(f"Admin memproses transaksi untuk {transaction.get('product_name')}")
                            else:
                                console.print(f"[red]❌ Stok {transaction.get('product_name')} habis![/red]")
                            break
                    
                    if not product_found:
                        console.print(f"[red]❌ Produk tidak ditemukan! ID: {product_id}[/red]")
                    
                    # Save updated queue
                    from modules.queue_manager import save_queues
                    save_queues()
                else:
                    console.print("[red]❌ Nomor transaksi tidak valid[/red]")
            except ValueError:
                console.print("[red]❌ Input harus berupa angka[/red]")
    elif choice == "3":
        # Delete single transaction
        if queue_items:
            try:
                index = int(Prompt.ask("[yellow]Masukkan nomor transaksi[/yellow]")) - 1
                if 0 <= index < len(queue_items):
                    transaction = queue_items[index]
                    if Confirm.ask(f"Hapus transaksi untuk {transaction.get('product_name')}?", default=False):
                        transaction_queue.items.pop(index)
                        console.print("[green]✅ Transaksi dihapus dari antrian[/green]")
                        log_event(f"Admin menghapus transaksi untuk {transaction.get('product_name')} dari antrian")
                        
                        # Save updated queue
                        from modules.queue_manager import save_queues
                        save_queues()
                else:
                    console.print("[red]❌ Nomor transaksi tidak valid[/red]")
            except ValueError:
                console.print("[red]❌ Input harus berupa angka[/red]")
    elif choice == "4":
        # Empty queue
        if Confirm.ask("Apakah Anda yakin ingin mengosongkan seluruh antrian?", default=False):
            transaction_queue.clear()
            console.print("[green]✅ Antrian transaksi dikosongkan[/green]")
            log_event("Admin mengosongkan antrian transaksi")
            
            # Save updated queue
            from modules.queue_manager import save_queues
            save_queues()
    
    if choice != "5":
        Prompt.ask("\nTekan Enter untuk melanjutkan...")
        manage_transaction_queue()