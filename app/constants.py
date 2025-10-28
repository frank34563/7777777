import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

SUPPORT_USERNAME = "AiCrypto_Support1"
SUPPORT_HANDLE = f"@{SUPPORT_USERNAME}"

MIN_DEPOSIT = 10
DAILY_PROFIT_RATE = 0.015  # 1.5 percent

MAIN_TRC20_WALLET = os.getenv("MAIN_TRC20_WALLET", "TAbcDeF123...XyZ789")

DB_PATH = os.getenv("DB_PATH", "database.sqlite3")

# Callback data keys
CB_BALANCE = "balance"
CB_INVEST = "invest"
CB_WITHDRAW = "withdraw"
CB_HISTORY = "history"
CB_SETTINGS = "settings"
CB_INFO = "info"
CB_HELP = "help"
CB_BACK = "back"

CB_SET_WALLET = "set_wallet"
CB_CHANGE_WALLET = "change_wallet"

CB_NETWORK_TRC20 = "net_trc20"
CB_NETWORK_ERC20 = "net_erc20"
CB_NETWORK_BEP20 = "net_bep20"

# Admin actions
CB_ADMIN_APPROVE_DEPOSIT = "admin_approve_deposit"
CB_ADMIN_REJECT_DEPOSIT = "admin_reject_deposit"
CB_ADMIN_APPROVE_WITHDRAW = "admin_approve_withdraw"
CB_ADMIN_REJECT_WITHDRAW = "admin_reject_withdraw"

# Transaction types and status
TX_DEPOSIT = "deposit"
TX_WITHDRAW = "withdraw"
TX_PROFIT = "profit"
TX_REJECT = "reject"

ST_PENDING = "pending"
ST_APPROVED = "approved"
ST_REJECTED = "rejected"
ST_PAID = "paid"
ST_CREDITED = "credited"
