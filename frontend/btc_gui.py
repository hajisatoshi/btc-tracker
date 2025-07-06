#!/usr/bin/env python3
"""
BTC Portfolio Tracker GUI - Version 2.0
Enhanced version with separate Savings and Spending tracking
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import requests
import csv
from typing import Dict, List, Optional

# Configuration constants
API_URL = "http://localhost:5000"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
CURRENCIES = ('USD', 'CAD', 'EUR', 'GBP', 'Swiss Franc', 'Ounces of Gold')

# Utility functions
def show_error(title: str, message: str):
    """Show error message dialog"""
    messagebox.showerror(title, message)

def show_info(title: str, message: str):
    """Show info message dialog"""
    messagebox.showinfo(title, message)

def show_warning(title: str, message: str):
    """Show warning message dialog"""
    messagebox.showwarning(title, message)

def confirm_action(title: str, message: str) -> bool:
    """Show confirmation dialog and return result"""
    return messagebox.askyesno(title, message)

def validate_float(value: str, field_name: str) -> float:
    """Validate and convert string to float"""
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid number format for {field_name}")

def validate_date(date_str: str) -> bool:
    """Validate date string format"""
    try:
        datetime.strptime(date_str, DEFAULT_DATE_FORMAT)
        return True
    except ValueError:
        return False

def format_btc_amount(amount: float) -> str:
    """Format BTC amount with 8 decimal places"""
    return f"{amount:.8f}"

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "CAD":
        return f"C${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "GBP":
        return f"£{amount:,.2f}"
    elif currency == "Swiss Franc":
        return f"₣{amount:,.2f}"
    elif currency == "Ounces of Gold":
        return f"{amount:.4f} oz"
    else:
        return f"{amount:,.2f}"

def get_current_date() -> str:
    """Get current date in YYYY-MM-DD format"""
    return datetime.now().strftime(DEFAULT_DATE_FORMAT)

class APIClient:
    """Handles API communication"""
    
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
        self.token = None
    
    def set_token(self, token: str):
        """Set authentication token"""
        self.token = token
    
    def get_headers(self) -> Dict:
        """Get headers with authentication"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def make_request(self, method: str, endpoint: str, data: Dict = None) -> tuple:
        """Make HTTP request and return response and status code"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.request(method, url, json=data, headers=self.get_headers(), timeout=10)
            return response.json(), response.status_code
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {str(e)}")
    
    def login(self, username: str, password: str) -> tuple:
        """Login user"""
        return self.make_request('POST', '/login', {'username': username, 'password': password})
    
    def register(self, username: str, password: str) -> tuple:
        """Register user"""
        return self.make_request('POST', '/register', {'username': username, 'password': password})
    
    def get_portfolio_summary(self) -> tuple:
        """Get portfolio summary"""
        return self.make_request('GET', '/portfolio/summary')
    
    def get_btc_price(self) -> tuple:
        """Get current BTC price"""
        return self.make_request('GET', '/btc-price')
    
    # Transaction endpoints
    def add_transaction(self, data: Dict) -> tuple:
        """Add new transaction"""
        return self.make_request('POST', '/transactions', data)
    
    def get_transactions(self, transaction_type: str = None, currency: str = None) -> tuple:
        """Get transactions with optional type and currency filter"""
        endpoint = '/transactions'
        params = []
        if transaction_type:
            params.append(f'type={transaction_type}')
        if currency:
            params.append(f'currency={currency}')
        
        if params:
            endpoint += '?' + '&'.join(params)
        
        return self.make_request('GET', endpoint)
    
    def update_transaction(self, transaction_id: int, data: Dict) -> tuple:
        """Update transaction"""
        return self.make_request('PUT', f'/transactions/{transaction_id}', data)
    
    def delete_transaction(self, transaction_id: int) -> tuple:
        """Delete transaction"""
        return self.make_request('DELETE', f'/transactions/{transaction_id}')
    
    # Legacy purchase endpoints for backward compatibility
    def add_purchase(self, data: Dict) -> tuple:
        """Add new purchase (legacy)"""
        return self.make_request('POST', '/purchases', data)
    
    def get_purchases(self) -> tuple:
        """Get purchases (legacy)"""
        return self.make_request('GET', '/purchases')
    
    def update_purchase(self, purchase_id: int, data: Dict) -> tuple:
        """Update purchase (legacy)"""
        return self.make_request('PUT', f'/purchases/{purchase_id}', data)
    
    def delete_purchase(self, purchase_id: int) -> tuple:
        """Delete purchase (legacy)"""
        return self.make_request('DELETE', f'/purchases/{purchase_id}')

class CurrencyConverter:
    """Handles currency conversion"""
    
    @staticmethod
    def convert_from_usd(usd_amount: float, target_currency: str) -> str:
        """Convert USD to target currency with formatting"""
        if target_currency == "USD":
            return format_currency(usd_amount, "USD")
        elif target_currency == "CAD":
            return format_currency(usd_amount * 1.35, "CAD")
        elif target_currency == "EUR":
            return format_currency(usd_amount * 0.92, "EUR")
        elif target_currency == "GBP":
            return format_currency(usd_amount * 0.79, "GBP")
        elif target_currency == "Swiss Franc":
            return format_currency(usd_amount * 0.91, "Swiss Franc")
        elif target_currency == "Ounces of Gold":
            return format_currency(usd_amount / 2000, "Ounces of Gold")
        else:
            return format_currency(usd_amount, target_currency)
    
    @staticmethod
    def get_cost_in_currency(transaction: dict, currency: str) -> float:
        """Get the cost value in the specified currency"""
        if currency == "USD":
            return transaction.get('cost_usd', 0)
        elif currency == "CAD":
            return transaction.get('cost_cad', 0)
        elif currency == "EUR":
            return transaction.get('cost_eur', 0)
        elif currency == "GBP":
            return transaction.get('cost_gbp', 0)
        elif currency == "Swiss Franc":
            return transaction.get('cost_usd', 0) * 0.91
        elif currency == "Ounces of Gold":
            return transaction.get('cost_usd', 0) / 2000
        else:
            return transaction.get('cost_usd', 0)

class FormValidator:
    """Validates form inputs"""
    
    @staticmethod
    def validate_transaction_form(date: str, btc_amount: str, cost: str, transaction_type: str) -> Dict:
        """Validate transaction form inputs"""
        errors = []
        
        if not date:
            errors.append("Date is required")
        elif not validate_date(date):
            errors.append("Invalid date format (use YYYY-MM-DD)")
        
        if not btc_amount:
            errors.append("BTC amount is required")
        else:
            try:
                amount = float(btc_amount)
                if amount <= 0:
                    errors.append("BTC amount must be positive")
            except ValueError:
                errors.append("Invalid BTC amount format")
        
        if not cost:
            errors.append("Cost is required")
        else:
            try:
                cost_value = float(cost)
                if cost_value <= 0:
                    errors.append("Cost must be positive")
            except ValueError:
                errors.append("Invalid cost format")
        
        if transaction_type not in ['save', 'spend']:
            errors.append("Invalid transaction type")
        
        return {'is_valid': len(errors) == 0, 'errors': errors}

class LoginFrame:
    """Handles user login and registration"""
    
    def __init__(self, parent, api_client: APIClient, on_login_success):
        self.parent = parent
        self.api_client = api_client
        self.on_login_success = on_login_success
        self.frame = None
        self.create_frame()
    
    def create_frame(self):
        """Create login UI"""
        self.frame = tk.Frame(self.parent, bg="white")
        
        # Title
        title_label = tk.Label(self.frame, text="BTC Portfolio Tracker v2", 
                              font=("Arial", 24, "bold"), bg="white", fg="#2C3E50")
        title_label.pack(pady=20)
        
        # Login form
        form_frame = tk.Frame(self.frame, bg="white")
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="Username:", font=("Arial", 12), bg="white").pack(pady=5)
        self.username_entry = tk.Entry(form_frame, width=30, font=("Arial", 12))
        self.username_entry.pack(pady=5)
        
        tk.Label(form_frame, text="Password:", font=("Arial", 12), bg="white").pack(pady=5)
        self.password_entry = tk.Entry(form_frame, width=30, font=("Arial", 12), show="*")
        self.password_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg="white")
        button_frame.pack(pady=20)
        
        login_btn = tk.Button(button_frame, text="Login", command=self.login, 
                             bg="#3498DB", fg="white", font=("Arial", 12, "bold"), width=10)
        login_btn.pack(side="left", padx=10)
        
        register_btn = tk.Button(button_frame, text="Register", command=self.register,
                               bg="#2ECC71", fg="white", font=("Arial", 12, "bold"), width=10)
        register_btn.pack(side="left", padx=10)
        
        # Bind Enter key to login
        self.username_entry.bind('<Return>', lambda e: self.login())
        self.password_entry.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            show_error("Login Error", "Please enter both username and password")
            return
        
        try:
            response, status_code = self.api_client.login(username, password)
            
            if status_code == 200:
                self.api_client.set_token(response['access_token'])
                self.on_login_success(username)
            else:
                show_error("Login Failed", response.get("msg", "Invalid credentials"))
        except Exception as e:
            show_error("Connection Error", str(e))
    
    def register(self):
        """Handle registration"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            show_error("Registration Error", "Please enter both username and password")
            return
        
        if len(password) < 6:
            show_error("Registration Error", "Password must be at least 6 characters long")
            return
        
        try:
            response, status_code = self.api_client.register(username, password)
            
            if status_code == 201:
                show_info("Registration Successful", "Account created successfully! Please login.")
                self.password_entry.delete(0, tk.END)
            else:
                show_error("Registration Failed", response.get("msg", "Registration failed"))
        except Exception as e:
            show_error("Connection Error", str(e))
    
    def pack(self, **kwargs):
        """Pack the frame"""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Hide the frame"""
        self.frame.pack_forget()

class SummaryTab:
    """Handles portfolio summary display"""
    
    def __init__(self, parent, api_client: APIClient, on_logout):
        self.parent = parent
        self.api_client = api_client
        self.on_logout = on_logout
        self.frame = ttk.Frame(parent)
        self.summary_data = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup summary UI"""
        container = tk.Frame(self.frame)
        container.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title
        title_frame = tk.Frame(container)
        title_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(title_frame, text="Portfolio Summary", 
                font=("Arial", 18, "bold")).pack(side="left")
        
        # Currency filter for summary
        currency_frame = tk.Frame(title_frame)
        currency_frame.pack(side="left", padx=(20, 0))
        
        tk.Label(currency_frame, text="Display Currency:", font=("Arial", 10)).pack(side="left", padx=(0, 5))
        self.display_currency = ttk.Combobox(currency_frame, width=10, state="readonly", font=("Arial", 10))
        self.display_currency['values'] = ('USD', 'CAD', 'EUR', 'GBP')
        self.display_currency.set('USD')
        self.display_currency.pack(side="left")
        self.display_currency.bind('<<ComboboxSelected>>', self.on_currency_change)
        
        tk.Button(title_frame, text="Logout", command=self.on_logout,
                 bg="#E74C3C", fg="white", font=("Arial", 10, "bold")).pack(side="right")
        
        # Net position section
        net_frame = tk.LabelFrame(container, text="Net Position", 
                                 font=("Arial", 12, "bold"), padx=10, pady=10)
        net_frame.pack(fill="x", pady=(0, 20))
        
        self.net_btc_label = tk.Label(net_frame, text="Net BTC: Loading...", 
                                     font=("Arial", 14))
        self.net_btc_label.pack(pady=5)
        
        self.net_cost_label = tk.Label(net_frame, text="Net Cost Basis: Loading...", 
                                      font=("Arial", 12))
        self.net_cost_label.pack(pady=2)
        
        self.current_value_label = tk.Label(net_frame, text="Current Value: Loading...", 
                                           font=("Arial", 12))
        self.current_value_label.pack(pady=2)
        
        self.gain_loss_label = tk.Label(net_frame, text="Gain/Loss: Loading...", 
                                       font=("Arial", 12, "bold"))
        self.gain_loss_label.pack(pady=5)
        
        # Breakdown section
        breakdown_frame = tk.Frame(container)
        breakdown_frame.pack(fill="x", pady=(0, 20))
        
        # Savings column
        savings_frame = tk.LabelFrame(breakdown_frame, text="Savings", 
                                     font=("Arial", 12, "bold"), padx=10, pady=10)
        savings_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.savings_btc_label = tk.Label(savings_frame, text="BTC: Loading...", 
                                         font=("Arial", 11))
        self.savings_btc_label.pack(pady=2)
        
        self.savings_cost_label = tk.Label(savings_frame, text="Cost: Loading...", 
                                          font=("Arial", 11))
        self.savings_cost_label.pack(pady=2)
        
        # Spending column
        spending_frame = tk.LabelFrame(breakdown_frame, text="Spending", 
                                      font=("Arial", 12, "bold"), padx=10, pady=10)
        spending_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.spending_btc_label = tk.Label(spending_frame, text="BTC: Loading...", 
                                          font=("Arial", 11))
        self.spending_btc_label.pack(pady=2)
        
        self.spending_cost_label = tk.Label(spending_frame, text="Cost: Loading...", 
                                           font=("Arial", 11))
        self.spending_cost_label.pack(pady=2)
        
        # Price section
        price_frame = tk.LabelFrame(container, text="Current BTC Price", 
                                   font=("Arial", 12, "bold"), padx=10, pady=10)
        price_frame.pack(fill="x", pady=(0, 20))
        
        self.btc_price_label = tk.Label(price_frame, text="BTC Price: Loading...", 
                                       font=("Arial", 12))
        self.btc_price_label.pack(pady=5)
        
        # Refresh button
        tk.Button(container, text="Refresh Data", command=self.refresh_summary,
                 bg="#3498DB", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
    
    def refresh_summary(self):
        """Refresh portfolio summary"""
        # Don't try to refresh if no token is set
        if not self.api_client.token:
            return
            
        try:
            response, status_code = self.api_client.get_portfolio_summary()
            
            if status_code == 200:
                self.summary_data = response
                self.update_display()
            elif status_code == 401:
                # Session expired - don't show error during normal operation
                pass
            else:
                show_error("Summary Error", response.get("msg", "Failed to load summary"))
        except Exception as e:
            # Only show connection errors if we have a token (user is logged in)
            if self.api_client.token:
                show_error("Connection Error", str(e))
    
    def update_display(self):
        """Update display with summary data"""
        if not self.summary_data:
            return
        
        data = self.summary_data
        display_currency = self.display_currency.get()
        
        # Get currency-specific data
        net_btc = data.get('net_btc', 0)
        
        # Get cost basis and current value for selected currency
        if display_currency == 'USD':
            net_cost = data.get('net_cost_basis_usd', 0)
            current_value = data.get('current_value_usd')
            btc_price = data.get('btc_price_usd')
            savings_cost = data.get('savings', {}).get('cost_usd', 0)
            spending_cost = data.get('spending', {}).get('cost_usd', 0)
        elif display_currency == 'CAD':
            net_cost = data.get('net_cost_basis_cad', 0)
            current_value = data.get('current_value_cad')
            btc_price = data.get('btc_price_cad')
            savings_cost = data.get('savings', {}).get('cost_cad', 0)
            spending_cost = data.get('spending', {}).get('cost_cad', 0)
        elif display_currency == 'EUR':
            net_cost = data.get('net_cost_basis_eur', 0)
            current_value = data.get('current_value_eur')
            btc_price = data.get('btc_price_eur')
            savings_cost = data.get('savings', {}).get('cost_eur', 0)
            spending_cost = data.get('spending', {}).get('cost_eur', 0)
        elif display_currency == 'GBP':
            net_cost = data.get('net_cost_basis_gbp', 0)
            current_value = data.get('current_value_gbp')
            btc_price = data.get('btc_price_gbp')
            savings_cost = data.get('savings', {}).get('cost_gbp', 0)
            spending_cost = data.get('spending', {}).get('cost_gbp', 0)
        
        # Update labels
        self.net_btc_label.config(text=f"Net BTC: {format_btc_amount(net_btc)}")
        self.net_cost_label.config(text=f"Net Cost Basis: {format_currency(net_cost, display_currency)}")
        
        if current_value is not None:
            self.current_value_label.config(text=f"Current Value: {format_currency(current_value, display_currency)}")
            
            # Calculate gain/loss
            gain_loss = current_value - net_cost
            color = "#2ECC71" if gain_loss >= 0 else "#E74C3C"
            sign = "+" if gain_loss >= 0 else ""
            
            self.gain_loss_label.config(
                text=f"Gain/Loss: {sign}{format_currency(gain_loss, display_currency)}",
                fg=color)
        else:
            self.current_value_label.config(text="Current Value: Price unavailable")
            self.gain_loss_label.config(text="Gain/Loss: Price unavailable", fg="gray")
        
        # Breakdown
        savings = data.get('savings', {})
        spending = data.get('spending', {})
        
        self.savings_btc_label.config(text=f"BTC: {format_btc_amount(savings.get('btc', 0))}")
        self.savings_cost_label.config(text=f"Cost: {format_currency(savings_cost, display_currency)}")
        
        self.spending_btc_label.config(text=f"BTC: {format_btc_amount(spending.get('btc', 0))}")
        self.spending_cost_label.config(text=f"Cost: {format_currency(spending_cost, display_currency)}")
        
        # Price
        if btc_price is not None:
            self.btc_price_label.config(text=f"BTC Price: {format_currency(btc_price, display_currency)}")
        else:
            self.btc_price_label.config(text="BTC Price: Unavailable")
    
    def on_currency_change(self, event=None):
        """Handle currency filter change"""
        self.update_display()

class TransactionTab:
    """Base class for transaction tabs (savings/spending)"""
    
    def __init__(self, parent, api_client: APIClient, transaction_type: str, on_transaction_added):
        self.parent = parent
        self.api_client = api_client
        self.transaction_type = transaction_type
        self.on_transaction_added = on_transaction_added
        self.frame = ttk.Frame(parent)
        self.transactions = []
        self.item_to_transaction_id = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup transaction UI"""
        container = tk.Frame(self.frame)
        container.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title
        title_text = "Bitcoin Savings" if self.transaction_type == 'save' else "Bitcoin Spending"
        tk.Label(container, text=title_text, font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Add transaction form
        self.create_transaction_form(container)
        
        # Transactions list
        self.create_transactions_list(container)
        
        # Don't load transactions during initialization - wait for login
    
    def create_transaction_form(self, parent):
        """Create transaction form"""
        form_frame = tk.LabelFrame(parent, text=f"Add New {self.transaction_type.title()}", 
                                  font=("Arial", 12, "bold"), padx=10, pady=10)
        form_frame.pack(fill="x", pady=(0, 20))
        
        # Form fields in a grid
        fields_frame = tk.Frame(form_frame)
        fields_frame.pack(fill="x", pady=10)
        
        # Date
        tk.Label(fields_frame, text="Date (YYYY-MM-DD):", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.date_entry = tk.Entry(fields_frame, width=15, font=("Arial", 10))
        self.date_entry.grid(row=0, column=1, padx=(0, 20))
        self.date_entry.insert(0, get_current_date())
        
        # BTC Amount
        tk.Label(fields_frame, text="BTC Amount:", font=("Arial", 10)).grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.btc_amount_entry = tk.Entry(fields_frame, width=15, font=("Arial", 10))
        self.btc_amount_entry.grid(row=0, column=3, padx=(0, 20))
        
        # Currency selection
        tk.Label(fields_frame, text="Currency:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.currency_var = tk.StringVar(value="USD")
        currency_frame = tk.Frame(fields_frame)
        currency_frame.grid(row=1, column=1, columnspan=3, sticky="w", pady=(10, 0))
        
        tk.Radiobutton(currency_frame, text="USD", variable=self.currency_var, 
                      value="USD", font=("Arial", 9)).pack(side="left")
        tk.Radiobutton(currency_frame, text="CAD", variable=self.currency_var, 
                      value="CAD", font=("Arial", 9)).pack(side="left")
        tk.Radiobutton(currency_frame, text="EUR", variable=self.currency_var, 
                      value="EUR", font=("Arial", 9)).pack(side="left")
        tk.Radiobutton(currency_frame, text="GBP", variable=self.currency_var, 
                      value="GBP", font=("Arial", 9)).pack(side="left")
        
        # Cost
        tk.Label(fields_frame, text="Cost:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.cost_entry = tk.Entry(fields_frame, width=15, font=("Arial", 10))
        self.cost_entry.grid(row=2, column=1, padx=(0, 20), pady=(10, 0))
        
        # Notes
        tk.Label(form_frame, text="Notes (optional):", font=("Arial", 10)).pack(anchor="w", pady=(10, 0))
        self.notes_entry = tk.Text(form_frame, width=60, height=3, font=("Arial", 10))
        self.notes_entry.pack(fill="x", pady=(5, 10))
        
        # Add button
        action_text = "Add Saving" if self.transaction_type == 'save' else "Add Spending"
        button_color = "#2ECC71" if self.transaction_type == 'save' else "#E74C3C"
        
        tk.Button(form_frame, text=action_text, command=self.add_transaction,
                 bg=button_color, fg="white", font=("Arial", 11, "bold")).pack(pady=(0, 10))
    
    def create_transactions_list(self, parent):
        """Create transactions list"""
        list_frame = tk.LabelFrame(parent, text=f"Recent {self.transaction_type.title()}s", 
                                  font=("Arial", 12, "bold"), padx=10, pady=10)
        list_frame.pack(fill="both", expand=True)
        
        # Currency filter
        filter_frame = tk.Frame(list_frame)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(filter_frame, text="Show cost in:", font=("Arial", 10)).pack(side="left", padx=(0, 10))
        self.currency_filter = ttk.Combobox(filter_frame, width=15, state="readonly", font=("Arial", 10))
        self.currency_filter['values'] = CURRENCIES
        self.currency_filter.set('USD')
        self.currency_filter.pack(side="left")
        self.currency_filter.bind('<<ComboboxSelected>>', self.on_currency_change)
        
        # Add currency-based filtering
        tk.Label(filter_frame, text="Filter by currency:", font=("Arial", 10)).pack(side="left", padx=(20, 10))
        self.currency_type_filter = ttk.Combobox(filter_frame, width=10, state="readonly", font=("Arial", 10))
        self.currency_type_filter['values'] = ('All', 'USD', 'CAD', 'EUR', 'GBP')
        self.currency_type_filter.set('All')
        self.currency_type_filter.pack(side="left")
        self.currency_type_filter.bind('<<ComboboxSelected>>', self.on_currency_type_change)
        
        # Refresh button
        tk.Button(filter_frame, text="Refresh", command=self.refresh_transactions,
                 bg="#3498DB", fg="white", font=("Arial", 9)).pack(side="right")
        
        # Transactions table
        table_frame = tk.Frame(list_frame)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        columns = ("Date", "BTC Amount", "Cost", "Notes")
        self.transactions_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        # Set column widths
        column_widths = {"Date": 100, "BTC Amount": 140, "Cost": 120, "Notes": 200}
        for col in columns:
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=column_widths[col])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscrollcommand=scrollbar.set)
        
        self.transactions_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Action buttons
        action_frame = tk.Frame(list_frame)
        action_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(action_frame, text="Edit Selected", command=self.edit_transaction,
                 bg="#F39C12", fg="white", font=("Arial", 9)).pack(side="left", padx=(0, 10))
        tk.Button(action_frame, text="Delete Selected", command=self.delete_transaction,
                 bg="#E74C3C", fg="white", font=("Arial", 9)).pack(side="left")
    
    def add_transaction(self):
        """Add new transaction"""
        try:
            # Get form data
            transaction_date = self.date_entry.get().strip()
            btc_amount = self.btc_amount_entry.get().strip()
            cost = self.cost_entry.get().strip()
            currency = self.currency_var.get()
            notes = self.notes_entry.get("1.0", tk.END).strip()
            
            # Validate
            validation = FormValidator.validate_transaction_form(
                transaction_date, btc_amount, cost, self.transaction_type
            )
            
            if not validation['is_valid']:
                show_error("Validation Error", "\n".join(validation['errors']))
                return
            
            # Convert values
            btc_amount = validate_float(btc_amount, "BTC amount")
            cost = validate_float(cost, "Cost")
            
            # Convert to all currencies (approximate exchange rates)
            if currency == "USD":
                cost_usd = cost
                cost_cad = cost * 1.35
                cost_eur = cost * 0.92
                cost_gbp = cost * 0.79
            elif currency == "CAD":
                cost_cad = cost
                cost_usd = cost / 1.35
                cost_eur = cost_usd * 0.92
                cost_gbp = cost_usd * 0.79
            elif currency == "EUR":
                cost_eur = cost
                cost_usd = cost / 0.92
                cost_cad = cost_usd * 1.35
                cost_gbp = cost_usd * 0.79
            elif currency == "GBP":
                cost_gbp = cost
                cost_usd = cost / 0.79
                cost_cad = cost_usd * 1.35
                cost_eur = cost_usd * 0.92
            
            # Prepare data
            data = {
                "transaction_date": transaction_date,
                "transaction_type": self.transaction_type,
                "btc_amount": btc_amount,
                "cost_usd": cost_usd,
                "cost_cad": cost_cad,
                "cost_eur": cost_eur,
                "cost_gbp": cost_gbp,
                "currency": currency,
                "notes": notes
            }
            
            # Submit
            response, status_code = self.api_client.add_transaction(data)
            
            if status_code == 201:
                action_text = "saved" if self.transaction_type == 'save' else "spent"
                show_info("Success", f"Transaction {action_text} successfully!\nAmount: {format_btc_amount(btc_amount)} BTC\nCost: {format_currency(cost)} {currency}")
                self.clear_form()
                self.refresh_transactions()
                self.on_transaction_added()
            else:
                show_error("Add Failed", response.get("msg", "Failed to add transaction"))
        
        except ValueError as e:
            show_error("Validation Error", str(e))
        except Exception as e:
            show_error("Connection Error", str(e))
    
    def clear_form(self):
        """Clear the form fields"""
        self.btc_amount_entry.delete(0, tk.END)
        self.cost_entry.delete(0, tk.END)
        self.notes_entry.delete("1.0", tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, get_current_date())
    
    def refresh_transactions(self):
        """Refresh transactions list"""
        # Don't try to refresh if no token is set
        if not self.api_client.token:
            return
            
        try:
            # Get currency filter
            currency_filter = self.currency_type_filter.get() if hasattr(self, 'currency_type_filter') else 'All'
            currency_param = None if currency_filter == 'All' else currency_filter
            
            response, status_code = self.api_client.get_transactions(self.transaction_type, currency_param)
            
            if status_code == 200:
                self.transactions = response
                self.display_transactions()
            elif status_code == 401:
                # Session expired - don't show error during normal operation
                pass
            else:
                show_error("Transactions Error", response.get("msg", "Failed to load transactions"))
        except Exception as e:
            # Only show connection errors if we have a token (user is logged in)
            if self.api_client.token:
                show_error("Connection Error", str(e))
    
    def on_currency_type_change(self, event=None):
        """Handle currency type filter change"""
        self.refresh_transactions()
    
    def display_transactions(self):
        """Display transactions in the table"""
        # Clear existing items
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        self.item_to_transaction_id = {}
        currency = self.currency_filter.get()
        
        # Add transactions to tree
        for transaction in self.transactions:
            # Get the actual cost in the selected currency
            cost_value = CurrencyConverter.get_cost_in_currency(transaction, currency)
            cost_display = format_currency(cost_value, currency)
            
            item = self.transactions_tree.insert("", "end", values=(
                transaction["transaction_date"],
                format_btc_amount(transaction['btc_amount']),
                cost_display,
                transaction["notes"]
            ))
            self.item_to_transaction_id[item] = transaction["id"]
    
    def on_currency_change(self, event=None):
        """Handle currency filter change"""
        self.display_transactions()
    
    def edit_transaction(self):
        """Edit selected transaction"""
        selected = self.transactions_tree.selection()
        if not selected:
            show_warning("No Selection", "Please select a transaction to edit")
            return
        
        item = selected[0]
        transaction_id = self.item_to_transaction_id.get(item)
        
        # Find transaction data
        transaction_data = next((t for t in self.transactions if t["id"] == transaction_id), None)
        if not transaction_data:
            show_error("Not Found", "Transaction not found")
            return
        
        self.show_edit_dialog(transaction_data)
    
    def show_edit_dialog(self, transaction_data: Dict):
        """Show edit transaction dialog"""
        edit_window = tk.Toplevel(self.parent)
        edit_window.title(f"Edit {self.transaction_type.title()}")
        edit_window.geometry("500x400")
        
        tk.Label(edit_window, text=f"Edit {self.transaction_type.title()}", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Form fields
        tk.Label(edit_window, text="Date (YYYY-MM-DD):").pack()
        date_entry = tk.Entry(edit_window, width=30)
        date_entry.pack(pady=5)
        date_entry.insert(0, transaction_data["transaction_date"])
        
        tk.Label(edit_window, text="BTC Amount:").pack()
        btc_entry = tk.Entry(edit_window, width=30)
        btc_entry.pack(pady=5)
        btc_entry.insert(0, str(transaction_data["btc_amount"]))
        
        tk.Label(edit_window, text="Cost USD:").pack()
        usd_entry = tk.Entry(edit_window, width=30)
        usd_entry.pack(pady=5)
        usd_entry.insert(0, str(transaction_data["cost_usd"]))
        
        tk.Label(edit_window, text="Cost CAD:").pack()
        cad_entry = tk.Entry(edit_window, width=30)
        cad_entry.pack(pady=5)
        cad_entry.insert(0, str(transaction_data["cost_cad"]))
        
        tk.Label(edit_window, text="Cost EUR:").pack()
        eur_entry = tk.Entry(edit_window, width=30)
        eur_entry.pack(pady=5)
        eur_entry.insert(0, str(transaction_data.get("cost_eur", 0)))
        
        tk.Label(edit_window, text="Cost GBP:").pack()
        gbp_entry = tk.Entry(edit_window, width=30)
        gbp_entry.pack(pady=5)
        gbp_entry.insert(0, str(transaction_data.get("cost_gbp", 0)))
        
        tk.Label(edit_window, text="Currency:").pack()
        currency_entry = tk.Entry(edit_window, width=30)
        currency_entry.pack(pady=5)
        currency_entry.insert(0, transaction_data.get("currency", "USD"))
        
        tk.Label(edit_window, text="Notes:").pack()
        notes_entry = tk.Text(edit_window, width=40, height=4)
        notes_entry.pack(pady=5)
        notes_entry.insert("1.0", transaction_data["notes"])
        
        def update_transaction():
            try:
                # Validate form
                validation = FormValidator.validate_transaction_form(
                    date_entry.get(),
                    btc_entry.get(),
                    usd_entry.get(),
                    self.transaction_type
                )
                
                if not validation['is_valid']:
                    show_error("Validation Error", "\n".join(validation['errors']))
                    return
                
                data = {
                    "transaction_date": date_entry.get(),
                    "transaction_type": self.transaction_type,
                    "btc_amount": validate_float(btc_entry.get(), "BTC amount"),
                    "cost_usd": validate_float(usd_entry.get(), "USD cost"),
                    "cost_cad": validate_float(cad_entry.get(), "CAD cost"),
                    "cost_eur": validate_float(eur_entry.get(), "EUR cost"),
                    "cost_gbp": validate_float(gbp_entry.get(), "GBP cost"),
                    "currency": currency_entry.get(),
                    "notes": notes_entry.get("1.0", tk.END).strip()
                }
                
                response, status_code = self.api_client.update_transaction(transaction_data["id"], data)
                
                if status_code == 200:
                    show_info("Success", "Transaction updated successfully!")
                    edit_window.destroy()
                    self.refresh_transactions()
                    self.on_transaction_added()
                else:
                    show_error("Update Failed", response.get("msg", "Failed to update transaction"))
            except ValueError as e:
                show_error("Validation Error", str(e))
            except Exception as e:
                show_error("Connection Error", str(e))
        
        tk.Button(edit_window, text="Update Transaction", command=update_transaction,
                 bg="#F39C12", fg="white").pack(pady=10)
    
    def delete_transaction(self):
        """Delete selected transaction"""
        selected = self.transactions_tree.selection()
        if not selected:
            show_warning("No Selection", "Please select a transaction to delete")
            return
        
        item = selected[0]
        transaction_id = self.item_to_transaction_id.get(item)
        
        action_text = "saving" if self.transaction_type == 'save' else "spending"
        if confirm_action("Confirm Delete", f"Are you sure you want to delete this {action_text} transaction?"):
            try:
                response, status_code = self.api_client.delete_transaction(transaction_id)
                
                if status_code == 200:
                    show_info("Success", "Transaction deleted successfully!")
                    self.refresh_transactions()
                    self.on_transaction_added()
                else:
                    show_error("Delete Failed", response.get("msg", "Failed to delete transaction"))
            except Exception as e:
                show_error("Connection Error", str(e))

class CSVImportTab:
    """Handles CSV import functionality"""
    
    def __init__(self, parent, api_client: APIClient, on_import_complete):
        self.parent = parent
        self.api_client = api_client
        self.on_import_complete = on_import_complete
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup CSV import UI"""
        container = tk.Frame(self.frame)
        container.pack(pady=20, padx=20, fill="both", expand=True)
        
        tk.Label(container, text="Import CSV Data", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Instructions
        instructions = tk.Text(container, width=80, height=8, font=("Arial", 10))
        instructions.pack(pady=(0, 20))
        
        instructions.insert("1.0", """CSV Import Instructions:

1. Your CSV file should have the following columns:
   - date (YYYY-MM-DD format)
   - transaction_type (either 'save' or 'spend')
   - btc_amount (decimal number)
   - cost_usd (decimal number)
   - cost_cad (decimal number)
   - cost_eur (decimal number) [optional]
   - cost_gbp (decimal number) [optional]
   - currency (USD, CAD, EUR, or GBP) [optional, defaults to USD]
   - notes (optional text)

2. The first row should contain column headers.

3. Example CSV format:
   date,transaction_type,btc_amount,cost_usd,cost_cad,cost_eur,cost_gbp,currency,notes
   2024-01-15,save,0.00125000,50.00,67.50,46.00,39.50,USD,First BTC purchase
   2024-02-01,spend,0.00050000,25.00,33.75,23.00,19.75,USD,Paid for coffee
""")
        
        instructions.config(state="disabled")
        
        # File selection
        file_frame = tk.Frame(container)
        file_frame.pack(pady=(0, 20))
        
        tk.Label(file_frame, text="Select CSV File:", font=("Arial", 12)).pack(side="left", padx=(0, 10))
        
        self.file_path_var = tk.StringVar()
        self.file_path_entry = tk.Entry(file_frame, textvariable=self.file_path_var, width=50, font=("Arial", 10))
        self.file_path_entry.pack(side="left", padx=(0, 10))
        
        tk.Button(file_frame, text="Browse", command=self.browse_file,
                 bg="#3498DB", fg="white", font=("Arial", 10)).pack(side="left")
        
        # Import button
        tk.Button(container, text="Import CSV", command=self.import_csv,
                 bg="#2ECC71", fg="white", font=("Arial", 12, "bold")).pack(pady=20)
        
        # Progress area
        self.progress_text = tk.Text(container, width=80, height=10, font=("Arial", 9))
        self.progress_text.pack(fill="both", expand=True)
    
    def browse_file(self):
        """Browse for CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def import_csv(self):
        """Import CSV file"""
        file_path = self.file_path_var.get()
        if not file_path:
            show_error("No File Selected", "Please select a CSV file to import")
            return
        
        try:
            self.progress_text.delete("1.0", tk.END)
            self.progress_text.insert(tk.END, "Starting CSV import...\n")
            self.progress_text.update()
            
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Check required columns
                required_columns = ['date', 'transaction_type', 'btc_amount', 'cost_usd', 'cost_cad']
                missing_columns = [col for col in required_columns if col not in reader.fieldnames]
                
                if missing_columns:
                    show_error("CSV Error", f"Missing required columns: {', '.join(missing_columns)}")
                    return
                
                imported_count = 0
                error_count = 0
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Validate and prepare data
                        data = {
                            "transaction_date": row['date'].strip(),
                            "transaction_type": row['transaction_type'].strip().lower(),
                            "btc_amount": float(row['btc_amount']),
                            "cost_usd": float(row['cost_usd']),
                            "cost_cad": float(row['cost_cad']),
                            "cost_eur": float(row.get('cost_eur', 0)),
                            "cost_gbp": float(row.get('cost_gbp', 0)),
                            "currency": row.get('currency', 'USD').strip().upper(),
                            "notes": row.get('notes', '').strip()
                        }
                        
                        # Validate transaction type
                        if data['transaction_type'] not in ['save', 'spend']:
                            raise ValueError(f"Invalid transaction type: {data['transaction_type']}")
                        
                        # Validate date
                        if not validate_date(data['transaction_date']):
                            raise ValueError(f"Invalid date format: {data['transaction_date']}")
                        
                        # Submit transaction
                        response, status_code = self.api_client.add_transaction(data)
                        
                        if status_code == 201:
                            imported_count += 1
                            self.progress_text.insert(tk.END, f"Row {row_num}: Imported successfully\n")
                        else:
                            error_count += 1
                            self.progress_text.insert(tk.END, f"Row {row_num}: Error - {response.get('msg', 'Unknown error')}\n")
                    
                    except Exception as e:
                        error_count += 1
                        self.progress_text.insert(tk.END, f"Row {row_num}: Error - {str(e)}\n")
                    
                    self.progress_text.see(tk.END)
                    self.progress_text.update()
                
                # Summary
                self.progress_text.insert(tk.END, f"\nImport completed!\n")
                self.progress_text.insert(tk.END, f"Successfully imported: {imported_count} transactions\n")
                self.progress_text.insert(tk.END, f"Errors: {error_count}\n")
                self.progress_text.see(tk.END)
                
                if imported_count > 0:
                    show_info("Import Complete", f"Successfully imported {imported_count} transactions!")
                    self.on_import_complete()
                else:
                    show_warning("Import Warning", "No transactions were imported. Please check the file format.")
        
        except Exception as e:
            show_error("Import Error", f"Failed to import CSV: {str(e)}")

class BTCApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("BTC Portfolio Tracker v2.0")
        self.root.geometry("1000x700")
        self.root.configure(bg="white")
        
        self.api_client = APIClient()
        
        # Create UI components
        self.create_login_frame()
        self.create_main_tabs()
        
        # Show login first
        self.show_login()
    
    def create_login_frame(self):
        """Create login frame"""
        self.login_frame = LoginFrame(self.root, self.api_client, self.on_login_success)
    
    def create_main_tabs(self):
        """Create all application tabs"""
        self.notebook = ttk.Notebook(self.root)
        
        # Summary tab
        self.summary_tab = SummaryTab(self.notebook, self.api_client, self.logout)
        self.notebook.add(self.summary_tab.frame, text="📊 Summary")
        
        # Savings tab
        self.savings_tab = TransactionTab(self.notebook, self.api_client, 'save', self.on_transaction_added)
        self.notebook.add(self.savings_tab.frame, text="💰 Savings")
        
        # Spending tab
        self.spending_tab = TransactionTab(self.notebook, self.api_client, 'spend', self.on_transaction_added)
        self.notebook.add(self.spending_tab.frame, text="💸 Spending")
        
        # CSV import tab
        self.csv_import_tab = CSVImportTab(self.notebook, self.api_client, self.on_import_complete)
        self.notebook.add(self.csv_import_tab.frame, text="📁 Import CSV")
    
    def on_login_success(self, username: str):
        """Handle successful login"""
        self.show_main_app()
        self.summary_tab.refresh_summary()
        self.savings_tab.refresh_transactions()
        self.spending_tab.refresh_transactions()
        show_info("Welcome", f"Welcome, {username}!")
    
    def on_transaction_added(self):
        """Handle transaction addition"""
        self.summary_tab.refresh_summary()
        self.savings_tab.refresh_transactions()
        self.spending_tab.refresh_transactions()
    
    def on_import_complete(self):
        """Handle import completion"""
        self.summary_tab.refresh_summary()
        self.savings_tab.refresh_transactions()
        self.spending_tab.refresh_transactions()
    
    def show_login(self):
        """Show login screen"""
        self.notebook.pack_forget()
        self.login_frame.pack(pady=50)
    
    def show_main_app(self):
        """Show main application"""
        self.login_frame.pack_forget()
        self.notebook.pack(fill="both", expand=True)
    
    def logout(self):
        """Handle logout"""
        self.api_client.set_token(None)
        self.show_login()

def main():
    """Main entry point"""
    root = tk.Tk()
    app = BTCApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
