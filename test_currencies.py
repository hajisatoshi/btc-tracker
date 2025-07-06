#!/usr/bin/env python3
"""
Test script to verify EUR and GBP support in the BTC tracker
"""

import requests
import json

API_URL = "http://localhost:5000"

def test_btc_price():
    """Test BTC price endpoint for all currencies"""
    print("Testing BTC price endpoint...")
    try:
        response = requests.get(f"{API_URL}/btc-price")
        if response.status_code == 200:
            data = response.json()
            print("✓ BTC price endpoint working")
            print(f"  USD: ${data.get('btc_usd', 'N/A')}")
            print(f"  CAD: C${data.get('btc_cad', 'N/A')}")
            print(f"  EUR: €{data.get('btc_eur', 'N/A')}")
            print(f"  GBP: £{data.get('btc_gbp', 'N/A')}")
        else:
            print(f"✗ BTC price endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ BTC price endpoint error: {e}")

def test_registration_and_login():
    """Test user registration and login"""
    print("\nTesting registration and login...")
    
    # Test registration
    try:
        reg_data = {"username": "testuser", "password": "testpass123"}
        response = requests.post(f"{API_URL}/register", json=reg_data)
        if response.status_code in [201, 409]:  # 201 = created, 409 = already exists
            print("✓ Registration endpoint working")
        else:
            print(f"✗ Registration failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Registration error: {e}")
        return None
    
    # Test login
    try:
        login_data = {"username": "testuser", "password": "testpass123"}
        response = requests.post(f"{API_URL}/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print("✓ Login endpoint working")
            return token
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Login error: {e}")
        return None

def test_transaction_endpoints(token):
    """Test transaction endpoints with new currencies"""
    if not token:
        print("Skipping transaction tests - no token")
        return
    
    print("\nTesting transaction endpoints...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test adding transactions in different currencies
    test_transactions = [
        {
            "transaction_date": "2024-01-15",
            "transaction_type": "save",
            "btc_amount": 0.001,
            "cost_usd": 50.0,
            "cost_cad": 67.5,
            "cost_eur": 46.0,
            "cost_gbp": 39.5,
            "currency": "USD",
            "notes": "Test USD transaction"
        },
        {
            "transaction_date": "2024-01-16",
            "transaction_type": "save",
            "btc_amount": 0.0015,
            "cost_usd": 69.57,
            "cost_cad": 75.0,
            "cost_eur": 64.13,
            "cost_gbp": 54.98,
            "currency": "CAD",
            "notes": "Test CAD transaction"
        },
        {
            "transaction_date": "2024-01-17",
            "transaction_type": "spend",
            "btc_amount": 0.0005,
            "cost_usd": 23.91,
            "cost_cad": 32.28,
            "cost_eur": 22.0,
            "cost_gbp": 18.87,
            "currency": "EUR",
            "notes": "Test EUR transaction"
        },
        {
            "transaction_date": "2024-01-18",
            "transaction_type": "spend",
            "btc_amount": 0.0003,
            "cost_usd": 15.19,
            "cost_cad": 20.51,
            "cost_eur": 14.01,
            "cost_gbp": 12.0,
            "currency": "GBP",
            "notes": "Test GBP transaction"
        }
    ]
    
    transaction_ids = []
    
    for i, transaction in enumerate(test_transactions):
        try:
            response = requests.post(f"{API_URL}/transactions", json=transaction, headers=headers)
            if response.status_code == 201:
                print(f"✓ Added {transaction['currency']} transaction")
                # Get transaction ID for cleanup
                transactions_response = requests.get(f"{API_URL}/transactions", headers=headers)
                if transactions_response.status_code == 200:
                    transactions_data = transactions_response.json()
                    if transactions_data:
                        # Find the transaction we just added
                        for t in transactions_data:
                            if (t.get('notes') == transaction['notes'] and 
                                t.get('currency') == transaction['currency']):
                                transaction_ids.append(t['id'])
                                break
            else:
                print(f"✗ Failed to add {transaction['currency']} transaction: {response.status_code}")
                print(f"  Response: {response.text}")
        except Exception as e:
            print(f"✗ Error adding {transaction['currency']} transaction: {e}")
    
    # Test getting transactions
    try:
        response = requests.get(f"{API_URL}/transactions", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {len(data)} transactions")
            
            # Check if we have transactions in different currencies
            currencies = set(t.get('currency', 'USD') for t in data)
            print(f"  Currencies found: {', '.join(currencies)}")
        else:
            print(f"✗ Failed to retrieve transactions: {response.status_code}")
    except Exception as e:
        print(f"✗ Error retrieving transactions: {e}")
    
    # Test currency filtering
    for currency in ['USD', 'CAD', 'EUR', 'GBP']:
        try:
            response = requests.get(f"{API_URL}/transactions?currency={currency}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Currency filter for {currency}: {len(data)} transactions")
            else:
                print(f"✗ Currency filter for {currency} failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Error filtering {currency} transactions: {e}")
    
    # Test portfolio summary
    try:
        response = requests.get(f"{API_URL}/portfolio/summary", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✓ Portfolio summary endpoint working")
            print(f"  Net BTC: {data.get('net_btc', 'N/A')}")
            print(f"  Net cost basis USD: ${data.get('net_cost_basis_usd', 'N/A')}")
            print(f"  Net cost basis CAD: C${data.get('net_cost_basis_cad', 'N/A')}")
            print(f"  Net cost basis EUR: €{data.get('net_cost_basis_eur', 'N/A')}")
            print(f"  Net cost basis GBP: £{data.get('net_cost_basis_gbp', 'N/A')}")
        else:
            print(f"✗ Portfolio summary failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Portfolio summary error: {e}")
    
    # Cleanup - delete test transactions
    print("\nCleaning up test transactions...")
    for tid in transaction_ids:
        try:
            response = requests.delete(f"{API_URL}/transactions/{tid}", headers=headers)
            if response.status_code == 200:
                print(f"✓ Deleted transaction {tid}")
            else:
                print(f"✗ Failed to delete transaction {tid}: {response.status_code}")
        except Exception as e:
            print(f"✗ Error deleting transaction {tid}: {e}")

if __name__ == "__main__":
    print("BTC Portfolio Tracker - Multi-Currency Support Test")
    print("=" * 50)
    
    # Test BTC price endpoint
    test_btc_price()
    
    # Test user registration and login
    token = test_registration_and_login()
    
    # Test transaction endpoints
    test_transaction_endpoints(token)
    
    print("\n" + "=" * 50)
    print("Test completed!")
