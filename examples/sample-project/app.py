"""Sample Python application with intentional issues for testing."""

import os

# Intentional issue: Hardcoded credentials (Critical)
DATABASE_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"


def get_user_data(user_id):
    """Fetch user data from database."""
    # Intentional issue: SQL Injection vulnerability (Critical)
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)


def execute_query(query):
    """Mock database query execution."""
    print(f"Executing: {query}")
    return {"id": 1, "name": "Test User"}


# Intentional issue: Code duplication (Warning)
def calculate_total_price(items):
    """Calculate total price of items."""
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total


def calculate_total_cost(products):
    """Calculate total cost of products."""
    total = 0
    for product in products:
        total += product['price'] * product['quantity']
    return total


# Intentional issue: High complexity (Warning)
def process_order(order):
    """Process an order with complex logic."""
    if order['status'] == 'pending':
        if order['payment_method'] == 'card':
            if order['amount'] > 1000:
                if order['customer_type'] == 'premium':
                    discount = 0.2
                else:
                    discount = 0.1
            else:
                discount = 0.05
        elif order['payment_method'] == 'cash':
            if order['amount'] > 500:
                discount = 0.15
            else:
                discount = 0.05
        else:
            discount = 0
    else:
        discount = 0

    final_amount = order['amount'] * (1 - discount)
    return final_amount


# Intentional issue: Unclear variable names (Info)
def calc(a, b, c):
    """Calculate something."""
    x = a + b
    y = x * c
    z = y / 2
    return z


if __name__ == '__main__':
    # Test the functions
    user = get_user_data(1)
    print(user)

    items = [
        {'price': 100, 'quantity': 2},
        {'price': 50, 'quantity': 3}
    ]
    total = calculate_total_price(items)
    print(f"Total: {total}")
