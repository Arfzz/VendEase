from modules.utils import load_json, save_json, log_event
from modules.structures.linkedList import TransactionList, TransactionNode
from modules.queue_manager import add_transaction_to_queue
import datetime
import uuid

TRANSACTION_FILE = 'data/transactions.json'

def record_transaction(product_id, product_name, price, quantity, money_input):
    """
    Record a new transaction with all necessary details
    
    Args:
        product_id: ID of the product
        product_name: Name of the product
        price: Price per unit
        quantity: Number of items purchased
        money_input: Money given by customer
    """
    total_price = price * quantity
    change = money_input - total_price
    
    # Generate unique transaction ID
    transaction_id = str(uuid.uuid4())[:8]
    
    # Format current datetime
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Create transaction data
    transaction = {
        "id": transaction_id,
        "datetime": timestamp,
        "product_id": product_id,
        "product_name": product_name,
        "price": price,
        "quantity": quantity,
        "total": total_price,
        "money_input": money_input,
        "change": change
    }
    
    
    
    # Load existing transactions
    transactions = load_json(TRANSACTION_FILE)
    if transactions is None:
        transactions = []
    
    # Add new transaction
    transactions.append(transaction)
    
    # Save updated transactions
    save_json(TRANSACTION_FILE, transactions)
    
    return transaction

def get_transactions():
    """Get all transactions as a list"""
    transactions = load_json(TRANSACTION_FILE)
    if transactions is None:
        transactions = []
    return transactions

def get_total_income():
    """Calculate total income from all transactions"""
    transactions = get_transactions()
    return sum(t.get('total', t.get('price', 0) * t.get('quantity', 1)) for t in transactions)

def get_transactions_as_linkedlist():
    """Convert transactions to a linked list"""
    transactions = get_transactions()
    transaction_list = TransactionList()
    
    for t in transactions:
        transaction_id = t.get('id', 'N/A')
        datetime_str = t.get('timestamp', t.get('datetime', 'N/A'))  # pakai 'timestamp'
        product_name = t.get('product_name', 'Unknown')
        
        price = t.get('total_price', t.get('total', t.get('price', 0) * t.get('quantity', 1)))  # pakai 'total_price'
        money_input = t.get('payment_amount', t.get('money_input', price))  # pakai 'payment_amount'
        change = t.get('change_amount', t.get('change', 0))  # pakai 'change_amount'
        
        transaction_list.append(
            transaction_id, 
            datetime_str, 
            product_name, 
            price, 
            money_input, 
            change
        )
    
    return transaction_list


def filter_transactions_by_date(start_date, end_date):
    """Filter transactions by date range"""
    transactions = get_transactions()
    filtered = []
    
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59)  # End of day
    
    for t in transactions:
        try:
            # Try to parse the datetime
            trans_date = datetime.datetime.strptime(t.get('datetime', ''), "%Y-%m-%d %H:%M:%S")
            if start <= trans_date <= end:
                filtered.append(t)
        except ValueError:
            # Skip transactions with invalid datetime format
            continue
    
    return filtered

def filter_transactions_by_product(product_id):
    """Filter transactions by product ID"""
    transactions = get_transactions()
    return [t for t in transactions if t.get('product_id') == product_id]

def get_product_sales_count():
    """Get the count of sales for each product"""
    transactions = get_transactions()
    product_sales = {}
    
    for t in transactions:
        product_id = t.get('product_id')
        quantity = t.get('quantity', 1)
        
        if product_id in product_sales:
            product_sales[product_id] += quantity
        else:
            product_sales[product_id] = quantity
    
    return product_sales

def get_transaction_history(limit=None):
    """
    Get transaction history, optionally limited to a number of recent transactions
    
    Args:
        limit: Maximum number of transactions to return (newest first)
        
    Returns:
        list: List of transaction dictionaries
    """
    try:
        transactions = load_json("data/transactions.json")
        
        # Sort by datetime (newest first)
        transactions.sort(key=lambda x: x.get('datetime', ''), reverse=True)
        
        # Apply limit if specified
        if limit and isinstance(limit, int) and limit > 0:
            transactions = transactions[:limit]
            
        return transactions
    except Exception as e:
        log_event(f"Error getting transaction history: {e}")
        return []
    
    