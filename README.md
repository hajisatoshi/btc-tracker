# 🚀 BTC Tracker

A Bitcoin portfolio tracking application built with Python and tkinter.

![BTC Tracker Icon](btc_icon.png)

## ✨ Features

- **Real-time Bitcoin price tracking** - Get current BTC prices from CoinGecko API
- **Portfolio management** - Add, edit, and remove Bitcoin holdings
- **Profit/Loss calculation** - Track your investment performance
- **Modern GUI** - Clean and intuitive interface
- **Persistent data** - Your portfolio data is saved locally
- **Desktop integration** - Launch from applications menu

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Frontend**: Python tkinter
- **Database**: SQLite
- **API**: CoinGecko for real-time prices
- **Icon**: Custom Bitcoin-themed SVG design

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/btc-tracker.git
   cd btc-tracker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run the application**:
   ```bash
   python3 frontend/btc_gui.py
   ```

## 🚀 Usage

1. **Start the app** - Launch from applications menu or run the Python script
2. **Add holdings** - Click "Add Transaction" to record your Bitcoin purchases
3. **View portfolio** - See your total holdings and current value
4. **Track performance** - Monitor profit/loss in real-time

## 📁 Project Structure

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

## 🎨 Features in Detail

- **Real-time pricing**: Fetches current Bitcoin prices from CoinGecko API
- **Transaction history**: Keep track of all your Bitcoin purchases
- **Portfolio summary**: See total holdings, current value, and profit/loss
- **Responsive design**: Clean and modern user interface
- **Data persistence**: All data stored locally in SQLite database

## 🔧 Development

To contribute or modify the app:

1. **Edit the code** in your favorite IDE
2. **Test changes** by running the app
3. **Commit changes** with Git
4. **Push to GitHub** to share

## 📱 Desktop Integration

The app includes a desktop entry file for easy system integration:
- Launch from applications menu
- Custom Bitcoin-themed icon
- Runs independently of development environment

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests!

## 📄 License

This project is open source and available under the MIT License.

---

**Made with ❤️ and Python** 🐍
