"""Sample Python application with intentional issues for testing.

⚠ WARNING / 경고
이 파일은 Vibe-Code Auditor의 정적/AI 분석 기능을 테스트하기 위한
\"취약한 예시 코드\"를 포함하고 있습니다.

- 실제 서비스 코드에 이 예시를 그대로 복사/사용하면 안 됩니다.
- 하드코딩된 비밀번호, API 키, SQL Injection 취약점 등은 모두 의도적인 예시입니다.
"""

import os

# Intentional issue: Hardcoded credentials (Critical)
# ⚠ 이 코드는 보안 취약점 예시를 위한 것으로, 실제 서비스에는 절대 사용하지 마세요.
DATABASE_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"


def get_user_data(user_id):
    """Fetch user data from database."""
    # Intentional issue: SQL Injection vulnerability (Critical)
    # ⚠ 취약한 예시: 교육용 목적이며, 실제 코드에서는 반드시 파라미터 바인딩을 사용해야 합니다.
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
