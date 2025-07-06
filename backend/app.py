from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from dotenv import load_dotenv
import requests

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
import secrets
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- JWT AND SECRET KEY CONFIGURATION START HERE ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    print(f"Warning: SECRET_KEY not found in .env. Using a generated key: {app.config['SECRET_KEY']}")
    print("Please add SECRET_KEY=YOUR_GENERATED_KEY_HERE to your .env file for production use.")

app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
if not app.config["JWT_SECRET_KEY"]:
    app.config["JWT_SECRET_KEY"] = secrets.token_hex(32)
    print(f"Warning: JWT_SECRET_KEY not found in .env. Using a generated key: {app.config['JWT_SECRET_KEY']}")
    print("Please add JWT_SECRET_KEY=YOUR_GENERATED_KEY_HERE to your .env file for production use.")

# Set JWT token expiration to 8 hours for better user experience
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)

jwt = JWTManager(app)
# --- JWT AND SECRET KEY CONFIGURATION END HERE ---

DATABASE = 'portfolio.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            transaction_date TEXT NOT NULL,
            transaction_type TEXT NOT NULL CHECK (transaction_type IN ('save', 'spend')),
            btc_amount REAL NOT NULL,
            cost_usd REAL NOT NULL,
            cost_cad REAL NOT NULL,
            cost_eur REAL DEFAULT 0,
            cost_gbp REAL DEFAULT 0,
            currency TEXT DEFAULT 'USD',
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Migration: Copy existing purchases to transactions table as 'save' type
    # First, add new columns to existing transactions if they don't exist
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'cost_eur' not in columns:
        cursor.execute('ALTER TABLE transactions ADD COLUMN cost_eur REAL DEFAULT 0')
    if 'cost_gbp' not in columns:
        cursor.execute('ALTER TABLE transactions ADD COLUMN cost_gbp REAL DEFAULT 0')
    if 'currency' not in columns:
        cursor.execute('ALTER TABLE transactions ADD COLUMN currency TEXT DEFAULT "USD"')
    
    # Now copy existing purchases to transactions table as 'save' type (if purchases table exists)
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO transactions (user_id, transaction_date, transaction_type, btc_amount, cost_usd, cost_cad, cost_eur, cost_gbp, currency, notes)
            SELECT user_id, purchase_date, 'save', btc_amount, cost_usd, cost_cad, 0, 0, 'USD', notes 
            FROM purchases
        ''')
    except sqlite3.OperationalError:
        # Purchases table doesn't exist, skip migration
        pass
    conn.commit()
    conn.close()
    print(f"Database '{DATABASE}' initialized with users and transactions tables.")

with app.app_context():
    init_db()

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the BTC Portfolio Tracker API!"})

@app.route('/test-db', methods=['GET'])
def test_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        table_names = [table[0] for table in tables]
        return jsonify({"message": "Database connection successful!", "tables_found": table_names})
    except Exception as e:
        return jsonify({"message": "Database connection failed!", "error": str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                       (username, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"msg": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"msg": "Username already exists"}), 409
    except Exception as e:
        conn.close()
        return jsonify({"msg": "An error occurred during registration", "error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        access_token = create_access_token(identity=str(user['id']))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    user = conn.execute("SELECT username FROM users WHERE id = ?", (current_user_id,)).fetchone()
    conn.close()

    if user:
        return jsonify(logged_in_as=user['username'], user_id=current_user_id), 200
    else:
        return jsonify({"msg": "User not found for this token"}), 404

# --- Transaction Management Endpoints START HERE ---

@app.route('/transactions', methods=['POST'])
@jwt_required()
def add_transaction():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    transaction_date = data.get('transaction_date')
    transaction_type = data.get('transaction_type')  # 'save' or 'spend'
    btc_amount = data.get('btc_amount')
    cost_usd = data.get('cost_usd', 0)
    cost_cad = data.get('cost_cad', 0)
    cost_eur = data.get('cost_eur', 0)
    cost_gbp = data.get('cost_gbp', 0)
    currency = data.get('currency', 'USD')  # Default to USD
    notes = data.get('notes', '')

    if not (transaction_date and transaction_type and btc_amount):
        return jsonify({"msg": "Missing required fields"}), 400
    
    if transaction_type not in ['save', 'spend']:
        return jsonify({"msg": "Invalid transaction type. Must be 'save' or 'spend'"}), 400

    if currency not in ['USD', 'CAD', 'EUR', 'GBP']:
        return jsonify({"msg": "Invalid currency. Must be USD, CAD, EUR, or GBP"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO transactions (user_id, transaction_date, transaction_type, btc_amount, cost_usd, cost_cad, cost_eur, cost_gbp, currency, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (current_user_id, transaction_date, transaction_type, btc_amount, cost_usd, cost_cad, cost_eur, cost_gbp, currency, notes)
    )
    conn.commit()
    conn.close()
    return jsonify({"msg": "Transaction added successfully"}), 201

@app.route('/transactions', methods=['GET'])
@jwt_required()
def list_transactions():
    current_user_id = get_jwt_identity()
    transaction_type = request.args.get('type')  # Optional filter by type
    currency = request.args.get('currency')  # Optional filter by currency
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build query based on filters
    query = '''SELECT id, transaction_date, transaction_type, btc_amount, cost_usd, cost_cad, cost_eur, cost_gbp, currency, notes
               FROM transactions WHERE user_id = ?'''
    params = [current_user_id]
    
    if transaction_type:
        query += ' AND transaction_type = ?'
        params.append(transaction_type)
    
    if currency:
        query += ' AND currency = ?'
        params.append(currency)
    
    query += ' ORDER BY transaction_date DESC'
    
    cursor.execute(query, params)
    transactions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(transactions), 200

@app.route('/transactions/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    transaction_date = data.get('transaction_date')
    transaction_type = data.get('transaction_type')
    btc_amount = data.get('btc_amount')
    cost_usd = data.get('cost_usd', 0)
    cost_cad = data.get('cost_cad', 0)
    cost_eur = data.get('cost_eur', 0)
    cost_gbp = data.get('cost_gbp', 0)
    currency = data.get('currency', 'USD')
    notes = data.get('notes', '')

    if not (transaction_date and transaction_type and btc_amount):
        return jsonify({"msg": "Missing required fields"}), 400
    
    if transaction_type not in ['save', 'spend']:
        return jsonify({"msg": "Invalid transaction type. Must be 'save' or 'spend'"}), 400

    if currency not in ['USD', 'CAD', 'EUR', 'GBP']:
        return jsonify({"msg": "Invalid currency. Must be USD, CAD, EUR, or GBP"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE transactions
           SET transaction_date = ?, transaction_type = ?, btc_amount = ?, cost_usd = ?, cost_cad = ?, cost_eur = ?, cost_gbp = ?, currency = ?, notes = ?
           WHERE id = ? AND user_id = ?''',
        (transaction_date, transaction_type, btc_amount, cost_usd, cost_cad, cost_eur, cost_gbp, currency, notes, transaction_id, current_user_id)
    )
    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated:
        return jsonify({"msg": "Transaction updated successfully"}), 200
    else:
        return jsonify({"msg": "Transaction not found or not authorized"}), 404

@app.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''DELETE FROM transactions WHERE id = ? AND user_id = ?''',
        (transaction_id, current_user_id)
    )
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted:
        return jsonify({"msg": "Transaction deleted successfully"}), 200
    else:
        return jsonify({"msg": "Transaction not found or not authorized"}), 404

# --- Portfolio Management Endpoints START HERE ---

@app.route('/purchases', methods=['POST'])
@jwt_required()
def add_purchase():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    purchase_date = data.get('purchase_date')
    btc_amount = data.get('btc_amount')
    cost_usd = data.get('cost_usd')
    cost_cad = data.get('cost_cad')
    cost_eur = data.get('cost_eur', 0)
    cost_gbp = data.get('cost_gbp', 0)
    currency = data.get('currency', 'USD')
    notes = data.get('notes', '')

    if not (purchase_date and btc_amount and cost_usd and cost_cad):
        return jsonify({"msg": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO transactions (user_id, transaction_date, transaction_type, btc_amount, cost_usd, cost_cad, cost_eur, cost_gbp, currency, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (current_user_id, purchase_date, 'save', btc_amount, cost_usd, cost_cad, cost_eur, cost_gbp, currency, notes)
    )
    conn.commit()
    conn.close()
    return jsonify({"msg": "Purchase added successfully"}), 201

@app.route('/purchases', methods=['GET'])
@jwt_required()
def list_purchases():
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT id, transaction_date as purchase_date, btc_amount, cost_usd, cost_cad, cost_eur, cost_gbp, currency, notes
           FROM transactions WHERE user_id = ? AND transaction_type = 'save' ORDER BY transaction_date DESC''',
        (current_user_id,)
    )
    purchases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(purchases), 200

@app.route('/purchases/<int:purchase_id>', methods=['PUT'])
@jwt_required()
def update_purchase(purchase_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    purchase_date = data.get('purchase_date')
    btc_amount = data.get('btc_amount')
    cost_usd = data.get('cost_usd')
    cost_cad = data.get('cost_cad')
    cost_eur = data.get('cost_eur', 0)
    cost_gbp = data.get('cost_gbp', 0)
    currency = data.get('currency', 'USD')
    notes = data.get('notes', '')

    if not (purchase_date and btc_amount and cost_usd and cost_cad):
        return jsonify({"msg": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE transactions
           SET transaction_date = ?, btc_amount = ?, cost_usd = ?, cost_cad = ?, cost_eur = ?, cost_gbp = ?, currency = ?, notes = ?
           WHERE id = ? AND user_id = ? AND transaction_type = 'save' ''',
        (purchase_date, btc_amount, cost_usd, cost_cad, cost_eur, cost_gbp, currency, notes, purchase_id, current_user_id)
    )
    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated:
        return jsonify({"msg": "Purchase updated successfully"}), 200
    else:
        return jsonify({"msg": "Purchase not found or not authorized"}), 404

@app.route('/purchases/<int:purchase_id>', methods=['DELETE'])
@jwt_required()
def delete_purchase(purchase_id):
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''DELETE FROM transactions WHERE id = ? AND user_id = ? AND transaction_type = 'save' ''',
        (purchase_id, current_user_id)
    )
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted:
        return jsonify({"msg": "Purchase deleted successfully"}), 200
    else:
        return jsonify({"msg": "Purchase not found or not authorized"}), 404

# --- Portfolio Summary Endpoint ---
@app.route('/portfolio/summary', methods=['GET'])
@jwt_required()
def portfolio_summary():
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get savings (positive BTC)
    cursor.execute(
        '''SELECT SUM(btc_amount) as total_btc, SUM(cost_usd) as total_usd, SUM(cost_cad) as total_cad, SUM(cost_eur) as total_eur, SUM(cost_gbp) as total_gbp
           FROM transactions WHERE user_id = ? AND transaction_type = 'save' ''',
        (current_user_id,)
    )
    savings = cursor.fetchone()
    
    # Get spending (negative BTC)
    cursor.execute(
        '''SELECT SUM(btc_amount) as total_btc, SUM(cost_usd) as total_usd, SUM(cost_cad) as total_cad, SUM(cost_eur) as total_eur, SUM(cost_gbp) as total_gbp
           FROM transactions WHERE user_id = ? AND transaction_type = 'spend' ''',
        (current_user_id,)
    )
    spending = cursor.fetchone()
    
    conn.close()

    # Fetch live BTC price
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': 'bitcoin', 'vs_currencies': 'usd,cad,eur,gbp'},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        price_usd = data['bitcoin']['usd']
        price_cad = data['bitcoin']['cad']
        price_eur = data['bitcoin']['eur']
        price_gbp = data['bitcoin']['gbp']
    except Exception as e:
        price_usd = None
        price_cad = None
        price_eur = None
        price_gbp = None

    # Calculate totals
    saved_btc = savings['total_btc'] or 0
    saved_usd = savings['total_usd'] or 0
    saved_cad = savings['total_cad'] or 0
    saved_eur = savings['total_eur'] or 0
    saved_gbp = savings['total_gbp'] or 0
    
    spent_btc = spending['total_btc'] or 0
    spent_usd = spending['total_usd'] or 0
    spent_cad = spending['total_cad'] or 0
    spent_eur = spending['total_eur'] or 0
    spent_gbp = spending['total_gbp'] or 0
    
    # Net calculations
    net_btc = saved_btc - spent_btc
    net_cost_usd = saved_usd - spent_usd
    net_cost_cad = saved_cad - spent_cad
    net_cost_eur = saved_eur - spent_eur
    net_cost_gbp = saved_gbp - spent_gbp

    return jsonify({
        "net_btc": net_btc,
        "net_cost_basis_usd": net_cost_usd,
        "net_cost_basis_cad": net_cost_cad,
        "net_cost_basis_eur": net_cost_eur,
        "net_cost_basis_gbp": net_cost_gbp,
        "current_value_usd": net_btc * price_usd if price_usd else None,
        "current_value_cad": net_btc * price_cad if price_cad else None,
        "current_value_eur": net_btc * price_eur if price_eur else None,
        "current_value_gbp": net_btc * price_gbp if price_gbp else None,
        "savings": {
            "btc": saved_btc,
            "cost_usd": saved_usd,
            "cost_cad": saved_cad,
            "cost_eur": saved_eur,
            "cost_gbp": saved_gbp
        },
        "spending": {
            "btc": spent_btc,
            "cost_usd": spent_usd,
            "cost_cad": spent_cad,
            "cost_eur": spent_eur,
            "cost_gbp": spent_gbp
        },
        "btc_price_usd": price_usd,
        "btc_price_cad": price_cad,
        "btc_price_eur": price_eur,
        "btc_price_gbp": price_gbp
    }), 200

@app.route('/btc-price', methods=['GET'])
def get_btc_price():
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={
                'ids': 'bitcoin',
                'vs_currencies': 'usd,cad,eur,gbp'
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        price_usd = data['bitcoin']['usd']
        price_cad = data['bitcoin']['cad']
        price_eur = data['bitcoin']['eur']
        price_gbp = data['bitcoin']['gbp']
        return jsonify({
            'btc_usd': price_usd, 
            'btc_cad': price_cad,
            'btc_eur': price_eur,
            'btc_gbp': price_gbp
        }), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to fetch BTC price', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)