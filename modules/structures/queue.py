class Queue:
    """
    Implementation of a Queue data structure for managing transaction processing
    and low stock notifications
    """
    def __init__(self):
        self.items = []
    
    def is_empty(self):
        """Check if queue is empty"""
        return len(self.items) == 0
    
    def enqueue(self, item):
        """Add item to the end of the queue"""
        self.items.append(item)
        return item
    
    def dequeue(self):
        """Remove and return item from the front of the queue"""
        if self.is_empty():
            return None
        return self.items.pop(0)
    
    def peek(self):
        """Return the first item without removing it"""
        if self.is_empty():
            return None
        return self.items[0]
    
    def size(self):
        """Return the number of items in the queue"""
        return len(self.items)
    
    def clear(self):
        """Remove all items from the queue"""
        self.items = []
    
    def __str__(self):
        """Return string representation of the queue"""
        return str(self.items)


class TransactionQueue(Queue):
    """
    Specialized queue for pending transaction processing
    """
    def enqueue_transaction(self, transaction_id, product_name, price, quantity, money_input, user_id=None):
        """Add transaction to the queue with specific transaction details"""
        transaction = {
            'transaction_id': transaction_id,
            'product_name': product_name,
            'price': price,
            'quantity': quantity,
            'money_input': money_input,
            'user_id': user_id,
            'status': 'pending'
        }
        return self.enqueue(transaction)
    
    def get_pending_transactions(self):
        """Return list of all pending transactions"""
        return self.items


class NotificationQueue(Queue):
    """
    Specialized queue for stock notifications and system alerts
    """
    def add_stock_notification(self, product_id, product_name, current_stock, threshold):
        """Add low stock notification to the queue"""
        notification = {
            'type': 'low_stock',
            'product_id': product_id,
            'product_name': product_name,
            'current_stock': current_stock,
            'threshold': threshold,
            'read': False,
            'timestamp': self._get_timestamp()
        }
        return self.enqueue(notification)
    
    def add_system_notification(self, message, notification_type='system'):
        """Add system notification to the queue"""
        notification = {
            'type': notification_type,
            'message': message,
            'read': False,
            'timestamp': self._get_timestamp()
        }
        return self.enqueue(notification)
    
    def get_unread_notifications(self):
        """Return list of all unread notifications"""
        return [n for n in self.items if not n.get('read', False)]
    
    def mark_as_read(self, index):
        """Mark a notification as read by index"""
        if 0 <= index < len(self.items):
            self.items[index]['read'] = True
            return True
        return False
    
    def mark_all_as_read(self):
        """Mark all notifications as read"""
        for notification in self.items:
            notification['read'] = True
    
    def _get_timestamp(self):
        """Get current timestamp for notification"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")