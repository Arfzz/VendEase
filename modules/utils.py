import json, hashlib, os, datetime

def load_json(file_path):
    try:
        if not os.path.exists(file_path):
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(file_path, 'w') as file:
                json.dump([], file)
            return []
        
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return []

def save_json(file_path, data):
    try:
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving JSON: {e}")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_login(username, password):
    """
    Validates login credentials and returns user role if valid.
    """
    users = load_json('data/users.json')
    hashed_password = hash_password(password)
    
    for user in users:
        if user['username'] == username and user['password'] == hashed_password:
            log_event(f"User {username} logged in as {user['role']}")
            return user['role']
    
    log_event(f"Failed login attempt for username: {username}")
    return None

def log_event(message):
    """Log system events with timestamp"""
    try:
        log_dir = os.path.dirname('data/system_log.txt')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        with open('data/system_log.txt', 'a') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Error logging event: {e}")
        
        import json, hashlib, os, datetime

def load_json(file_path):
    try:
        if not os.path.exists(file_path):
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(file_path, 'w') as file:
                json.dump([], file)
            return []
        
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return []

def save_json(file_path, data):
    try:
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving JSON: {e}")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_login(username, password):
    """
    Validates login credentials and returns user role if valid.
    """
    users = load_json('data/users.json')
    hashed_password = hash_password(password)
    
    for user in users:
        if user['username'] == username and user['password'] == hashed_password:
            log_event(f"User {username} logged in as {user['role']}")
            return user['role']
    
    log_event(f"Failed login attempt for username: {username}")
    return None

def log_event(message):
    """Log system events with timestamp"""
    try:
        log_dir = os.path.dirname('data/system_log.txt')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        with open('data/system_log.txt', 'a') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Error logging event: {e}")

def initialize_data():
    """Initialize the system with default data if not exists"""
    # Create default users if users.json doesn't exist
    users = load_json('data/users.json')
    if not users:
        default_users = [
            {
                "username": "admin",
                "password": hash_password("admin123"),
                "role": "admin"
            },
            {
                "username": "tech",
                "password": hash_password("tech123"),
                "role": "technician"
            },
            {
                "username": "super",
                "password": hash_password("super123"),
                "role": "superadmin"
            },
            {
                "username": "user",
                "password": hash_password("user123"),
                "role": "user"
            }
        ]
        save_json('data/users.json', default_users)
        log_event("Default users created")
    
    # Create default products if products.json doesn't exist
    products = load_json('data/products.json')
    if not products:
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
        save_json('data/products.json', default_products)
        log_event("Default products created")