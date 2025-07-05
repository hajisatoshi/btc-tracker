"""
Configuration file for BTC Portfolio Tracker
"""

# API Configuration
API_BASE_URL = "http://localhost:5000"

# Currency Configuration
CURRENCIES = {
    'USD': {
        'symbol': '$',
        'rate': 1.0,
        'precision': 2
    },
    'CAD': {
        'symbol': '$',
        'rate': 1.35,
        'precision': 2
    },
    'Swiss Franc': {
        'symbol': 'CHF',
        'rate': 0.92,
        'precision': 2
    },
    'Ounces of Gold': {
        'symbol': 'oz Au',
        'rate': 0.0005,
        'precision': 6
    }
}

# UI Configuration
WINDOW_SIZE = "800x600"
FONT_HEADER = ("Arial", 14, "bold")
FONT_LABEL = ("Arial", 10, "bold")
FONT_NORMAL = ("Arial", 10)
FONT_SMALL = ("Arial", 8)

# Colors
COLORS = {
    'primary': '#007bff',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Button colors
BUTTON_COLORS = {
    'login': {'bg': COLORS['success'], 'fg': 'white'},
    'register': {'bg': COLORS['primary'], 'fg': 'white'},
    'add': {'bg': COLORS['success'], 'fg': 'white'},
    'edit': {'bg': COLORS['warning'], 'fg': 'white'},
    'delete': {'bg': COLORS['danger'], 'fg': 'white'},
    'refresh': {'bg': COLORS['primary'], 'fg': 'white'},
    'logout': {'bg': COLORS['danger'], 'fg': 'white'},
    'import': {'bg': COLORS['info'], 'fg': 'white'}
}

# Table Configuration
TABLE_COLUMNS = {
    'purchases': [
        {'name': 'Date', 'width': 100},
        {'name': 'BTC Amount', 'width': 120},
        {'name': 'Cost', 'width': 120},
        {'name': 'Notes', 'width': 200}
    ],
    'preview': [
        {'name': 'Date', 'width': 120},
        {'name': 'BTC Amount', 'width': 120},
        {'name': 'Cost', 'width': 120},
        {'name': 'Currency', 'width': 120},
        {'name': 'Notes', 'width': 120}
    ]
}

# CSV Import Configuration
CSV_REQUIRED_FIELDS = ["Date", "BTC Amount", "Cost"]
CSV_OPTIONAL_FIELDS = ["Currency", "Notes"]
CSV_FIELD_DESCRIPTIONS = {
    "Date": "Purchase date (YYYY-MM-DD format)",
    "BTC Amount": "Amount of Bitcoin purchased",
    "Cost": "Cost of purchase in any currency",
    "Currency": "Currency used (USD, CAD, etc.)",
    "Notes": "Additional notes (optional)"
}

# Default values
DEFAULT_CURRENCY = "USD"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
PREVIEW_ROWS_LIMIT = 10
