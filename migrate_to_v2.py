#!/usr/bin/env python3
"""
Migration script for BTC Portfolio Tracker v1.0 to v2.0
This script helps migrate data from the old purchases-only system to the new transactions system.
"""

import sqlite3
import os
import sys
from datetime import datetime

def backup_database(db_path):
    """Create a backup of the database"""
    backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Read original database
        with sqlite3.connect(db_path) as src:
            # Create backup
            with sqlite3.connect(backup_path) as dst:
                src.backup(dst)
        
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Failed to backup database: {e}")
        return None

def migrate_database(db_path):
    """Migrate database from v1.0 to v2.0"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Starting database migration...")
        
        # Check if transactions table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        if cursor.fetchone():
            print("ℹ️  Transactions table already exists. Checking for migration...")
            
            # Check if migration has been completed
            cursor.execute("SELECT COUNT(*) FROM transactions")
            transaction_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM purchases")
            purchase_count = cursor.fetchone()[0]
            
            if transaction_count == 0 and purchase_count > 0:
                print("🔄 Found unmigrated purchases. Migrating...")
                migrate_purchases_to_transactions(cursor)
            else:
                print("ℹ️  Database already migrated.")
        else:
            print("🔄 Creating transactions table...")
            create_transactions_table(cursor)
            
            # Check if there are purchases to migrate
            cursor.execute("SELECT COUNT(*) FROM purchases")
            purchase_count = cursor.fetchone()[0]
            
            if purchase_count > 0:
                print(f"🔄 Migrating {purchase_count} purchases to transactions...")
                migrate_purchases_to_transactions(cursor)
            else:
                print("ℹ️  No purchases found to migrate.")
        
        conn.commit()
        conn.close()
        
        print("✅ Database migration completed successfully!")
        return True
    
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_transactions_table(cursor):
    """Create the transactions table"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            transaction_date TEXT NOT NULL,
            transaction_type TEXT NOT NULL CHECK (transaction_type IN ('save', 'spend')),
            btc_amount REAL NOT NULL,
            cost_usd REAL NOT NULL,
            cost_cad REAL NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✅ Transactions table created.")

def migrate_purchases_to_transactions(cursor):
    """Migrate existing purchases to transactions as 'save' type"""
    cursor.execute('''
        INSERT INTO transactions (user_id, transaction_date, transaction_type, btc_amount, cost_usd, cost_cad, notes)
        SELECT user_id, purchase_date, 'save', btc_amount, cost_usd, cost_cad, notes 
        FROM purchases
    ''')
    
    # Get count of migrated records
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE transaction_type = 'save'")
    migrated_count = cursor.fetchone()[0]
    
    print(f"✅ Migrated {migrated_count} purchases to transactions.")

def verify_migration(db_path):
    """Verify that migration completed successfully"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        if not cursor.fetchone():
            print("❌ Transactions table not found!")
            return False
        
        # Check data integrity
        cursor.execute("SELECT COUNT(*) FROM purchases")
        purchase_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE transaction_type = 'save'")
        save_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE transaction_type = 'spend'")
        spend_count = cursor.fetchone()[0]
        
        print(f"📊 Migration Summary:")
        print(f"   - Original purchases: {purchase_count}")
        print(f"   - Migrated saves: {save_count}")
        print(f"   - Spending transactions: {spend_count}")
        print(f"   - Total transactions: {save_count + spend_count}")
        
        if purchase_count == save_count:
            print("✅ Migration verified successfully!")
            return True
        else:
            print("⚠️  Migration verification failed - counts don't match!")
            return False
    
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main migration function"""
    print("🚀 BTC Portfolio Tracker v2.0 Migration Tool")
    print("=" * 50)
    
    # Default database path
    default_db_path = "/home/mhf/Projects/btc-tracker/backend/portfolio.db"
    
    # Check if database exists
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = default_db_path
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("Please provide the correct path to your portfolio.db file.")
        print("Usage: python3 migrate_to_v2.py [path_to_database]")
        sys.exit(1)
    
    print(f"📁 Using database: {db_path}")
    
    # Create backup
    backup_path = backup_database(db_path)
    if not backup_path:
        print("❌ Failed to create backup. Aborting migration.")
        sys.exit(1)
    
    # Perform migration
    if migrate_database(db_path):
        # Verify migration
        if verify_migration(db_path):
            print("\n🎉 Migration completed successfully!")
            print("You can now use BTC Portfolio Tracker v2.0 with:")
            print("- Savings tracking (your existing purchases)")
            print("- New spending tracking capability")
            print("- Enhanced portfolio summary")
            print("\n💾 Your original data has been backed up to:")
            print(f"   {backup_path}")
        else:
            print("\n⚠️  Migration completed but verification failed.")
            print("Please check your data manually.")
    else:
        print("\n❌ Migration failed!")
        print("Your original database has been preserved.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
