import sqlite3
from contextlib import closing
from .constants import DB_PATH

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with closing(get_conn()) as conn, conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            tg_id INTEGER UNIQUE NOT NULL,
            balance REAL NOT NULL DEFAULT 0,
            in_process REAL NOT NULL DEFAULT 0,
            daily_profit REAL NOT NULL DEFAULT 0,
            total_profit REAL NOT NULL DEFAULT 0,
            wallet TEXT,
            network TEXT,
            join_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            txid TEXT,
            wallet TEXT,
            network TEXT,
            screenshot_file_id TEXT,
            admin_note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_user ON transactions(user_id)")

def get_or_create_user(tg_id: int) -> sqlite3.Row:
    with closing(get_conn()) as conn, conn:
        cur = conn.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
        row = cur.fetchone()
        if row:
            return row
        conn.execute("INSERT INTO users (tg_id) VALUES (?)", (tg_id,))
        cur = conn.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
        return cur.fetchone()

def update_user_wallet(tg_id: int, wallet: str, network: str):
    with closing(get_conn()) as conn, conn:
        conn.execute("UPDATE users SET wallet = ?, network = ? WHERE tg_id = ?", (wallet, network, tg_id,))

def get_user_by_tg(tg_id: int):
    with closing(get_conn()) as conn:
        cur = conn.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
        return cur.fetchone()

def add_transaction(user_id: int, tx_type: str, amount: float, status: str,
                    txid: str = None, wallet: str = None, network: str = None, screenshot_file_id: str = None,
                    admin_note: str = None):
    with closing(get_conn()) as conn, conn:
        conn.execute("""            INSERT INTO transactions (user_id, type, amount, status, txid, wallet, network, screenshot_file_id, admin_note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, tx_type, amount, status, txid, wallet, network, screenshot_file_id, admin_note))

def list_transactions(user_id: int, limit: int = 20):
    with closing(get_conn()) as conn:
        cur = conn.execute("""            SELECT * FROM transactions WHERE user_id = ? ORDER BY datetime(created_at) DESC LIMIT ?
        """, (user_id, limit))
        return cur.fetchall()

def move_between_balances(tg_id: int, from_field: str, to_field: str, amount: float):
    with closing(get_conn()) as conn, conn:
        conn.execute(f"""            UPDATE users
            SET {from_field} = MAX({from_field} - ?, 0),
                {to_field} = {to_field} + ?
            WHERE tg_id = ?
        """, (amount, amount, tg_id))
