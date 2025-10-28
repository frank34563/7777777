AiCrypto Investment Bot

Prereqs
1. Python 3.12
2. Telegram Bot token
3. Admin Telegram user id

Environment
Copy .env.example to .env and set
BOT_TOKEN
ADMIN_ID
MAIN_TRC20_WALLET
DB_PATH optional

Install
pip install -r requirements.txt

Run locally
python -m app.main

Railway or Docker
Use Procfile worker entry
Ensure your .env vars are set in Railway
Set start command to python -m app.main

Daily profit
The bot uses JobQueue to run at midnight UTC
Adjust schedule in main.py if needed
