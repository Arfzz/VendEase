from modules.structures.queue import TransactionQueue, NotificationQueue
from modules.utils import load_json, save_json, log_event
import os
import json
from datetime import datetime

# Global queue instances
transaction_queue = TransactionQueue()
notification_queue = NotificationQueue()

# Constants
STOCK_THRESHOLD = 5  # Default threshold for low stock notifications

def init_queues():
    """Initialize queues from saved data if available"""
    # Load pending transactions
    try:
        if os.path.exists("data/pending_transactions.json"):
            transactions = load_json("data/pending_transactions.json")
            for transaction in transactions:
                transaction_queue.enqueue(transaction)
            
            log_event(f"Loaded {len(transactions)} pending transactions into queue")
    except Exception as e:
        log_event(f"Error loading pending transactions: {e}")
    
    # Load notifications
    try:
        if os.path.exists("data/notifications.json"):
            notifications = load_json("data/notifications.json")
            for notification in notifications:
                notification_queue.enqueue(notification)
            
            log_event(f"Loaded {len(notifications)} notifications into queue")
    except Exception as e:
        log_event(f"Error loading notifications: {e}")

def save_queues():
    """Save current queue state to files"""
    # Save pending transactions
    try:
        save_json("data/pending_transactions.json", transaction_queue.items)
        log_event(f"Saved {transaction_queue.size()} pending transactions")
    except Exception as e:
        log_event(f"Error saving pending transactions: {e}")
    
    # Save notifications
    try:
        save_json("data/notifications.json", notification_queue.items)
        log_event(f"Saved {notification_queue.size()} notifications")
    except Exception as e:
        log_event(f"Error saving notifications: {e}")

def add_transaction_to_queue(transaction_id, product_name, price, quantity, money_input, user_id=None):
    """Add a new transaction to the queue"""
    transaction = transaction_queue.enqueue_transaction(
        transaction_id, product_name, price, quantity, money_input, user_id
    )
    save_queues()
    log_event(f"Transaction {transaction_id} added to queue")
    return transaction

def process_transaction_queue(limit=None):
    """Process pending transactions in the queue"""
    processed_count = 0
    
    while not transaction_queue.is_empty() and (limit is None or processed_count < limit):
        transaction = transaction_queue.dequeue()
        
        # In a real system, here we would process the transaction
        # For example: update database, send confirmation, etc.
        log_event(f"Processed transaction {transaction['transaction_id']} for {transaction['product_name']}")
        
        processed_count += 1
    
    save_queues()
    return processed_count

def check_stock_levels():
    """Check product stock levels and create notifications for low stock"""
    products = load_json("data/products.json")
    notification_count = 0
    
    for product in products:
        stock = int(product['stock'])
        
        # Check if stock is below threshold
        if stock <= STOCK_THRESHOLD:
            # Only add notification if we don't already have one for this product
            existing_notifications = [n for n in notification_queue.items 
                                     if n['type'] == 'low_stock' and 
                                        n['product_id'] == product['id'] and
                                        not n['read']]
            
            if not existing_notifications:
                notification_queue.add_stock_notification(
                    product['id'],
                    product['name'],
                    stock,
                    STOCK_THRESHOLD
                )
                notification_count += 1
                log_event(f"Low stock notification created for {product['name']} (current: {stock})")
    
    if notification_count > 0:
        save_queues()
    
    return notification_count

def get_notification_count():
    """Get count of unread notifications"""
    return len(notification_queue.get_unread_notifications())

def get_queue_status():
    """Get current status of transaction and notification queues"""
    return {
        "pending_transactions": transaction_queue.size(),
        "unread_notifications": len(notification_queue.get_unread_notifications()),
        "total_notifications": notification_queue.size()
    }