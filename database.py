import os
import shutil
import sqlite3
from datetime import datetime

# Determine base application directory (works on both Android and Desktop)
def get_app_dir():
    # Detect Android native app path
    if "ANDROID_ARGUMENT" in os.environ or "PYTHON_SERVICE_ARGUMENT" in os.environ:
        from android.storage import app_storage_path
        return app_storage_path()
    return os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(get_app_dir(), "adarsh_billing.db")

def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_db() as conn:
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                tax_id TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                sku_prefix TEXT DEFAULT ''
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                sku TEXT,
                name TEXT NOT NULL,
                hsn_sac TEXT,
                unit_price REAL DEFAULT 0.0
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_type TEXT DEFAULT 'Tax Invoice',
                invoice_num TEXT UNIQUE NOT NULL,
                order_no TEXT,
                customer_id INTEGER,
                invoice_date TEXT,
                financial_year TEXT,
                subtotal REAL,
                cgst_rate REAL,
                cgst_amount REAL,
                sgst_rate REAL,
                sgst_amount REAL,
                total REAL,
                payment_status TEXT DEFAULT 'Unpaid'
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS delivery_challans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challan_num TEXT UNIQUE NOT NULL,
                challan_date TEXT,
                customer_id INTEGER,
                po_ref TEXT,
                status TEXT DEFAULT 'Open'
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS company_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                address TEXT,
                gstin TEXT,
                phone TEXT,
                email TEXT,
                inv_prefix TEXT DEFAULT 'AEW/2026-27/',
                next_inv_seq INTEGER DEFAULT 1
            )
        """)

        cur.execute("""
            INSERT OR IGNORE INTO company_settings (id, name, address, gstin, phone, email, inv_prefix, next_inv_seq)
            VALUES (1, 'Adarsh Engineering Works', 'Thane, Maharashtra', '27AAAAA0000A1Z5', '9820000000', 'adarsh@example.com', 'AEW/2026-27/', 1)
        """)
        conn.commit()

# --- BACKUP AND RESTORE UTILITIES ---
def backup_database(destination_dir=None):
    """Creates a point-in-time snapshot backup of adarsh_billing.db."""
    try:
        if not os.path.exists(DB_PATH):
            return False, "Database does not exist."

        if not destination_dir:
            destination_dir = os.path.join(get_app_dir(), "backups")
        os.makedirs(destination_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(destination_dir, f"backup_aew_{timestamp}.db")

        # Perform live safe online SQLite backup
        with get_db() as src:
            dest = sqlite3.connect(backup_path)
            src.backup(dest)
            dest.close()

        return True, backup_path
    except Exception as e:
        return False, str(e)

def restore_database(source_backup_path):
    """Restores database from an existing .db file after running integrity check."""
    if not os.path.exists(source_backup_path):
        return False, "Source backup file not found."

    try:
        # 1. Integrity verification
        test_conn = sqlite3.connect(source_backup_path)
        cur = test_conn.cursor()
        cur.execute("PRAGMA integrity_check;")
        res = cur.fetchone()
        test_conn.close()

        if not res or res[0] != "ok":
            return False, "Selected backup failed integrity check."

        # 2. Safety snapshot of current database
        safety_path = os.path.join(get_app_dir(), "pre_restore_safety.db")
        if os.path.exists(DB_PATH):
            with get_db() as curr_conn:
                safety_dest = sqlite3.connect(safety_path)
                curr_conn.backup(safety_dest)
                safety_dest.close()

        # 3. Replace current database
        with sqlite3.connect(source_backup_path) as src_conn:
            with get_db() as target_conn:
                src_conn.backup(target_conn)

        return True, "Database restored successfully."
    except Exception as e:
        return False, str(e)
