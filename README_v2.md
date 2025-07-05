# BTC Portfolio Tracker v2.0

A comprehensive Bitcoin portfolio tracker that now supports both **savings** and **spending** transactions, giving you complete visibility into your Bitcoin activity.

## 🚀 New Features in v2.0

### Enhanced Transaction Types
- **Savings Tracking**: Record Bitcoin purchases, acquisitions, and any BTC coming into your portfolio
- **Spending Tracking**: Track Bitcoin spending, sales, and any BTC going out of your portfolio
- **Net Position Calculation**: Automatically calculates your current net BTC position (savings - spending)

### Improved User Interface
- **📊 Summary Tab**: Comprehensive overview showing net position, savings/spending breakdown, and current portfolio value
- **💰 Savings Tab**: Dedicated interface for recording Bitcoin savings/purchases
- **💸 Spending Tab**: Dedicated interface for recording Bitcoin spending/sales
- **📁 CSV Import Tab**: Bulk import transactions from CSV files

### Enhanced Portfolio Analytics
- **Net BTC Position**: Your actual Bitcoin holdings after accounting for spending
- **Savings vs Spending Breakdown**: Clear visualization of money in vs money out
- **Real-time Value Calculation**: Current portfolio value based on live BTC prices
- **Profit/Loss Tracking**: See your gains or losses at a glance

## 📋 Features

### Core Functionality
- **User Authentication**: Secure login and registration system
- **Transaction Management**: Add, edit, and delete both savings and spending transactions
- **Multi-Currency Support**: Track costs in USD, CAD, Swiss Franc, and Ounces of Gold
- **Real-time BTC Prices**: Live Bitcoin price data from CoinGecko API
- **Data Export/Import**: CSV import/export functionality for bulk operations

### Security & Data
- **JWT Authentication**: Secure API communication
- **SQLite Database**: Local data storage with proper relationships
- **Data Validation**: Client and server-side validation for all inputs
- **Backup Compatible**: Easy data migration and backup support

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd /home/mhf/Projects/btc-tracker/backend
   ```

2. Install dependencies:
   ```bash
   pip install flask flask-cors flask-jwt-extended python-dotenv requests
   ```

3. Create environment file (optional):
   ```bash
   # Create .env file with your keys (optional)
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   ```

4. Start the backend server:
   ```bash
   python3 app.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd /home/mhf/Projects/btc-tracker/frontend
   ```

2. Install dependencies:
   ```bash
   pip install tkinter requests  # tkinter is usually included with Python
   ```

3. Run the application:
   ```bash
   python3 btc_gui_v2.py
   ```

## 📊 Usage Guide

### Getting Started
1. **Register/Login**: Create an account or log in to an existing one
2. **Add Transactions**: Use the Savings or Spending tabs to record transactions
3. **View Summary**: Check your portfolio overview in the Summary tab
4. **Import Data**: Use the CSV Import tab for bulk transaction import

### Recording Savings (BTC In)
- Date of transaction
- BTC amount acquired
- Cost in USD or CAD
- Optional notes

### Recording Spending (BTC Out)
- Date of transaction
- BTC amount spent
- Value in USD or CAD
- Optional notes

### CSV Import Format
```csv
date,transaction_type,btc_amount,cost_usd,cost_cad,notes
2024-01-15,save,0.00125000,50.00,67.50,First BTC purchase
2024-02-15,spend,0.00050000,25.00,33.75,Paid for coffee
```

## 🔧 Technical Architecture

### Backend (Flask)
- **Framework**: Flask with CORS support
- **Authentication**: JWT-based authentication
- **Database**: SQLite with proper schema migration
- **API Endpoints**: RESTful API for all operations
- **External API**: CoinGecko for live BTC prices

### Frontend (Tkinter)
- **Framework**: Python Tkinter for cross-platform GUI
- **Architecture**: Modular class-based design
- **Components**: Separate tabs for different functionalities
- **Validation**: Client-side input validation and error handling

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- Transactions table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    transaction_date TEXT NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('save', 'spend')),
    btc_amount REAL NOT NULL,
    cost_usd REAL NOT NULL,
    cost_cad REAL NOT NULL,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Legacy purchases table (for backward compatibility)
CREATE TABLE purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    purchase_date TEXT NOT NULL,
    btc_amount REAL NOT NULL,
    cost_usd REAL NOT NULL,
    cost_cad REAL NOT NULL,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 🔌 API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /protected` - Test protected route

### Transactions
- `POST /transactions` - Add new transaction
- `GET /transactions` - List all transactions
- `GET /transactions?type=save` - List savings transactions
- `GET /transactions?type=spend` - List spending transactions
- `PUT /transactions/{id}` - Update transaction
- `DELETE /transactions/{id}` - Delete transaction

### Portfolio
- `GET /portfolio/summary` - Get portfolio summary
- `GET /btc-price` - Get current BTC price

### Legacy (Backward Compatibility)
- `POST /purchases` - Add purchase (legacy)
- `GET /purchases` - List purchases (legacy)
- `PUT /purchases/{id}` - Update purchase (legacy)
- `DELETE /purchases/{id}` - Delete purchase (legacy)

## 📁 File Structure

```
btc-tracker/
├── backend/
│   ├── app.py              # Flask backend server
│   ├── portfolio.db        # SQLite database
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables (optional)
├── frontend/
│   ├── btc_gui_v2.py      # Main GUI application (v2.0)
│   ├── btc_gui.py         # Original GUI (v1.0)
│   ├── sample_transactions.csv  # Sample CSV for import
│   └── utils.py           # Utility functions
└── README.md              # This file
```

## 🆕 Migration from v1.0

The application automatically migrates your existing purchase data to the new transaction system:
- All existing purchases become "save" transactions
- Original purchase table is preserved for backward compatibility
- New transaction types are available immediately
- No data loss during migration

## 🎯 Future Enhancements

- **Advanced Analytics**: Charts and graphs for portfolio performance
- **Multi-Wallet Support**: Track multiple Bitcoin wallets
- **Tax Reporting**: Generate tax reports for Bitcoin transactions
- **Mobile App**: Mobile version of the application
- **Cloud Sync**: Synchronize data across devices
- **Price Alerts**: Set up notifications for price changes
- **DCA Tracking**: Dollar-cost averaging analysis

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure the backend server is running
   - Check if port 5000 is available

2. **CSV Import Errors**
   - Verify CSV format matches the expected structure
   - Check that all required columns are present
   - Ensure date format is YYYY-MM-DD

3. **Price Data Unavailable**
   - Check internet connection
   - CoinGecko API might be temporarily unavailable

### Getting Help
- Check the console output for detailed error messages
- Verify all dependencies are installed
- Ensure Python 3.7+ is being used

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Bitcoin Tracking! 🚀**
