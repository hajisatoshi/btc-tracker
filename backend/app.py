from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from dotenv import load_dotenv
import requests

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
import secrets

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
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            purchase_date TEXT NOT NULL,
            btc_amount REAL NOT NULL,
            cost_usd REAL NOT NULL,
            cost_cad REAL NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database '{DATABASE}' initialized with users and purchases tables.")

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
    notes = data.get('notes', '')

    if not (purchase_date and btc_amount and cost_usd and cost_cad):
        return jsonify({"msg": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO purchases (user_id, purchase_date, btc_amount, cost_usd, cost_cad, notes)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (current_user_id, purchase_date, btc_amount, cost_usd, cost_cad, notes)
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
        '''SELECT id, purchase_date, btc_amount, cost_usd, cost_cad, notes
           FROM purchases WHERE user_id = ? ORDER BY purchase_date DESC''',
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
    notes = data.get('notes', '')

    if not (purchase_date and btc_amount and cost_usd and cost_cad):
        return jsonify({"msg": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE purchases
           SET purchase_date = ?, btc_amount = ?, cost_usd = ?, cost_cad = ?, notes = ?
           WHERE id = ? AND user_id = ?''',
        (purchase_date, btc_amount, cost_usd, cost_cad, notes, purchase_id, current_user_id)
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
        '''DELETE FROM purchases WHERE id = ? AND user_id = ?''',
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
    cursor.execute(
        '''SELECT SUM(btc_amount) as total_btc, SUM(cost_usd) as total_usd, SUM(cost_cad) as total_cad
           FROM purchases WHERE user_id = ?''',
        (current_user_id,)
    )
    row = cursor.fetchone()
    conn.close()

    # Fetch live BTC price
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': 'bitcoin', 'vs_currencies': 'usd,cad'},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        price_usd = data['bitcoin']['usd']
        price_cad = data['bitcoin']['cad']
    except Exception as e:
        price_usd = None
        price_cad = None

    total_btc = row['total_btc'] or 0
    total_usd = row['total_usd'] or 0
    total_cad = row['total_cad'] or 0

    return jsonify({
        "total_btc": total_btc,
        "cost_basis_usd": total_usd,
        "cost_basis_cad": total_cad,
        "current_value_usd": total_btc * price_usd if price_usd else None,
        "current_value_cad": total_btc * price_cad if price_cad else None,
        "btc_price_usd": price_usd,
        "btc_price_cad": price_cad
    }), 200

@app.route('/btc-price', methods=['GET'])
def get_btc_price():
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={
                'ids': 'bitcoin',
                'vs_currencies': 'usd,cad'
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        price_usd = data['bitcoin']['usd']
        price_cad = data['bitcoin']['cad']
        return jsonify({'btc_usd': price_usd, 'btc_cad': price_cad}), 200
    except Exception as e:
        return jsonify({'msg': 'Failed to fetch BTC price', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 