import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import requests

API_URL = "http://localhost:5000"

class BTCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BTC Portfolio Tracker")
        self.root.geometry("800x600")
        self.token = None
        self.purchases = []
        self.item_to_purchase_id = {}  # Map tree items to purchase IDs

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        
        # Login Frame
        self.login_frame = tk.Frame(root)
        self.setup_login_frame()
        
        # Main Application Tabs
        self.portfolio_frame = ttk.Frame(self.notebook)
        self.purchases_frame = ttk.Frame(self.notebook)
        self.add_purchase_frame = ttk.Frame(self.notebook)
        self.import_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.portfolio_frame, text="Portfolio Summary")
        self.notebook.add(self.purchases_frame, text="All Purchases")
        self.notebook.add(self.add_purchase_frame, text="Add Purchase")
        self.notebook.add(self.import_frame, text="Import CSV")
        
        self.setup_portfolio_frame()
        self.setup_purchases_frame()
        self.setup_add_purchase_frame()
        self.setup_import_frame()
        
        # Show login first
        self.login_frame.pack(pady=50)

    def setup_login_frame(self):
        # Login form
        login_container = tk.Frame(self.login_frame)
        login_container.pack()
        
        tk.Label(login_container, text="BTC Portfolio Tracker", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(login_container, text="Username:").pack()
        self.username_entry = tk.Entry(login_container, width=30)
        self.username_entry.pack(pady=5)
        
        tk.Label(login_container, text="Password:").pack()
        self.password_entry = tk.Entry(login_container, show="*", width=30)
        self.password_entry.pack(pady=5)
        
        login_btn = tk.Button(login_container, text="Login", command=self.login, bg="green", fg="white")
        login_btn.pack(pady=10)
        
        register_btn = tk.Button(login_container, text="Register New User", command=self.show_register)
        register_btn.pack()

    def setup_portfolio_frame(self):
        # Portfolio summary
        summary_container = tk.Frame(self.portfolio_frame)
        summary_container.pack(pady=20, padx=20, fill="both", expand=True)
        
        tk.Label(summary_container, text="Portfolio Summary", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Currency filter for portfolio
        portfolio_filter_frame = tk.Frame(summary_container)
        portfolio_filter_frame.pack(pady=5)
        
        tk.Label(portfolio_filter_frame, text="Show values in:").pack(side="left", padx=5)
        self.portfolio_currency_filter = ttk.Combobox(portfolio_filter_frame, width=15, state="readonly")
        self.portfolio_currency_filter['values'] = ('USD', 'CAD', 'Swiss Franc', 'Ounces of Gold')
        self.portfolio_currency_filter.set('USD')  # Default to USD
        self.portfolio_currency_filter.pack(side="left", padx=5)
        self.portfolio_currency_filter.bind('<<ComboboxSelected>>', self.on_portfolio_currency_change)
        
        self.summary_label = tk.Label(summary_container, text="", justify="left", font=("Arial", 10))
        self.summary_label.pack(pady=10)
        
        refresh_btn = tk.Button(summary_container, text="Refresh Portfolio", command=self.get_portfolio, bg="blue", fg="white")
        refresh_btn.pack(pady=5)
        
        logout_btn = tk.Button(summary_container, text="Logout", command=self.logout, bg="red", fg="white")
        logout_btn.pack(pady=5)

    def setup_purchases_frame(self):
        # Purchases list
        list_container = tk.Frame(self.purchases_frame)
        list_container.pack(pady=20, padx=20, fill="both", expand=True)
        
        tk.Label(list_container, text="All Purchases", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Currency filter
        filter_frame = tk.Frame(list_container)
        filter_frame.pack(pady=5)
        
        tk.Label(filter_frame, text="Show cost in:").pack(side="left", padx=5)
        self.currency_filter = ttk.Combobox(filter_frame, width=15, state="readonly")
        self.currency_filter['values'] = ('USD', 'CAD', 'Swiss Franc', 'Ounces of Gold')
        self.currency_filter.set('USD')  # Default to USD
        self.currency_filter.pack(side="left", padx=5)
        self.currency_filter.bind('<<ComboboxSelected>>', self.on_currency_filter_change)
        
        # Treeview for purchases
        columns = ("Date", "BTC Amount", "Cost", "Notes")
        self.purchases_tree = ttk.Treeview(list_container, columns=columns, show="headings", height=15)
        
        # Set column widths
        self.purchases_tree.column("Date", width=100)
        self.purchases_tree.column("BTC Amount", width=120)
        self.purchases_tree.column("Cost", width=120)
        self.purchases_tree.column("Notes", width=200)
        
        for col in columns:
            self.purchases_tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.purchases_tree.yview)
        self.purchases_tree.configure(yscrollcommand=scrollbar.set)
        
        self.purchases_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons - stack vertically
        btn_frame = tk.Frame(list_container)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Refresh List", command=self.load_purchases, bg="blue", fg="white").pack(pady=2)
        tk.Button(btn_frame, text="Edit Selected", command=self.edit_purchase, bg="orange", fg="white").pack(pady=2)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_purchase, bg="red", fg="white").pack(pady=2)

    def setup_add_purchase_frame(self):
        # Add purchase form
        form_container = tk.Frame(self.add_purchase_frame)
        form_container.pack(pady=20, padx=20)
        
        tk.Label(form_container, text="Add New Purchase", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Form fields
        tk.Label(form_container, text="Purchase Date (YYYY-MM-DD):").pack()
        self.date_entry = tk.Entry(form_container, width=30)
        self.date_entry.pack(pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(form_container, text="BTC Amount:").pack()
        self.btc_amount_entry = tk.Entry(form_container, width=30)
        self.btc_amount_entry.pack(pady=5)
        
        tk.Label(form_container, text="Currency:").pack()
        self.currency_var = tk.StringVar(value="USD")
        currency_frame = tk.Frame(form_container)
        currency_frame.pack(pady=5)
        tk.Radiobutton(currency_frame, text="USD", variable=self.currency_var, value="USD").pack(side="left", padx=10)
        tk.Radiobutton(currency_frame, text="CAD", variable=self.currency_var, value="CAD").pack(side="left", padx=10)
        
        tk.Label(form_container, text="Cost:").pack()
        self.cost_entry = tk.Entry(form_container, width=30)
        self.cost_entry.pack(pady=5)
        
        tk.Label(form_container, text="Notes (optional):").pack()
        self.notes_entry = tk.Text(form_container, width=40, height=4)
        self.notes_entry.pack(pady=5)
        
        add_btn = tk.Button(form_container, text="Add Purchase", command=self.add_purchase, bg="green", fg="white")
        add_btn.pack(pady=10)

    def setup_import_frame(self):
        # CSV Import wizard
        import_container = tk.Frame(self.import_frame)
        import_container.pack(pady=20, padx=20, fill="both", expand=True)
        
        tk.Label(import_container, text="Import CSV File", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Step 1: File selection
        step1_frame = tk.LabelFrame(import_container, text="Step 1: Select CSV File", font=("Arial", 10, "bold"))
        step1_frame.pack(fill="x", pady=10, padx=10)
        
        self.file_path_var = tk.StringVar()
        tk.Label(step1_frame, text="Selected file:").pack(anchor="w", padx=10, pady=5)
        self.file_path_label = tk.Label(step1_frame, textvariable=self.file_path_var, fg="gray")
        self.file_path_label.pack(anchor="w", padx=10)
        
        tk.Button(step1_frame, text="Browse CSV File", command=self.browse_csv_file, bg="blue", fg="white").pack(pady=10)
        
        # Step 2: Column mapping
        step2_frame = tk.LabelFrame(import_container, text="Step 2: Map CSV Columns", font=("Arial", 10, "bold"))
        step2_frame.pack(fill="x", pady=10, padx=10)
        
        self.mapping_frame = tk.Frame(step2_frame)
        self.mapping_frame.pack(padx=10, pady=10)
        
        # Step 3: Preview and import
        step3_frame = tk.LabelFrame(import_container, text="Step 3: Preview and Import", font=("Arial", 10, "bold"))
        step3_frame.pack(fill="both", expand=True, pady=10, padx=10)
        
        # Preview area
        self.preview_frame = tk.Frame(step3_frame)
        self.preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Import buttons
        button_frame = tk.Frame(step3_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Preview Data", command=self.preview_csv_data, bg="orange", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="Import All", command=self.import_csv_data, bg="green", fg="white").pack(side="left", padx=5)
        
        # Initialize variables
        self.csv_data = None
        self.column_mappings = {}

    def browse_csv_file(self):
        """Open file dialog to select CSV file"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.load_csv_file(file_path)

    def load_csv_file(self, file_path):
        """Load and analyze CSV file"""
        try:
            import csv
            
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read first few rows to detect structure
                sample = file.read(1024)
                file.seek(0)
                
                # Detect delimiter
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                # Read CSV data
                reader = csv.DictReader(file, delimiter=delimiter)
                self.csv_data = list(reader)
                
                if self.csv_data:
                    self.setup_column_mapping(list(self.csv_data[0].keys()))
                    messagebox.showinfo("Success", f"CSV loaded successfully!\n{len(self.csv_data)} rows found.")
                else:
                    messagebox.showerror("Error", "CSV file appears to be empty.")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file:\n{str(e)}")
            self.csv_data = None

    def setup_column_mapping(self, csv_columns):
        """Setup column mapping interface"""
        # Clear existing mapping widgets
        for widget in self.mapping_frame.winfo_children():
            widget.destroy()
        
        # Required fields for our app
        required_fields = {
            "Date": "Purchase date (YYYY-MM-DD format)",
            "BTC Amount": "Amount of Bitcoin purchased",
            "Cost": "Cost of purchase in any currency",
            "Currency": "Currency used (USD, CAD, etc.)",
            "Notes": "Additional notes (optional)"
        }
        
        self.column_mappings = {}
        
        # Create mapping dropdowns
        tk.Label(self.mapping_frame, text="Map your CSV columns to required fields:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, pady=10)
        
        row = 1
        for field, description in required_fields.items():
            tk.Label(self.mapping_frame, text=f"{field}:", width=15, anchor="w").grid(row=row, column=0, sticky="w", padx=5, pady=2)
            
            # Dropdown for column selection
            mapping_var = tk.StringVar()
            mapping_dropdown = ttk.Combobox(self.mapping_frame, textvariable=mapping_var, width=20, state="readonly")
            mapping_dropdown['values'] = ['-- Select Column --'] + csv_columns
            mapping_dropdown.set('-- Select Column --')
            mapping_dropdown.grid(row=row, column=1, padx=5, pady=2)
            
            # Store the mapping variable
            self.column_mappings[field] = mapping_var
            
            # Description
            tk.Label(self.mapping_frame, text=description, fg="gray", font=("Arial", 8)).grid(row=row, column=2, sticky="w", padx=5, pady=2)
            
            row += 1

    def preview_csv_data(self):
        """Preview the mapped CSV data"""
        if not self.csv_data:
            messagebox.showerror("Error", "Please select a CSV file first.")
            return
        
        # Check if required mappings are set
        required_mappings = ["Date", "BTC Amount", "Cost"]
        missing_mappings = []
        
        for field in required_mappings:
            if field not in self.column_mappings or self.column_mappings[field].get() == '-- Select Column --':
                missing_mappings.append(field)
        
        if missing_mappings:
            messagebox.showerror("Error", f"Please map the following required fields:\n{', '.join(missing_mappings)}")
            return
        
        # Clear previous preview
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        # Create preview table
        preview_container = tk.Frame(self.preview_frame)
        preview_container.pack(fill="both", expand=True)
        
        tk.Label(preview_container, text="Preview (first 10 rows):", font=("Arial", 10, "bold")).pack(anchor="w")
        
        # Create treeview for preview
        columns = ("Date", "BTC Amount", "Cost", "Currency", "Notes")
        preview_tree = ttk.Treeview(preview_container, columns=columns, show="headings", height=10)
        
        for col in columns:
            preview_tree.heading(col, text=col)
            preview_tree.column(col, width=120)
        
        scrollbar_preview = ttk.Scrollbar(preview_container, orient="vertical", command=preview_tree.yview)
        preview_tree.configure(yscrollcommand=scrollbar_preview.set)
        
        preview_tree.pack(side="left", fill="both", expand=True)
        scrollbar_preview.pack(side="right", fill="y")
        
        # Process and display preview data
        processed_count = 0
        error_count = 0
        
        for i, row in enumerate(self.csv_data[:10]):  # Preview first 10 rows
            try:
                # Extract mapped values
                date = row.get(self.column_mappings["Date"].get(), "")
                btc_amount = row.get(self.column_mappings["BTC Amount"].get(), "")
                cost = row.get(self.column_mappings["Cost"].get(), "")
                currency = row.get(self.column_mappings["Currency"].get(), "USD") if self.column_mappings["Currency"].get() != '-- Select Column --' else "USD"
                notes = row.get(self.column_mappings["Notes"].get(), "") if self.column_mappings["Notes"].get() != '-- Select Column --' else ""
                
                preview_tree.insert("", "end", values=(date, btc_amount, cost, currency, notes))
                processed_count += 1
                
            except Exception as e:
                error_count += 1
        
        # Show preview summary
        summary_text = f"Preview complete: {processed_count} rows processed"
        if error_count > 0:
            summary_text += f", {error_count} errors"
        
        tk.Label(preview_container, text=summary_text, fg="blue").pack(anchor="w", pady=5)

    def import_csv_data(self):
        """Import the CSV data into the database"""
        if not self.csv_data:
            messagebox.showerror("Error", "Please select a CSV file first.")
            return
        
        # Check if required mappings are set
        required_mappings = ["Date", "BTC Amount", "Cost"]
        missing_mappings = []
        
        for field in required_mappings:
            if field not in self.column_mappings or self.column_mappings[field].get() == '-- Select Column --':
                missing_mappings.append(field)
        
        if missing_mappings:
            messagebox.showerror("Error", f"Please map the following required fields:\n{', '.join(missing_mappings)}")
            return
        
        # Confirm import
        if not messagebox.askyesno("Confirm Import", f"Import {len(self.csv_data)} transactions?\nThis action cannot be undone."):
            return
        
        # Process and import data
        headers = {"Authorization": f"Bearer {self.token}"}
        successful_imports = 0
        failed_imports = 0
        error_details = []
        
        for i, row in enumerate(self.csv_data):
            try:
                # Extract mapped values
                date = row.get(self.column_mappings["Date"].get(), "").strip()
                btc_amount_str = row.get(self.column_mappings["BTC Amount"].get(), "").strip()
                cost_str = row.get(self.column_mappings["Cost"].get(), "").strip()
                currency = row.get(self.column_mappings["Currency"].get(), "USD").strip() if self.column_mappings["Currency"].get() != '-- Select Column --' else "USD"
                notes = row.get(self.column_mappings["Notes"].get(), "").strip() if self.column_mappings["Notes"].get() != '-- Select Column --' else ""
                
                # Validate and convert data
                if not date or not btc_amount_str or not cost_str:
                    raise ValueError("Missing required data")
                
                btc_amount = float(btc_amount_str)
                cost = float(cost_str)
                
                # Convert currency to USD and CAD
                if currency.upper() == "USD":
                    cost_usd = cost
                    cost_cad = cost * 1.35
                elif currency.upper() == "CAD":
                    cost_cad = cost
                    cost_usd = cost / 1.35
                else:
                    # Default to treating as USD
                    cost_usd = cost
                    cost_cad = cost * 1.35
                
                # Prepare data for API
                data = {
                    "purchase_date": date,
                    "btc_amount": btc_amount,
                    "cost_usd": cost_usd,
                    "cost_cad": cost_cad,
                    "notes": f"{notes} (Imported from CSV)" if notes else "Imported from CSV"
                }
                
                # Send to API
                resp = requests.post(f"{API_URL}/purchases", json=data, headers=headers)
                if resp.status_code == 201:
                    successful_imports += 1
                else:
                    failed_imports += 1
                    error_details.append(f"Row {i+1}: API error - {resp.json().get('msg', 'Unknown error')}")
                    
            except ValueError as e:
                failed_imports += 1
                error_details.append(f"Row {i+1}: Data error - {str(e)}")
            except Exception as e:
                failed_imports += 1
                error_details.append(f"Row {i+1}: {str(e)}")
        
        # Show import results
        result_message = f"Import completed!\n\nSuccessful: {successful_imports}\nFailed: {failed_imports}"
        
        if failed_imports > 0 and len(error_details) <= 10:
            result_message += f"\n\nErrors:\n" + "\n".join(error_details[:10])
        elif failed_imports > 10:
            result_message += f"\n\nFirst 10 errors:\n" + "\n".join(error_details[:10])
        
        if successful_imports > 0:
            messagebox.showinfo("Import Complete", result_message)
            # Refresh the portfolio and purchases
            self.get_portfolio()
            self.load_purchases()
        else:
            messagebox.showerror("Import Failed", result_message)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        try:
            data = {"username": username, "password": password}
            resp = requests.post(f"{API_URL}/login", json=data)
            
            if resp.status_code == 200:
                self.token = resp.json()["access_token"]
                self.login_frame.pack_forget()
                self.notebook.pack(fill="both", expand=True)
                self.get_portfolio()
                self.load_purchases()
                messagebox.showinfo("Success", f"Welcome, {username}!")
            else:
                messagebox.showerror("Error", resp.json().get("msg", "Login failed"))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}\nMake sure the backend server is running!")

    def show_register(self):
        # Create registration window
        register_window = tk.Toplevel(self.root)
        register_window.title("Register New User")
        register_window.geometry("300x250")
        register_window.resizable(False, False)
        
        tk.Label(register_window, text="Register New User", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(register_window, text="Username:").pack()
        username_entry = tk.Entry(register_window, width=30)
        username_entry.pack(pady=5)
        
        tk.Label(register_window, text="Password:").pack()
        password_entry = tk.Entry(register_window, show="*", width=30)
        password_entry.pack(pady=5)
        
        tk.Label(register_window, text="Confirm Password:").pack()
        confirm_password_entry = tk.Entry(register_window, show="*", width=30)
        confirm_password_entry.pack(pady=5)
        
        def register_user():
            username = username_entry.get()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()
            
            if not username or not password or not confirm_password:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match")
                return
            
            try:
                data = {"username": username, "password": password}
                resp = requests.post(f"{API_URL}/register", json=data)
                
                if resp.status_code == 201:
                    messagebox.showinfo("Success", "User registered successfully! You can now log in.")
                    register_window.destroy()
                    self.username_entry.delete(0, tk.END)
                    self.username_entry.insert(0, username)
                else:
                    messagebox.showerror("Error", resp.json().get("msg", "Registration failed"))
            except Exception as e:
                messagebox.showerror("Error", f"Connection error: {str(e)}\nMake sure the backend server is running!")
        
        tk.Button(register_window, text="Register", command=register_user, bg="blue", fg="white").pack(pady=10)

    def get_portfolio(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            resp = requests.get(f"{API_URL}/portfolio/summary", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                
                # Get selected currency for portfolio display
                selected_currency = getattr(self, 'portfolio_currency_filter', None)
                if selected_currency:
                    currency = selected_currency.get()
                else:
                    currency = 'USD'  # Default if filter not yet created
                
                # Convert values to selected currency
                cost_basis_display = self.convert_currency(data['cost_basis_usd'], currency)
                current_value_display = self.convert_currency(data['current_value_usd'], currency) if data['current_value_usd'] else "N/A"
                btc_price_display = self.convert_currency(data['btc_price_usd'], currency) if data['btc_price_usd'] else "N/A"
                
                # Calculate profit/loss in selected currency
                if data['current_value_usd'] and data['cost_basis_usd']:
                    profit_loss_usd = data['current_value_usd'] - data['cost_basis_usd']
                    profit_loss_display = self.convert_currency(profit_loss_usd, currency)
                    profit_loss_percent = ((data['current_value_usd'] - data['cost_basis_usd']) / data['cost_basis_usd']) * 100
                    profit_loss_text = f"Profit/Loss: {profit_loss_display} ({profit_loss_percent:+.2f}%)"
                else:
                    profit_loss_text = "Profit/Loss: N/A"
                
                summary = (
                    f"Total BTC: {data['total_btc']:.8f}\n"
                    f"Cost Basis: {cost_basis_display}\n"
                    f"Current Value: {current_value_display}\n"
                    f"BTC Price: {btc_price_display}\n"
                    f"{profit_loss_text}\n"
                )
                self.summary_label.config(text=summary)
            else:
                messagebox.showerror("Error", resp.json().get("msg", "Failed to fetch portfolio"))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def convert_currency(self, usd_amount, target_currency):
        """Convert USD amount to target currency"""
        # Simple conversion rates - in a real app, you'd fetch these from an API
        conversion_rates = {
            'USD': 1.0,
            'CAD': 1.35,
            'Swiss Franc': 0.92,
            'Ounces of Gold': 0.0005  # Approximate: $2000 per ounce of gold
        }
        
        if target_currency in conversion_rates:
            converted_amount = usd_amount * conversion_rates[target_currency]
            
            # Format based on currency type
            if target_currency == 'Ounces of Gold':
                return f"{converted_amount:.6f} oz Au"
            elif target_currency == 'Swiss Franc':
                return f"{converted_amount:.2f} CHF"
            elif target_currency == 'CAD':
                return f"${converted_amount:.2f} CAD"
            else:  # USD
                return f"${converted_amount:.2f} USD"
        else:
            return f"${usd_amount:.2f} USD"  # Fallback to USD

    def on_currency_filter_change(self, event=None):
        """Handle currency filter change"""
        self.load_purchases()

    def on_portfolio_currency_change(self, event=None):
        """Handle portfolio currency filter change"""
        self.get_portfolio()

    def load_purchases(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            resp = requests.get(f"{API_URL}/purchases", headers=headers)
            if resp.status_code == 200:
                self.purchases = resp.json()
                # Clear existing items
                for item in self.purchases_tree.get_children():
                    self.purchases_tree.delete(item)
                
                # Create a mapping from tree items to purchase IDs
                self.item_to_purchase_id = {}
                
                # Get selected currency filter
                selected_currency = getattr(self, 'currency_filter', None)
                if selected_currency:
                    currency = selected_currency.get()
                else:
                    currency = 'USD'  # Default if filter not yet created
                
                # Add purchases to tree
                for purchase in self.purchases:
                    # Convert cost to selected currency
                    cost_display = self.convert_currency(purchase["cost_usd"], currency)
                    
                    item = self.purchases_tree.insert("", "end", values=(
                        purchase["purchase_date"],
                        f"{purchase['btc_amount']:.8f}",
                        cost_display,
                        purchase["notes"]
                    ))
                    # Store the purchase ID in our mapping
                    self.item_to_purchase_id[item] = purchase["id"]
            else:
                messagebox.showerror("Error", resp.json().get("msg", "Failed to load purchases"))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def add_purchase(self):
        try:
            purchase_date = self.date_entry.get()
            btc_amount = float(self.btc_amount_entry.get())
            cost = float(self.cost_entry.get())
            currency = self.currency_var.get()
            notes = self.notes_entry.get("1.0", tk.END).strip()
            
            # Convert currency if needed
            if currency == "USD":
                cost_usd = cost
                # Simple conversion rate - you could fetch real rates from an API
                cost_cad = cost * 1.35  # Approximate USD to CAD conversion
            else:  # CAD
                cost_cad = cost
                # Simple conversion rate - you could fetch real rates from an API
                cost_usd = cost / 1.35  # Approximate CAD to USD conversion
            
            headers = {"Authorization": f"Bearer {self.token}"}
            data = {
                "purchase_date": purchase_date,
                "btc_amount": btc_amount,
                "cost_usd": cost_usd,
                "cost_cad": cost_cad,
                "notes": notes
            }
            
            resp = requests.post(f"{API_URL}/purchases", json=data, headers=headers)
            if resp.status_code == 201:
                messagebox.showinfo("Success", f"Purchase added successfully!\nCost: {cost:.2f} {currency}\nConverted: {cost_usd:.2f} USD / {cost_cad:.2f} CAD")
                # Clear form
                self.btc_amount_entry.delete(0, tk.END)
                self.cost_entry.delete(0, tk.END)
                self.notes_entry.delete("1.0", tk.END)
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
                # Refresh data
                self.get_portfolio()
                self.load_purchases()
            else:
                messagebox.showerror("Error", resp.json().get("msg", "Failed to add purchase"))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for BTC amount and cost")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def edit_purchase(self):
        selected = self.purchases_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a purchase to edit")
            return
        
        item = selected[0]
        purchase_id = self.item_to_purchase_id.get(item)
        
        # Find the purchase data
        purchase_data = None
        for purchase in self.purchases:
            if purchase["id"] == purchase_id:
                purchase_data = purchase
                break
        
        if not purchase_data:
            messagebox.showerror("Error", "Purchase not found")
            return
        
        # Edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Purchase")
        edit_window.geometry("400x300")
        
        tk.Label(edit_window, text="Edit Purchase", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Form fields with current values
        tk.Label(edit_window, text="Purchase Date (YYYY-MM-DD):").pack()
        date_entry = tk.Entry(edit_window, width=30)
        date_entry.pack(pady=5)
        date_entry.insert(0, purchase_data["purchase_date"])
        
        tk.Label(edit_window, text="BTC Amount:").pack()
        btc_entry = tk.Entry(edit_window, width=30)
        btc_entry.pack(pady=5)
        btc_entry.insert(0, str(purchase_data["btc_amount"]))
        
        tk.Label(edit_window, text="Cost USD:").pack()
        usd_entry = tk.Entry(edit_window, width=30)
        usd_entry.pack(pady=5)
        usd_entry.insert(0, str(purchase_data["cost_usd"]))
        
        tk.Label(edit_window, text="Cost CAD:").pack()
        cad_entry = tk.Entry(edit_window, width=30)
        cad_entry.pack(pady=5)
        cad_entry.insert(0, str(purchase_data["cost_cad"]))
        
        tk.Label(edit_window, text="Notes:").pack()
        notes_entry = tk.Text(edit_window, width=40, height=4)
        notes_entry.pack(pady=5)
        notes_entry.insert("1.0", purchase_data["notes"])
        
        def update_purchase():
            try:
                headers = {"Authorization": f"Bearer {self.token}"}
                data = {
                    "purchase_date": date_entry.get(),
                    "btc_amount": float(btc_entry.get()),
                    "cost_usd": float(usd_entry.get()),
                    "cost_cad": float(cad_entry.get()),
                    "notes": notes_entry.get("1.0", tk.END).strip()
                }
                
                resp = requests.put(f"{API_URL}/purchases/{purchase_id}", json=data, headers=headers)
                if resp.status_code == 200:
                    messagebox.showinfo("Success", "Purchase updated successfully!")
                    edit_window.destroy()
                    self.get_portfolio()
                    self.load_purchases()
                else:
                    messagebox.showerror("Error", resp.json().get("msg", "Failed to update purchase"))
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for BTC amount and costs")
            except Exception as e:
                messagebox.showerror("Error", f"Connection error: {str(e)}")
        
        tk.Button(edit_window, text="Update Purchase", command=update_purchase, bg="orange", fg="white").pack(pady=10)

    def delete_purchase(self):
        selected = self.purchases_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a purchase to delete")
            return
        
        item = selected[0]
        purchase_id = self.item_to_purchase_id.get(item)
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this purchase?"):
            try:
                headers = {"Authorization": f"Bearer {self.token}"}
                resp = requests.delete(f"{API_URL}/purchases/{purchase_id}", headers=headers)
                if resp.status_code == 200:
                    messagebox.showinfo("Success", "Purchase deleted successfully!")
                    self.get_portfolio()
                    self.load_purchases()
                else:
                    messagebox.showerror("Error", resp.json().get("msg", "Failed to delete purchase"))
            except Exception as e:
                messagebox.showerror("Error", f"Connection error: {str(e)}")

    def logout(self):
        self.token = None
        self.notebook.pack_forget()
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.login_frame.pack(pady=50)

if __name__ == "__main__":
    root = tk.Tk()
    app = BTCApp(root)
    root.mainloop()
