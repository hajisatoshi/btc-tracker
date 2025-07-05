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

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        
        # Login Frame
        self.login_frame = tk.Frame(root)
        self.setup_login_frame()
        
        # Main Application Tabs
        self.portfolio_frame = ttk.Frame(self.notebook)
        self.purchases_frame = ttk.Frame(self.notebook)
        self.add_purchase_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.portfolio_frame, text="Portfolio Summary")
        self.notebook.add(self.purchases_frame, text="All Purchases")
        self.notebook.add(self.add_purchase_frame, text="Add Purchase")
        
        self.setup_portfolio_frame()
        self.setup_purchases_frame()
        self.setup_add_purchase_frame()
        
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
        
        # Treeview for purchases
        columns = ("ID", "Date", "BTC Amount", "Cost USD", "Cost CAD", "Notes")
        self.purchases_tree = ttk.Treeview(list_container, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.purchases_tree.heading(col, text=col)
            self.purchases_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.purchases_tree.yview)
        self.purchases_tree.configure(yscrollcommand=scrollbar.set)
        
        self.purchases_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        btn_frame = tk.Frame(list_container)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Refresh List", command=self.load_purchases, bg="blue", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Edit Selected", command=self.edit_purchase, bg="orange", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_purchase, bg="red", fg="white").pack(side="left", padx=5)

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
        
        tk.Label(form_container, text="Cost USD:").pack()
        self.cost_usd_entry = tk.Entry(form_container, width=30)
        self.cost_usd_entry.pack(pady=5)
        
        tk.Label(form_container, text="Cost CAD:").pack()
        self.cost_cad_entry = tk.Entry(form_container, width=30)
        self.cost_cad_entry.pack(pady=5)
        
        tk.Label(form_container, text="Notes (optional):").pack()
        self.notes_entry = tk.Text(form_container, width=40, height=4)
        self.notes_entry.pack(pady=5)
        
        add_btn = tk.Button(form_container, text="Add Purchase", command=self.add_purchase, bg="green", fg="white")
        add_btn.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        try:
            resp = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
            if resp.status_code == 200:
                self.token = resp.json()["access_token"]
                messagebox.showinfo("Success", "Login successful!")
                self.login_frame.pack_forget()
                self.notebook.pack(fill="both", expand=True)
                self.get_portfolio()
                self.load_purchases()
            else:
                messagebox.showerror("Error", resp.json().get("msg", "Login failed"))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def show_register(self):
        # Simple registration window
        reg_window = tk.Toplevel(self.root)
        reg_window.title("Register New User")
        reg_window.geometry("300x200")
        
        tk.Label(reg_window, text="Username:").pack(pady=5)
        username_entry = tk.Entry(reg_window, width=30)
        username_entry.pack(pady=5)
        
        tk.Label(reg_window, text="Password:").pack(pady=5)
        password_entry = tk.Entry(reg_window, show="*", width=30)
        password_entry.pack(pady=5)
        
        def register():
            username = username_entry.get()
            password = password_entry.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password")
                return
            
            try:
                resp = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
                if resp.status_code == 201:
                    messagebox.showinfo("Success", "User registered successfully!")
                    reg_window.destroy()
                else:
                    messagebox.showerror("Error", resp.json().get("msg", "Registration failed"))
            except Exception as e:
                messagebox.showerror("Error", f"Connection error: {str(e)}")
        
        tk.Button(reg_window, text="Register", command=register, bg="green", fg="white").pack(pady=10)

    def get_portfolio(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            resp = requests.get(f"{API_URL}/portfolio/summary", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                summary = (
                    f"Total BTC: {data['total_btc']:.8f}\n"
                    f"Cost Basis USD: ${data['cost_basis_usd']:.2f}\n"
                    f"Cost Basis CAD: ${data['cost_basis_cad']:.2f}\n"
                    f"Current Value USD: ${data['current_value_usd']:.2f}\n"
                    f"Current Value CAD: ${data['current_value_cad']:.2f}\n"
                    f"BTC Price USD: ${data['btc_price_usd']:.2f}\n"
                    f"BTC Price CAD: ${data['btc_price_cad']:.2f}\n"
                )
                self.summary_label.config(text=summary)
            else:
                messagebox.showerror("Error", resp.json().get("msg", "Failed to fetch portfolio"))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def load_purchases(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            resp = requests.get(f"{API_URL}/purchases", headers=headers)
            if resp.status_code == 200:
                self.purchases = resp.json()
                # Clear existing items
                for item in self.purchases_tree.get_children():
                    self.purchases_tree.delete(item)
                
                # Add purchases to tree
                for purchase in self.purchases:
                    self.purchases_tree.insert("", "end", values=(
                        purchase["id"],
                        purchase["purchase_date"],
                        f"{purchase['btc_amount']:.8f}",
                        f"${purchase['cost_usd']:.2f}",
                        f"${purchase['cost_cad']:.2f}",
                        purchase["notes"]
                    ))
            else:
                messagebox.showerror("Error", resp.json().get("msg", "Failed to load purchases"))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def add_purchase(self):
        try:
            purchase_date = self.date_entry.get()
            btc_amount = float(self.btc_amount_entry.get())
            cost_usd = float(self.cost_usd_entry.get())
            cost_cad = float(self.cost_cad_entry.get())
            notes = self.notes_entry.get("1.0", tk.END).strip()
            
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
                messagebox.showinfo("Success", "Purchase added successfully!")
                # Clear form
                self.btc_amount_entry.delete(0, tk.END)
                self.cost_usd_entry.delete(0, tk.END)
                self.cost_cad_entry.delete(0, tk.END)
                self.notes_entry.delete("1.0", tk.END)
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
                # Refresh data
                self.get_portfolio()
                self.load_purchases()
            else:
                messagebox.showerror("Error", resp.json().get("msg", "Failed to add purchase"))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for BTC amount and costs")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def edit_purchase(self):
        selected = self.purchases_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a purchase to edit")
            return
        
        item = self.purchases_tree.item(selected[0])
        purchase_id = item["values"][0]
        
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
        
        item = self.purchases_tree.item(selected[0])
        purchase_id = item["values"][0]
        
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
