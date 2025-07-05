"""
Utility functions for BTC Portfolio Tracker
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration constants
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
FONT_HEADER = ("Arial", 14, "bold")
FONT_LABEL = ("Arial", 10, "bold")
FONT_NORMAL = ("Arial", 10)
FONT_SMALL = ("Arial", 8)

BUTTON_COLORS = {
    'primary': {'bg': '#007bff', 'fg': 'white'},
    'success': {'bg': '#28a745', 'fg': 'white'},
    'warning': {'bg': '#ffc107', 'fg': 'white'},
    'danger': {'bg': '#dc3545', 'fg': 'white'},
    'info': {'bg': '#17a2b8', 'fg': 'white'},
    'login': {'bg': '#28a745', 'fg': 'white'},
    'register': {'bg': '#007bff', 'fg': 'white'},
    'add': {'bg': '#28a745', 'fg': 'white'},
    'edit': {'bg': '#ffc107', 'fg': 'white'},
    'delete': {'bg': '#dc3545', 'fg': 'white'},
    'refresh': {'bg': '#007bff', 'fg': 'white'},
    'logout': {'bg': '#dc3545', 'fg': 'white'},
    'import': {'bg': '#17a2b8', 'fg': 'white'}
}

CURRENCIES = {
    'USD': {'symbol': '$', 'rate': 1.0, 'precision': 2},
    'CAD': {'symbol': '$', 'rate': 1.35, 'precision': 2},
    'Swiss Franc': {'symbol': 'CHF', 'rate': 0.92, 'precision': 2},
    'Ounces of Gold': {'symbol': 'oz Au', 'rate': 0.0005, 'precision': 6}
}

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
    """Format BTC amount with proper precision"""
    return f"{amount:.8f}"

def format_percentage(percentage: float) -> str:
    """Format percentage with sign"""
    return f"{percentage:+.2f}%"

def create_button(parent, text: str, command: callable, button_type: str = 'primary', **kwargs) -> tk.Button:
    """Create button with consistent styling"""
    colors = BUTTON_COLORS.get(button_type, BUTTON_COLORS['primary'])
    
    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=colors['bg'],
        fg=colors['fg'],
        **kwargs
    )
    return button

def create_label(parent, text: str, font_type: str = 'normal', **kwargs) -> tk.Label:
    """Create label with consistent styling"""
    fonts = {
        'header': FONT_HEADER,
        'label': FONT_LABEL,
        'normal': FONT_NORMAL,
        'small': FONT_SMALL
    }
    
    font = fonts.get(font_type, FONT_NORMAL)
    
    label = tk.Label(
        parent,
        text=text,
        font=font,
        **kwargs
    )
    return label

def clear_frame(frame: tk.Frame):
    """Clear all widgets from a frame"""
    for widget in frame.winfo_children():
        widget.destroy()

def get_current_date() -> str:
    """Get current date in default format"""
    return datetime.now().strftime(DEFAULT_DATE_FORMAT)

def safe_get_dict_value(data: Dict[str, Any], key: str, default: Any = "") -> Any:
    """Safely get value from dictionary"""
    return data.get(key, default)

def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def handle_api_error(response: Dict[str, Any], default_message: str = "An error occurred"):
    """Handle API error response"""
    error_message = response.get("msg", default_message)
    show_error("API Error", error_message)

def format_currency_list() -> tuple:
    """Get formatted currency list for comboboxes"""
    return tuple(CURRENCIES.keys())

def is_valid_email(email: str) -> bool:
    """Basic email validation"""
    return "@" in email and "." in email.split("@")[1]

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    import re
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

class FormValidator:
    """Form validation helper class"""
    
    @staticmethod
    def validate_purchase_form(date: str, btc_amount: str, cost: str) -> Dict[str, Any]:
        """Validate purchase form data"""
        errors = []
        
        # Validate date
        if not date:
            errors.append("Purchase date is required")
        elif not validate_date(date):
            errors.append("Invalid date format. Use YYYY-MM-DD")
        
        # Validate BTC amount
        if not btc_amount:
            errors.append("BTC amount is required")
        else:
            try:
                btc_val = validate_float(btc_amount, "BTC amount")
                if btc_val <= 0:
                    errors.append("BTC amount must be positive")
            except ValueError as e:
                errors.append(str(e))
        
        # Validate cost
        if not cost:
            errors.append("Cost is required")
        else:
            try:
                cost_val = validate_float(cost, "Cost")
                if cost_val <= 0:
                    errors.append("Cost must be positive")
            except ValueError as e:
                errors.append(str(e))
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_login_form(username: str, password: str) -> Dict[str, Any]:
        """Validate login form data"""
        errors = []
        
        if not username:
            errors.append("Username is required")
        
        if not password:
            errors.append("Password is required")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_registration_form(username: str, password: str, confirm_password: str) -> Dict[str, Any]:
        """Validate registration form data"""
        errors = []
        
        if not username:
            errors.append("Username is required")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters")
        
        if not password:
            errors.append("Password is required")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters")
        
        if not confirm_password:
            errors.append("Please confirm your password")
        elif password != confirm_password:
            errors.append("Passwords do not match")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }

class WidgetHelper:
    """Helper class for creating common UI widgets"""
    
    @staticmethod
    def create_form_field(parent, label_text: str, entry_type: str = 'text', **kwargs) -> tuple:
        """Create form field with label and entry"""
        label = create_label(parent, label_text)
        label.pack(pady=(10, 0))
        
        if entry_type == 'text':
            entry = tk.Entry(parent, **kwargs)
        elif entry_type == 'password':
            entry = tk.Entry(parent, show="*", **kwargs)
        elif entry_type == 'textarea':
            entry = tk.Text(parent, **kwargs)
        else:
            entry = tk.Entry(parent, **kwargs)
        
        entry.pack(pady=(0, 5))
        return label, entry
    
    @staticmethod
    def create_radio_group(parent, label_text: str, options: list, variable: tk.StringVar, **kwargs) -> tk.Frame:
        """Create radio button group"""
        create_label(parent, label_text).pack()
        
        radio_frame = tk.Frame(parent)
        radio_frame.pack(pady=5)
        
        for option in options:
            radio = tk.Radiobutton(radio_frame, text=option, variable=variable, value=option, **kwargs)
            radio.pack(side="left", padx=10)
        
        return radio_frame
    
    @staticmethod
    def create_combobox(parent, label_text: str, values: tuple, default: str = "", **kwargs) -> tuple:
        """Create combobox with label"""
        label = create_label(parent, label_text)
        label.pack(anchor="w", padx=5, pady=5)
        
        combobox = tk.ttk.Combobox(parent, values=values, state="readonly", **kwargs)
        if default:
            combobox.set(default)
        combobox.pack(side="left", padx=5)
        
        return label, combobox
