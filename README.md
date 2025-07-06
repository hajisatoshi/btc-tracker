# 🚀 BTC Portfolio Tracker v2.0

> **A comprehensive Bitcoin portfolio tracking application with multi-currency support, savings/spending management, and real-time price monitoring.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/btc-portfolio-tracker)

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Multi-Currency Support](#-multi-currency-support)
- [Screenshots](#-screenshots)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🏦 Portfolio Management
- **Savings Tracking**: Record and monitor your Bitcoin savings/purchases
- **Spending Tracking**: Track Bitcoin expenditures and transactions
- **Net Position**: Real-time calculation of your net Bitcoin holdings
- **Transaction History**: Complete history with filtering and search capabilities

### 💰 Multi-Currency Support
- **USD** (US Dollar) - Primary currency
- **CAD** (Canadian Dollar) 
- **EUR** (Euro) - **NEW in v2.0**
- **GBP** (British Pound) - **NEW in v2.0**
- **CHF** (Swiss Franc) - Display conversion
- **Gold** (Ounces) - Alternative store of value

### 📊 Real-Time Data
- **Live BTC Prices**: Real-time Bitcoin pricing in all supported currencies
- **Gain/Loss Calculation**: Automatic profit/loss calculation
- **Portfolio Summary**: Comprehensive overview of your Bitcoin position
- **Price History**: Track your cost basis vs. current market value

### 🔒 Security & Privacy
- **Local Database**: All data stored locally using SQLite
- **User Authentication**: Secure login with JWT tokens
- **Data Privacy**: No external data sharing or cloud storage
- **Encrypted Storage**: Password hashing and secure authentication

### 📁 Data Management
- **CSV Import/Export**: Bulk import transactions from CSV files
- **Data Backup**: Easy backup and restore functionality
- **Transaction Editing**: Modify or delete existing transactions
- **Search & Filter**: Advanced filtering by date, currency, and type

## � Quick Start

### Download Pre-Built Executable (Recommended)

1. **Download** the latest release for your operating system:
   - [Windows (64-bit)](https://github.com/yourusername/btc-portfolio-tracker/releases/latest/download/BTC-Portfolio-Tracker-Windows.exe)
   - [macOS (Intel/Apple Silicon)](https://github.com/yourusername/btc-portfolio-tracker/releases/latest/download/BTC-Portfolio-Tracker-macOS.dmg)
   - [Linux (64-bit)](https://github.com/yourusername/btc-portfolio-tracker/releases/latest/download/BTC-Portfolio-Tracker-Linux.tar.gz)

2. **Install/Run**:
   - **Windows**: Double-click the `.exe` file
   - **macOS**: Open the `.dmg` file and drag to Applications
   - **Linux**: Extract and run the executable

3. **First Launch**:
   - Register a new account or login
   - Start tracking your Bitcoin portfolio!

## 📦 Installation

### Option 1: Pre-Built Executables
Download the appropriate executable for your system from the [Releases](https://github.com/yourusername/btc-portfolio-tracker/releases) page.

### Option 2: Install from Source

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

#### Installation Steps

```bash
# Clone the repository
git clone https://github.com/yourusername/btc-portfolio-tracker.git
cd btc-portfolio-tracker

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python frontend/btc_gui.py
```

#### Backend Setup (for development)
```bash
# In a separate terminal, start the backend server
cd backend
python app.py
```

## 🎯 Usage

### Getting Started

1. **Launch the Application**
   - Run the executable or use `python frontend/btc_gui.py`
   - The application will start with the login screen

2. **Create Account**
   - Click "Register" to create a new account
   - Choose a secure username and password
   - Login with your credentials

3. **Dashboard Overview**
   - **Summary Tab**: View your net Bitcoin position and current value
   - **Savings Tab**: Record Bitcoin purchases and savings
   - **Spending Tab**: Track Bitcoin expenditures
   - **Import CSV Tab**: Bulk import transaction data

### Recording Transactions

#### Adding Savings (Bitcoin Purchases)
1. Go to the **Savings** tab
2. Enter transaction details:
   - Date (YYYY-MM-DD)
   - BTC Amount
   - Currency (USD, CAD, EUR, GBP)
   - Cost in selected currency
   - Notes (optional)
3. Click "Add Saving"

#### Adding Spending (Bitcoin Expenditures)
1. Go to the **Spending** tab
2. Enter transaction details (same format as savings)
3. Click "Add Spending"

#### Bulk Import via CSV
1. Go to the **Import CSV** tab
2. Prepare your CSV file with the following columns:
   ```
   date,transaction_type,btc_amount,cost_usd,cost_cad,cost_eur,cost_gbp,currency,notes
   2024-01-15,save,0.00125000,50.00,67.50,46.00,39.50,USD,First purchase
   2024-02-01,spend,0.00050000,25.00,33.75,23.00,19.75,USD,Coffee payment
   ```
3. Select your CSV file and click "Import CSV"

### Currency Features

- **Display Currency**: Choose your preferred currency for summary display
- **Transaction Currency**: Record transactions in any supported currency
- **Automatic Conversion**: Costs are automatically converted to all currencies
- **Filtering**: Filter transactions by currency type

## 💱 Multi-Currency Support

### Supported Currencies

| Currency | Code | Symbol | Support Level |
|----------|------|--------|---------------|
| US Dollar | USD | $ | Full Support |
| Canadian Dollar | CAD | C$ | Full Support |
| Euro | EUR | € | Full Support ✨ |
| British Pound | GBP | £ | Full Support ✨ |
| Swiss Franc | CHF | ₣ | Display Only |
| Gold | XAU | oz | Display Only |

### Currency Features

- **Real-time Exchange Rates**: Live pricing from CoinGecko API
- **Historical Cost Basis**: Track your cost basis in multiple currencies
- **Automatic Conversion**: Transactions automatically converted to all supported currencies
- **Flexible Display**: View portfolio summary in any supported currency

```
btc-tracker/
├── backend/
│   ├── app.py              # Flask backend API
│   ├── requirements.txt    # Python dependencies
│   └── portfolio.db        # SQLite database
├── frontend/
│   └── btc_gui.py         # tkinter GUI application
├── btc_icon.svg           # App icon (SVG)
├── btc_icon.png           # App icon (PNG)
└── README.md              # This file
```

## 🛠️ Development

### Building from Source

#### Prerequisites
- Python 3.8+
- Git
- Virtual environment (recommended)

#### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/btc-portfolio-tracker.git
cd btc-portfolio-tracker

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Running in Development Mode

```bash
# Terminal 1: Start backend server
cd backend
python app.py

# Terminal 2: Start frontend GUI
cd frontend
python btc_gui.py
```

#### Building Executables

```bash
# Build executable for current platform
python build_executable.py

# Output will be in the 'dist' directory
```

### Project Structure

```
btc-portfolio-tracker/
├── frontend/
│   ├── btc_gui.py          # Main GUI application
│   └── utils/              # GUI utilities
├── backend/
│   ├── app.py              # Flask backend server
│   └── portfolio.db        # SQLite database
├── assets/
│   ├── icons/              # Application icons
│   └── screenshots/        # Documentation images
├── build_executable.py     # Build script for executables
├── setup.py               # Package setup
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── LICENSE               # MIT License
```

### API Endpoints

#### Authentication
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /protected` - Verify authentication

#### Transactions
- `GET /transactions` - List transactions (supports filtering)
- `POST /transactions` - Create new transaction
- `PUT /transactions/{id}` - Update transaction
- `DELETE /transactions/{id}` - Delete transaction

#### Portfolio
- `GET /portfolio/summary` - Get portfolio summary
- `GET /btc-price` - Get current BTC prices

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 Python style guidelines
- Use `black` for code formatting
- Run `flake8` for linting
- Add tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CoinGecko API](https://www.coingecko.com/api) for real-time Bitcoin pricing
- [Flask](https://flask.palletsprojects.com/) for the backend framework
- [Tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI framework
- [SQLite](https://sqlite.org/) for local data storage

## 📞 Support

- � Bug Reports: [GitHub Issues](https://github.com/yourusername/btc-portfolio-tracker/issues)
- 📖 Documentation: [Wiki](https://github.com/yourusername/btc-portfolio-tracker/wiki)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/btc-portfolio-tracker/discussions)

---

<div align="center">
  <p>Made with ❤️ by the BTC Portfolio Tracker Team</p>
  <p>⭐ Star us on GitHub if you find this project useful!</p>
</div>
