from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from modules.utils import validate_login, load_json, save_json, log_event
from modules.user import user_menu
from modules.admin import admin_menu
from modules.technician import technician_menu
from modules.superadmin import superadmin_menu
from modules.utils import hash_password

console = Console()

def main_menu():
    while True:
        console.clear()
        console.print(Panel.fit("💡 [bold cyan]VENDING MACHINE SYSTEM[/bold cyan]", subtitle="WELCOME", border_style="bright_blue"))
        
        console.print("[1] Login")
        console.print("[2] Register")
        console.print("[3] Keluar")

        choice = Prompt.ask("\n[bold yellow]Pilih menu[/bold yellow]", choices=["1", "2", "3"])
        
        if choice == '1':
            login_user()
        elif choice == '2':
            register_user()
        elif choice == '3':
            console.print("\n[bold green]Terima kasih telah menggunakan vending machine![/bold green]")
            break

def login_user():
    console.clear()
    console.print(Panel.fit("💡 [bold cyan]VENDING MACHINE SYSTEM[/bold cyan]", subtitle="LOGIN", border_style="bright_blue"))

    username = Prompt.ask("[bold yellow]👤 Username[/bold yellow]")
    password = Prompt.ask("[bold yellow]🔒 Password[/bold yellow]", password=True)  # Menyembunyikan password

    user_role = validate_login(username, password)
    
    if user_role:
        console.print(f"\n[green]✅ Login berhasil sebagai [bold]{user_role.upper()}[/bold][/green]\n")
        log_event(f"User '{username}' logged in as {user_role}")

        # Arahkan ke menu sesuai role
        if user_role == "user":
            user_menu(username=username)
        elif user_role == "admin":
            admin_menu()
        elif user_role == "technician":
            technician_menu()
        elif user_role == "superadmin":
            superadmin_menu()

        console.print("\n[cyan]🔁 Logout berhasil. Kembali ke halaman utama...[/cyan]\n", style="dim")
    else:
        console.print("\n[red]❌ Login gagal. Username atau password salah.[/red]\n")
        log_event(f"Failed login attempt with username '{username}'")
    
    Prompt.ask("Tekan Enter untuk melanjutkan...")

def register_user():
    console.clear()
    console.print(Panel.fit("💡 [bold cyan]VENDING MACHINE SYSTEM[/bold cyan]", subtitle="REGISTER", border_style="bright_blue"))
    
    # Load users data
    users = load_json("data/users.json")
    
    while True:
        username = Prompt.ask("[bold yellow]👤 Create Username[/bold yellow]")
        
        # Check if username already exists
        username_exists = any(user["username"] == username for user in users)
        if username_exists:
            console.print("[red]❌ Username sudah digunakan. Silakan pilih username lain.[/red]")
            continue
        
        # Username valid, proceed to password
        break
    
    while True:
        password = Prompt.ask("[bold yellow]🔒 Create Password[/bold yellow]", password=True)
        confirm_password = Prompt.ask("[bold yellow]🔒 Confirm Password[/bold yellow]", password=True)
        
        if password != confirm_password:
            console.print("[red]❌ Password tidak cocok. Silakan coba lagi.[/red]")
            continue
        
        # Password matches, proceed
        break
    
    # Hash password untuk keamanan
    hashed_password = hash_password(password)
    
    # Add new user to users list
    new_user = {
        "username": username,
        "password": hashed_password,
        "role": "user"  # Semua registrasi baru otomatis mendapat role "user"
    }
    
    users.append(new_user)
    save_json("data/users.json", users)
    
    console.print("\n[green]✅ Registrasi berhasil! Anda sekarang dapat login.[/green]\n")
    log_event(f"New user registered: '{username}'")
    
    Prompt.ask("Tekan Enter untuk melanjutkan...")

if __name__ == "__main__":
    main_menu()


# modules/utils.py
# modules/user.py
# modules/admin.py
 
# modules/technician.py

# modules/superadmin.py
# modules/utils.py
# modules/user.py
# # modules/admin.py
# from rich.console import Console
# from rich.table import Table
# from rich.prompt import Prompt, IntPrompt
# from rich.panel import Panel
# from modules.utils import load_json, save_json, log_event
# console = Console()
# # modules/technician.py
# from rich.console import Console
# from rich.panel import Panel
# from rich.prompt import Prompt
# from modules.utils import log_event, load_json, save_json
# import os
# console = Console()