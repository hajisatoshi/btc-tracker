"""
Clean and refactored BTC Portfolio Tracker GUI
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import requests
import csv
from typing import Dict, List, Optional

# Import utility functions
try:
    from utils import (
        show_error, show_info, show_warning, confirm_action,
        validate_float, validate_date, format_btc_amount,
        create_button, create_label, clear_frame, get_current_date,
        FormValidator, WidgetHelper, format_currency_list,
        BUTTON_COLORS, FONT_HEADER
    )
except ImportError:
    # Fallback implementations if utils module is not available
    def show_error(title, message):
        messagebox.showerror(title, message)
    
    def show_info(title, message):
        messagebox.showinfo(title, message)
    
    def show_warning(title, message):
        messagebox.showwarning(title, message)
    
    def confirm_action(title, message):
        return messagebox.askyesno(title, message)
    
    def validate_float(value, field_name):
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Invalid number format for {field_name}")
    
    def validate_date(date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def format_btc_amount(amount):
        return f"{amount:.8f}"
    
    def create_button(parent, text, command, button_type='primary', **kwargs):
        colors = {'bg': '#007bff', 'fg': 'white'}
        return tk.Button(parent, text=text, command=command, bg=colors['bg'], fg=colors['fg'], **kwargs)
    
    def create_label(parent, text, font_type='normal', **kwargs):
        fonts = {'header': ("Arial", 14, "bold"), 'normal': ("Arial", 10)}
        font = fonts.get(font_type, fonts['normal'])
        return tk.Label(parent, text=text, font=font, **kwargs)
    
    def clear_frame(frame):
        for widget in frame.winfo_children():
            widget.destroy()
    
    def get_current_date():
        return datetime.now().strftime("%Y-%m-%d")
    
    def format_currency_list():
        return ('USD', 'CAD', 'Swiss Franc', 'Ounces of Gold')
    
    class FormValidator:
        @staticmethod
        def validate_login_form(username, password):
            errors = []
            if not username:
                errors.append("Username is required")
            if not password:
                errors.append("Password is required")
            return {'is_valid': len(errors) == 0, 'errors': errors}
        
        @staticmethod
        def validate_registration_form(username, password, confirm_password):
            errors = []
            if not username:
                errors.append("Username is required")
            if not password:
                errors.append("Password is required")
            if password != confirm_password:
                errors.append("Passwords do not match")
            return {'is_valid': len(errors) == 0, 'errors': errors}
        
        @staticmethod
        def validate_purchase_form(date, btc_amount, cost):
            errors = []
            if not date:
                errors.append("Purchase date is required")
            if not btc_amount:
                errors.append("BTC amount is required")
            if not cost:
                errors.append("Cost is required")
            return {'is_valid': len(errors) == 0, 'errors': errors}
    
    class WidgetHelper:
        @staticmethod
        def create_form_field(parent, label_text, entry_type='text', **kwargs):
            label = create_label(parent, label_text)
            label.pack(pady=(10, 0))
            
            if entry_type == 'password':
                entry = tk.Entry(parent, show="*", **kwargs)
            elif entry_type == 'textarea':
                entry = tk.Text(parent, **kwargs)
            else:
                entry = tk.Entry(parent, **kwargs)
            
            entry.pack(pady=(0, 5))
            return label, entry
        
        @staticmethod
        def create_radio_group(parent, label_text, options, variable, **kwargs):
            create_label(parent, label_text).pack()
            
            radio_frame = tk.Frame(parent)
            radio_frame.pack(pady=5)
            
            for option in options:
                radio = tk.Radiobutton(radio_frame, text=option, variable=variable, value=option, **kwargs)
                radio.pack(side="left", padx=10)
            
            return radio_frame

API_URL = "http://localhost:5000"

class CurrencyConverter:
    """Handles currency conversion logic"""
    
    CONVERSION_RATES = {
        'USD': 1.0,
        'CAD': 1.35,
        'Swiss Franc': 0.92,
        'Ounces of Gold': 0.0005  # Approximate: $2000 per ounce
    }
    
    CURRENCY_SYMBOLS = {
        'USD': '$',
        'CAD': '$',
        'Swiss Franc': 'CHF',
        'Ounces of Gold': 'oz Au'
    }
    
    @classmethod
    def convert_from_usd(cls, usd_amount: float, target_currency: str) -> str:
        """Convert USD amount to target currency with proper formatting"""
        if target_currency not in cls.CONVERSION_RATES:
            return f"${usd_amount:.2f} USD"
        
        converted_amount = usd_amount * cls.CONVERSION_RATES[target_currency]
        symbol = cls.CURRENCY_SYMBOLS[target_currency]
        
        if target_currency == 'Ounces of Gold':
            return f"{converted_amount:.6f} {symbol}"
        elif target_currency == 'Swiss Franc':
            return f"{converted_amount:.2f} {symbol}"
        else:
            return f"{symbol}{converted_amount:.2f} {target_currency}"
    
    @classmethod
    def convert_to_usd(cls, amount: float, source_currency: str) -> float:
        """Convert amount from source currency to USD"""
        if source_currency == "USD":
            return amount
        elif source_currency == "CAD":
            return amount / 1.35
        else:
            return amount  # Default to treating as USD

class APIClient:
    """Handles all API communication"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
    
    def set_token(self, token: str):
        self.token = token
    
    def get_headers(self) -> Dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> tuple:
        """Make API request and return response"""
        url = f"{API_URL}{endpoint}"
        
        try:
            if method == "GET":
                resp = requests.get(url, headers=self.get_headers())
            elif method == "POST":
                resp = requests.post(url, json=data, headers=self.get_headers())
            elif method == "PUT":
                resp = requests.put(url, json=data, headers=self.get_headers())
            elif method == "DELETE":
                resp = requests.delete(url, headers=self.get_headers())
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return resp.json(), resp.status_code
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {str(e)}\nMake sure the backend server is running!")
    
    def login(self, username: str, password: str) -> tuple:
        """Authenticate user and return response"""
        data = {"username": username, "password": password}
        return self._make_request("POST", "/login", data)
    
    def register(self, username: str, password: str) -> tuple:
        """Register new user and return response"""
        data = {"username": username, "password": password}
        return self._make_request("POST", "/register", data)
    
    def get_portfolio(self) -> tuple:
        """Get portfolio summary"""
        return self._make_request("GET", "/portfolio/summary")
    
    def get_purchases(self) -> tuple:
        """Get all purchases"""
        return self._make_request("GET", "/purchases")
    
    def add_purchase(self, purchase_data: Dict) -> tuple:
        """Add new purchase"""
        return self._make_request("POST", "/purchases", purchase_data)
    
    def update_purchase(self, purchase_id: int, purchase_data: Dict) -> tuple:
        """Update existing purchase"""
        return self._make_request("PUT", f"/purchases/{purchase_id}", purchase_data)
    
    def delete_purchase(self, purchase_id: int) -> tuple:
        """Delete purchase"""
        return self._make_request("DELETE", f"/purchases/{purchase_id}")

class LoginFrame:
    """Handles login and registration UI"""
    
    def __init__(self, parent, api_client: APIClient, on_login_success):
        self.parent = parent
        self.api_client = api_client
        self.on_login_success = on_login_success
        self.frame = tk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        container = tk.Frame(self.frame)
        container.pack()
        
        create_label(container, "BTC Portfolio Tracker", 'header').pack(pady=10)
        
        self.username_label, self.username_entry = WidgetHelper.create_form_field(
            container, "Username:", width=30
        )
        
        self.password_label, self.password_entry = WidgetHelper.create_form_field(
            container, "Password:", entry_type='password', width=30
        )
        
        create_button(container, "Login", self.login, 'login').pack(pady=10)
        create_button(container, "Register New User", self.show_register, 'register').pack()
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        validation = FormValidator.validate_login_form(username, password)
        if not validation['is_valid']:
            show_error("Validation Error", "\n".join(validation['errors']))
            return
        
        try:
            response, status_code = self.api_client.login(username, password)
            
            if status_code == 200:
                self.api_client.set_token(response["access_token"])
                self.on_login_success(username)
            else:
                show_error("Login Failed", response.get("msg", "Login failed"))
        except Exception as e:
            show_error("Connection Error", str(e))
    
    def show_register(self):
        """Show registration dialog"""
        register_window = tk.Toplevel(self.parent)
        register_window.title("Register New User")
        register_window.geometry("350x300")
        register_window.resizable(False, False)
        
        create_label(register_window, "Register New User", 'header').pack(pady=10)
        
        username_label, username_entry = WidgetHelper.create_form_field(
            register_window, "Username:", width=30
        )
        
        password_label, password_entry = WidgetHelper.create_form_field(
            register_window, "Password:", entry_type='password', width=30
        )
        
        confirm_label, confirm_entry = WidgetHelper.create_form_field(
            register_window, "Confirm Password:", entry_type='password', width=30
        )
        
        def register_user():
            username = username_entry.get()
            password = password_entry.get()
            confirm_password = confirm_entry.get()
            
            validation = FormValidator.validate_registration_form(username, password, confirm_password)
            if not validation['is_valid']:
                show_error("Validation Error", "\n".join(validation['errors']))
                return
            
            try:
                response, status_code = self.api_client.register(username, password)
                
                if status_code == 201:
                    show_info("Success", "User registered successfully! You can now log in.")
                    register_window.destroy()
                    self.username_entry.delete(0, tk.END)
                    self.username_entry.insert(0, username)
                else:
                    show_error("Registration Failed", response.get("msg", "Registration failed"))
            except Exception as e:
                show_error("Connection Error", str(e))
        
        create_button(register_window, "Register", register_user, 'register').pack(pady=10)
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        self.frame.pack_forget()

class PortfolioTab:
    """Handles portfolio summary display"""
    
    def __init__(self, parent, api_client: APIClient, on_logout):
        self.parent = parent
        self.api_client = api_client
        self.on_logout = on_logout
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        container = tk.Frame(self.frame)
        container.pack(pady=20, padx=20, fill="both", expand=True)
        
        create_label(container, "Portfolio Summary", 'header').pack(pady=10)
        
        # Currency filter
        filter_frame = tk.Frame(container)
        filter_frame.pack(pady=5)
        
        create_label(filter_frame, "Show values in:").pack(side="left", padx=5)
        self.currency_filter = ttk.Combobox(filter_frame, width=15, state="readonly")
        self.currency_filter['values'] = format_currency_list()
        self.currency_filter.set('USD')
        self.currency_filter.pack(side="left", padx=5)
        self.currency_filter.bind('<<ComboboxSelected>>', self.on_currency_change)
        
        self.summary_label = tk.Label(container, text="", justify="left", font=("Arial", 10))
        self.summary_label.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(container)
        button_frame.pack(pady=10)
        
        create_button(button_frame, "Refresh Portfolio", self.refresh_portfolio, 'refresh').pack(pady=5)
        create_button(button_frame, "Logout", self.on_logout, 'logout').pack(pady=5)
    
    def refresh_portfolio(self):
        """Refresh portfolio data"""
        try:
            response, status_code = self.api_client.get_portfolio()
            
            if status_code == 200:
                self.display_portfolio(response)
            else:
                show_error("Portfolio Error", response.get("msg", "Failed to fetch portfolio"))
        except Exception as e:
            show_error("Connection Error", str(e))
    
    def display_portfolio(self, data: Dict):
        """Display portfolio data"""
        currency = self.currency_filter.get()
        
        # Convert values to selected currency
        cost_basis = CurrencyConverter.convert_from_usd(data['cost_basis_usd'], currency)
        current_value = CurrencyConverter.convert_from_usd(data['current_value_usd'], currency) if data['current_value_usd'] else "N/A"
        btc_price = CurrencyConverter.convert_from_usd(data['btc_price_usd'], currency) if data['btc_price_usd'] else "N/A"
        
        # Calculate profit/loss
        if data['current_value_usd'] and data['cost_basis_usd']:
            profit_loss_usd = data['current_value_usd'] - data['cost_basis_usd']
            profit_loss = CurrencyConverter.convert_from_usd(profit_loss_usd, currency)
            profit_loss_percent = ((data['current_value_usd'] - data['cost_basis_usd']) / data['cost_basis_usd']) * 100
            profit_loss_text = f"Profit/Loss: {profit_loss} ({profit_loss_percent:+.2f}%)"
        else:
            profit_loss_text = "Profit/Loss: N/A"
        
        summary = (
            f"Total BTC: {format_btc_amount(data['total_btc'])}\n"
            f"Cost Basis: {cost_basis}\n"
            f"Current Value: {current_value}\n"
            f"BTC Price: {btc_price}\n"
            f"{profit_loss_text}\n"
        )
        self.summary_label.config(text=summary)
    
    def on_currency_change(self, event=None):
        """Handle currency filter change"""
        self.refresh_portfolio()

class PurchasesTab:
    """Handles purchases list display and management"""
    
    def __init__(self, parent, api_client: APIClient):
        self.parent = parent
        self.api_client = api_client
        self.frame = ttk.Frame(parent)
        self.purchases = []
        self.item_to_purchase_id = {}
        self.setup_ui()
    
    def setup_ui(self):
        container = tk.Frame(self.frame)
        container.pack(pady=20, padx=20, fill="both", expand=True)
        
        create_label(container, "All Purchases", 'header').pack(pady=10)
        
        # Currency filter
        filter_frame = tk.Frame(container)
        filter_frame.pack(pady=5)
        
        create_label(filter_frame, "Show cost in:").pack(side="left", padx=5)
        self.currency_filter = ttk.Combobox(filter_frame, width=15, state="readonly")
        self.currency_filter['values'] = format_currency_list()
        self.currency_filter.set('USD')
        self.currency_filter.pack(side="left", padx=5)
        self.currency_filter.bind('<<ComboboxSelected>>', self.on_currency_change)
        
        # Create purchases table
        self.create_purchases_table(container)
        
        # Action buttons
        self.create_action_buttons(container)
    
    def create_purchases_table(self, parent):
        """Create the purchases table"""
        table_frame = tk.Frame(parent)
        table_frame.pack(fill="both", expand=True, pady=10)
        
        columns = ("Date", "BTC Amount", "Cost", "Notes")
        self.purchases_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Set column widths
        column_widths = {"Date": 100, "BTC Amount": 120, "Cost": 120, "Notes": 200}
        for col in columns:
            self.purchases_tree.heading(col, text=col)
            self.purchases_tree.column(col, width=column_widths[col])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.purchases_tree.yview)
        self.purchases_tree.configure(yscrollcommand=scrollbar.set)
        
        self.purchases_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_action_buttons(self, parent):
        """Create action buttons"""
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        
        create_button(btn_frame, "Refresh List", self.refresh_purchases, 'refresh').pack(pady=2)
        create_button(btn_frame, "Edit Selected", self.edit_purchase, 'edit').pack(pady=2)
        create_button(btn_frame, "Delete Selected", self.delete_purchase, 'delete').pack(pady=2)
    
    def refresh_purchases(self):
        """Refresh purchases list"""
        try:
            response, status_code = self.api_client.get_purchases()
            
            if status_code == 200:
                self.purchases = response
                self.display_purchases()
            else:
                show_error("Purchases Error", response.get("msg", "Failed to load purchases"))
        except Exception as e:
            show_error("Connection Error", str(e))
    
    def display_purchases(self):
        """Display purchases in the table"""
        # Clear existing items
        for item in self.purchases_tree.get_children():
            self.purchases_tree.delete(item)
        
        self.item_to_purchase_id = {}
        currency = self.currency_filter.get()
        
        # Add purchases to tree
        for purchase in self.purchases:
            cost_display = CurrencyConverter.convert_from_usd(purchase["cost_usd"], currency)
            
            item = self.purchases_tree.insert("", "end", values=(
                purchase["purchase_date"],
                format_btc_amount(purchase['btc_amount']),
                cost_display,
                purchase["notes"]
            ))
            self.item_to_purchase_id[item] = purchase["id"]
    
    def on_currency_change(self, event=None):
        """Handle currency filter change"""
        self.display_purchases()
    
    def edit_purchase(self):
        """Edit selected purchase"""
        selected = self.purchases_tree.selection()
        if not selected:
            show_warning("No Selection", "Please select a purchase to edit")
            return
        
        item = selected[0]
        purchase_id = self.item_to_purchase_id.get(item)
        
        # Find purchase data
        purchase_data = next((p for p in self.purchases if p["id"] == purchase_id), None)
        if not purchase_data:
            show_error("Not Found", "Purchase not found")
            return
        
        self.show_edit_dialog(purchase_data)
    
    def show_edit_dialog(self, purchase_data: Dict):
        """Show edit purchase dialog"""
        edit_window = tk.Toplevel(self.parent)
        edit_window.title("Edit Purchase")
        edit_window.geometry("400x400")
        
        create_label(edit_window, "Edit Purchase", 'header').pack(pady=10)
        
        # Form fields
        date_label, date_entry = WidgetHelper.create_form_field(
            edit_window, "Purchase Date (YYYY-MM-DD):", width=30
        )
        date_entry.insert(0, purchase_data["purchase_date"])
        
        btc_label, btc_entry = WidgetHelper.create_form_field(
            edit_window, "BTC Amount:", width=30
        )
        btc_entry.insert(0, str(purchase_data["btc_amount"]))
        
        usd_label, usd_entry = WidgetHelper.create_form_field(
            edit_window, "Cost USD:", width=30
        )
        usd_entry.insert(0, str(purchase_data["cost_usd"]))
        
        cad_label, cad_entry = WidgetHelper.create_form_field(
            edit_window, "Cost CAD:", width=30
        )
        cad_entry.insert(0, str(purchase_data["cost_cad"]))
        
        notes_label, notes_entry = WidgetHelper.create_form_field(
            edit_window, "Notes:", entry_type='textarea', width=40, height=4
        )
        notes_entry.insert("1.0", purchase_data["notes"])
        
        def update_purchase():
            try:
                # Validate form
                validation = FormValidator.validate_purchase_form(
                    date_entry.get(),
                    btc_entry.get(),
                    usd_entry.get()
                )
                
                if not validation['is_valid']:
                    show_error("Validation Error", "\n".join(validation['errors']))
                    return
                
                data = {
                    "purchase_date": date_entry.get(),
                    "btc_amount": validate_float(btc_entry.get(), "BTC amount"),
                    "cost_usd": validate_float(usd_entry.get(), "USD cost"),
                    "cost_cad": validate_float(cad_entry.get(), "CAD cost"),
                    "notes": notes_entry.get("1.0", tk.END).strip()
                }
                
                response, status_code = self.api_client.update_purchase(purchase_data["id"], data)
                
                if status_code == 200:
                    show_info("Success", "Purchase updated successfully!")
                    edit_window.destroy()
                    self.refresh_purchases()
                else:
                    show_error("Update Failed", response.get("msg", "Failed to update purchase"))
            except ValueError as e:
                show_error("Validation Error", str(e))
            except Exception as e:
                show_error("Connection Error", str(e))
        
        create_button(edit_window, "Update Purchase", update_purchase, 'edit').pack(pady=10)
    
    def delete_purchase(self):
        """Delete selected purchase"""
        selected = self.purchases_tree.selection()
        if not selected:
            show_warning("No Selection", "Please select a purchase to delete")
            return
        
        item = selected[0]
        purchase_id = self.item_to_purchase_id.get(item)
        
        if confirm_action("Confirm Delete", "Are you sure you want to delete this purchase?"):
            try:
                response, status_code = self.api_client.delete_purchase(purchase_id)
                
                if status_code == 200:
                    show_info("Success", "Purchase deleted successfully!")
                    self.refresh_purchases()
                else:
                    show_error("Delete Failed", response.get("msg", "Failed to delete purchase"))
            except Exception as e:
                show_error("Connection Error", str(e))

class AddPurchaseTab:
    """Handles adding new purchases"""
    
    def __init__(self, parent, api_client: APIClient, on_purchase_added):
        self.parent = parent
        self.api_client = api_client
        self.on_purchase_added = on_purchase_added
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        container = tk.Frame(self.frame)
        container.pack(pady=20, padx=20)
        
        create_label(container, "Add New Purchase", 'header').pack(pady=10)
        
        # Form fields
        self.date_label, self.date_entry = WidgetHelper.create_form_field(
            container, "Purchase Date (YYYY-MM-DD):", width=30
        )
        self.date_entry.insert(0, get_current_date())
        
        self.btc_label, self.btc_amount_entry = WidgetHelper.create_form_field(
            container, "BTC Amount:", width=30
        )
        
        # Currency selection
        self.currency_var = tk.StringVar(value="USD")
        WidgetHelper.create_radio_group(
            container, "Currency:", ["USD", "CAD"], self.currency_var
        )
        
        self.cost_label, self.cost_entry = WidgetHelper.create_form_field(
            container, "Cost:", width=30
        )
        
        self.notes_label, self.notes_entry = WidgetHelper.create_form_field(
            container, "Notes (optional):", entry_type='textarea', width=40, height=4
        )
        
        create_button(container, "Add Purchase", self.add_purchase, 'add').pack(pady=10)
    
    def add_purchase(self):
        """Add new purchase"""
        try:
            # Validate form
            validation = FormValidator.validate_purchase_form(
                self.date_entry.get(),
                self.btc_amount_entry.get(),
                self.cost_entry.get()
            )
            
            if not validation['is_valid']:
                show_error("Validation Error", "\n".join(validation['errors']))
                return
            
            # Get form data
            purchase_date = self.date_entry.get()
            btc_amount = validate_float(self.btc_amount_entry.get(), "BTC amount")
            cost = validate_float(self.cost_entry.get(), "Cost")
            currency = self.currency_var.get()
            notes = self.notes_entry.get("1.0", tk.END).strip()
            
            # Convert currency
            if currency == "USD":
                cost_usd = cost
                cost_cad = cost * 1.35
            else:  # CAD
                cost_cad = cost
                cost_usd = cost / 1.35
            
            data = {
                "purchase_date": purchase_date,
                "btc_amount": btc_amount,
                "cost_usd": cost_usd,
                "cost_cad": cost_cad,
                "notes": notes
            }
            
            response, status_code = self.api_client.add_purchase(data)
            
            if status_code == 201:
                show_info("Success", f"Purchase added successfully!\nCost: {cost:.2f} {currency}")
                self.clear_form()
                self.on_purchase_added()
            else:
                show_error("Add Failed", response.get("msg", "Failed to add purchase"))
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

class CSVImportTab:
    """Handles CSV import functionality"""
    
    def __init__(self, parent, api_client: APIClient, on_import_complete):
        self.parent = parent
        self.api_client = api_client
        self.on_import_complete = on_import_complete
        self.frame = ttk.Frame(parent)
        self.csv_data = None
        self.column_mappings = {}
        self.setup_ui()
    
    def setup_ui(self):
        container = tk.Frame(self.frame)
        container.pack(pady=20, padx=20, fill="both", expand=True)
        
        create_label(container, "Import CSV File", 'header').pack(pady=10)
        
        # Step 1: File selection
        self.setup_file_selection(container)
        
        # Step 2: Column mapping
        self.setup_column_mapping(container)
        
        # Step 3: Preview and import
        self.setup_preview_section(container)
    
    def setup_file_selection(self, parent):
        """Setup file selection section"""
        step1_frame = tk.LabelFrame(parent, text="Step 1: Select CSV File", font=("Arial", 10, "bold"))
        step1_frame.pack(fill="x", pady=10, padx=10)
        
        self.file_path_var = tk.StringVar()
        create_label(step1_frame, "Selected file:").pack(anchor="w", padx=10, pady=5)
        
        self.file_path_label = tk.Label(step1_frame, textvariable=self.file_path_var, fg="gray")
        self.file_path_label.pack(anchor="w", padx=10)
        
        create_button(step1_frame, "Browse CSV File", self.browse_csv_file, 'primary').pack(pady=10)
    
    def setup_column_mapping(self, parent):
        """Setup column mapping section"""
        step2_frame = tk.LabelFrame(parent, text="Step 2: Map CSV Columns", font=("Arial", 10, "bold"))
        step2_frame.pack(fill="x", pady=10, padx=10)
        
        self.mapping_frame = tk.Frame(step2_frame)
        self.mapping_frame.pack(padx=10, pady=10)
    
    def setup_preview_section(self, parent):
        """Setup preview and import section"""
        step3_frame = tk.LabelFrame(parent, text="Step 3: Preview and Import", font=("Arial", 10, "bold"))
        step3_frame.pack(fill="both", expand=True, pady=10, padx=10)
        
        self.preview_frame = tk.Frame(step3_frame)
        self.preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        button_frame = tk.Frame(step3_frame)
        button_frame.pack(pady=10)
        
        create_button(button_frame, "Preview Data", self.preview_csv_data, 'warning').pack(side="left", padx=5)
        create_button(button_frame, "Import All", self.import_csv_data, 'success').pack(side="left", padx=5)
    
    def browse_csv_file(self):
        """Open file dialog to select CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.load_csv_file(file_path)
    
    def load_csv_file(self, file_path: str):
        """Load and analyze CSV file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sample = file.read(1024)
                file.seek(0)
                
                # Detect delimiter
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                # Read CSV data
                reader = csv.DictReader(file, delimiter=delimiter)
                self.csv_data = list(reader)
                
                if self.csv_data:
                    self.setup_column_mapping_ui(list(self.csv_data[0].keys()))
                    show_info("Success", f"CSV loaded successfully!\n{len(self.csv_data)} rows found.")
                else:
                    show_error("Empty File", "CSV file appears to be empty.")
                    
        except Exception as e:
            show_error("Load Error", f"Failed to load CSV file:\n{str(e)}")
            self.csv_data = None
    
    def setup_column_mapping_ui(self, csv_columns: List[str]):
        """Setup column mapping interface"""
        clear_frame(self.mapping_frame)
        
        required_fields = {
            "Date": "Purchase date (YYYY-MM-DD format)",
            "BTC Amount": "Amount of Bitcoin purchased",
            "Cost": "Cost of purchase in any currency",
            "Currency": "Currency used (USD, CAD, etc.)",
            "Notes": "Additional notes (optional)"
        }
        
        self.column_mappings = {}
        
        create_label(self.mapping_frame, "Map your CSV columns to required fields:", 'label').grid(
            row=0, column=0, columnspan=3, pady=10
        )
        
        for row, (field, description) in enumerate(required_fields.items(), 1):
            tk.Label(self.mapping_frame, text=f"{field}:", width=15, anchor="w").grid(
                row=row, column=0, sticky="w", padx=5, pady=2
            )
            
            mapping_var = tk.StringVar()
            mapping_dropdown = ttk.Combobox(
                self.mapping_frame, textvariable=mapping_var, width=20, state="readonly"
            )
            mapping_dropdown['values'] = ['-- Select Column --'] + csv_columns
            mapping_dropdown.set('-- Select Column --')
            mapping_dropdown.grid(row=row, column=1, padx=5, pady=2)
            
            self.column_mappings[field] = mapping_var
            
            tk.Label(self.mapping_frame, text=description, fg="gray", font=("Arial", 8)).grid(
                row=row, column=2, sticky="w", padx=5, pady=2
            )
    
    def preview_csv_data(self):
        """Preview the mapped CSV data"""
        if not self.csv_data:
            show_error("No Data", "Please select a CSV file first.")
            return
        
        # Check required mappings
        required_mappings = ["Date", "BTC Amount", "Cost"]
        missing_mappings = [
            field for field in required_mappings 
            if field not in self.column_mappings or self.column_mappings[field].get() == '-- Select Column --'
        ]
        
        if missing_mappings:
            show_error("Missing Mappings", f"Please map the following required fields:\n{', '.join(missing_mappings)}")
            return
        
        self.display_preview()
    
    def display_preview(self):
        """Display preview of CSV data"""
        clear_frame(self.preview_frame)
        
        preview_container = tk.Frame(self.preview_frame)
        preview_container.pack(fill="both", expand=True)
        
        create_label(preview_container, "Preview (first 10 rows):", 'label').pack(anchor="w")
        
        # Create preview table
        columns = ("Date", "BTC Amount", "Cost", "Currency", "Notes")
        preview_tree = ttk.Treeview(preview_container, columns=columns, show="headings", height=10)
        
        for col in columns:
            preview_tree.heading(col, text=col)
            preview_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(preview_container, orient="vertical", command=preview_tree.yview)
        preview_tree.configure(yscrollcommand=scrollbar.set)
        
        preview_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Process and display data
        for row in self.csv_data[:10]:
            try:
                date = row.get(self.column_mappings["Date"].get(), "")
                btc_amount = row.get(self.column_mappings["BTC Amount"].get(), "")
                cost = row.get(self.column_mappings["Cost"].get(), "")
                currency = row.get(self.column_mappings["Currency"].get(), "USD") if self.column_mappings["Currency"].get() != '-- Select Column --' else "USD"
                notes = row.get(self.column_mappings["Notes"].get(), "") if self.column_mappings["Notes"].get() != '-- Select Column --' else ""
                
                preview_tree.insert("", "end", values=(date, btc_amount, cost, currency, notes))
            except Exception:
                continue
    
    def import_csv_data(self):
        """Import CSV data into database"""
        if not self.csv_data:
            show_error("No Data", "Please select a CSV file first.")
            return
        
        # Check required mappings
        required_mappings = ["Date", "BTC Amount", "Cost"]
        missing_mappings = [
            field for field in required_mappings 
            if field not in self.column_mappings or self.column_mappings[field].get() == '-- Select Column --'
        ]
        
        if missing_mappings:
            show_error("Missing Mappings", f"Please map the following required fields:\n{', '.join(missing_mappings)}")
            return
        
        if not confirm_action("Confirm Import", f"Import {len(self.csv_data)} transactions?\nThis action cannot be undone."):
            return
        
        self.process_import()
    
    def process_import(self):
        """Process the CSV import"""
        successful_imports = 0
        failed_imports = 0
        error_details = []
        
        for i, row in enumerate(self.csv_data):
            try:
                # Extract and validate data
                date = row.get(self.column_mappings["Date"].get(), "").strip()
                btc_amount_str = row.get(self.column_mappings["BTC Amount"].get(), "").strip()
                cost_str = row.get(self.column_mappings["Cost"].get(), "").strip()
                currency = row.get(self.column_mappings["Currency"].get(), "USD").strip() if self.column_mappings["Currency"].get() != '-- Select Column --' else "USD"
                notes = row.get(self.column_mappings["Notes"].get(), "").strip() if self.column_mappings["Notes"].get() != '-- Select Column --' else ""
                
                if not date or not btc_amount_str or not cost_str:
                    raise ValueError("Missing required data")
                
                btc_amount = validate_float(btc_amount_str, "BTC amount")
                cost = validate_float(cost_str, "Cost")
                
                # Convert currency
                cost_usd = CurrencyConverter.convert_to_usd(cost, currency.upper())
                cost_cad = cost_usd * 1.35
                
                data = {
                    "purchase_date": date,
                    "btc_amount": btc_amount,
                    "cost_usd": cost_usd,
                    "cost_cad": cost_cad,
                    "notes": f"{notes} (Imported from CSV)" if notes else "Imported from CSV"
                }
                
                response, status_code = self.api_client.add_purchase(data)
                
                if status_code == 201:
                    successful_imports += 1
                else:
                    failed_imports += 1
                    error_details.append(f"Row {i+1}: API error - {response.get('msg', 'Unknown error')}")
                    
            except ValueError as e:
                failed_imports += 1
                error_details.append(f"Row {i+1}: Data error - {str(e)}")
            except Exception as e:
                failed_imports += 1
                error_details.append(f"Row {i+1}: {str(e)}")
        
        self.show_import_results(successful_imports, failed_imports, error_details)
    
    def show_import_results(self, successful: int, failed: int, errors: List[str]):
        """Show import results"""
        result_message = f"Import completed!\n\nSuccessful: {successful}\nFailed: {failed}"
        
        if failed > 0 and len(errors) <= 10:
            result_message += f"\n\nErrors:\n" + "\n".join(errors[:10])
        elif failed > 10:
            result_message += f"\n\nFirst 10 errors:\n" + "\n".join(errors[:10])
        
        if successful > 0:
            show_info("Import Complete", result_message)
            self.on_import_complete()
        else:
            show_error("Import Failed", result_message)

class BTCApp:
    """Main application class - cleaner and more organized"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("BTC Portfolio Tracker")
        self.root.geometry("800x600")
        
        # Initialize API client
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
        
        # Portfolio tab
        self.portfolio_tab = PortfolioTab(self.notebook, self.api_client, self.logout)
        self.notebook.add(self.portfolio_tab.frame, text="Portfolio Summary")
        
        # Purchases tab
        self.purchases_tab = PurchasesTab(self.notebook, self.api_client)
        self.notebook.add(self.purchases_tab.frame, text="All Purchases")
        
        # Add purchase tab
        self.add_purchase_tab = AddPurchaseTab(self.notebook, self.api_client, self.on_purchase_added)
        self.notebook.add(self.add_purchase_tab.frame, text="Add Purchase")
        
        # CSV import tab
        self.csv_import_tab = CSVImportTab(self.notebook, self.api_client, self.on_import_complete)
        self.notebook.add(self.csv_import_tab.frame, text="Import CSV")
    
    def on_login_success(self, username: str):
        """Handle successful login"""
        self.show_main_app()
        self.portfolio_tab.refresh_portfolio()
        self.purchases_tab.refresh_purchases()
        show_info("Welcome", f"Welcome, {username}!")
    
    def on_purchase_added(self):
        """Handle purchase addition"""
        self.portfolio_tab.refresh_portfolio()
        self.purchases_tab.refresh_purchases()
    
    def on_import_complete(self):
        """Handle import completion"""
        self.portfolio_tab.refresh_portfolio()
        self.purchases_tab.refresh_purchases()
    
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
