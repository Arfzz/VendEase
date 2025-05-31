class TransactionNode:
    """Node for transaction linked list"""
    def __init__(self, transaction_id, datetime, product_name, price, money_input, change):
        self.transaction_id = transaction_id
        self.datetime = datetime
        self.product_name = product_name
        self.price = price
        self.money_input = money_input
        self.change = change
        self.next = None  # Reference to next node


class TransactionList:
    """Linked list implementation for transaction history"""
    def __init__(self):
        self.head = None  # First node in the list
        self.tail = None  # Last node in the list
        self.size = 0     # Number of nodes in list
    
    def append(self, transaction_id, datetime, product_name, price, money_input, change):
        """Add a new transaction to the end of the list"""
        # Handle case where a dictionary is passed directly
        if isinstance(transaction_id, dict):
            t = transaction_id
            transaction_id = t.get('id', 'N/A')
            datetime = t.get('datetime', 'N/A')
            product_name = t.get('product_name', t.get('produk', 'Unknown'))
            price = t.get('total', t.get('price', 0) * t.get('quantity', 1))
            money_input = t.get('money_input', price)
            change = t.get('change', 0)
            
        new_node = TransactionNode(transaction_id, datetime, product_name, price, money_input, change)
        
        if not self.head:  # If list is empty
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node  # Link current tail to new node
            self.tail = new_node       # Update tail to new node
        
        self.size += 1
        return new_node
    
    def prepend(self, transaction_id, datetime, product_name, price, money_input, change):
        """Add a new transaction to the beginning of the list"""
        new_node = TransactionNode(transaction_id, datetime, product_name, price, money_input, change)
        
        if not self.head:  # If list is empty
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head  # Link new node to current head
            self.head = new_node       # Update head to new node
        
        self.size += 1
        return new_node
    
    def remove(self, transaction_id):
        """Remove a transaction by ID"""
        if not self.head:  # Empty list
            return False
        
        # If head node is to be removed
        if self.head.transaction_id == transaction_id:
            self.head = self.head.next
            self.size -= 1
            
            # If list is now empty, update tail
            if not self.head:
                self.tail = None
            
            return True
        
        # Search for the node to remove
        current = self.head
        while current.next and current.next.transaction_id != transaction_id:
            current = current.next
        
        # If node was found
        if current.next:
            # Remove the node
            if current.next == self.tail:
                self.tail = current  # Update tail
            
            current.next = current.next.next
            self.size -= 1
            return True
        
        return False  # Transaction not found
    
    def find(self, transaction_id):
        """Find a transaction by ID"""
        current = self.head
        while current:
            if current.transaction_id == transaction_id:
                return current
            current = current.next
        
        return None  # Transaction not found
    
    def filter_by_product(self, product_name):
        """Filter transactions by product name, returns a new list"""
        filtered_list = TransactionList()
        
        current = self.head
        while current:
            # Case-insensitive partial match
            if product_name.lower() in current.product_name.lower():
                filtered_list.append(
                    current.transaction_id,
                    current.datetime,
                    current.product_name,
                    current.price,
                    current.money_input,
                    current.change
                )
            current = current.next
        
        return filtered_list
    
    def reverse(self):
        """Reverse the list and return a new list"""
        reversed_list = TransactionList()
        
        # Helper function for recursive reverse traversal
        def _reverse_traverse(node):
            if node:
                _reverse_traverse(node.next)
                reversed_list.append(
                    node.transaction_id,
                    node.datetime,
                    node.product_name,
                    node.price,
                    node.money_input,
                    node.change
                )
        
        _reverse_traverse(self.head)
        return reversed_list
    
    def to_list(self):
        """Convert linked list to Python list of dictionaries"""
        result = []
        current = self.head
        
        while current:
            result.append({
                'id': current.transaction_id,
                'datetime': current.datetime,
                'product_name': current.product_name,
                'price': current.price,
                'money_input': current.money_input,
                'change': current.change
            })
            current = current.next
        
        return result
    
    def __len__(self):
        """Return the size of the list"""
        return self.size
    
    def __bool__(self):
        """Return True if list is not empty"""
        return self.head is not None