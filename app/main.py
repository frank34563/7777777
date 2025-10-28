import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
from .constants import *
from .db import init_db, get_or_create_user, get_user_by_tg, add_transaction, move_between_balances
from .keyboards import main_menu_kb
from .handlers_common import show_main_menu, on_balance, on_history, on_info, on_help
from .handlers_invest import start_invest, deposit_amount, deposit_proof, ASK_DEPOSIT_AMOUNT, AWAIT_DEPOSIT_PROOF
from .handlers_withdraw import start_withdraw, withdraw_amount, ASK_WITHDRAW_AMOUNT
from .handlers_settings import (
    open_settings, ask_wallet, capture_wallet, capture_network, ASK_WALLET, ASK_NETWORK
)
from telegram.ext import MessageHandler, ConversationHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_or_create_user(update.effective_user.id)
    await update.message.reply_text("Welcome to AiCrypto Investment Bot.", reply_markup=main_menu_kb())

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data

    if data == CB_BACK:
        await show_main_menu(update, context)
        return

    if data == CB_BALANCE:
        await on_balance(update, context); return

    if data == CB_HISTORY:
        await on_history(update, context); return

    if data == CB_INFO:
        await on_info(update, context); return

    if data == CB_HELP:
        await on_help(update, context); return

    if data == CB_INVEST:
        return await start_invest(update, context)

    if data == CB_WITHDRAW:
        return await start_withdraw(update, context)

    if data == CB_SETTINGS:
        return await open_settings(update, context)

    if data in (CB_SET_WALLET, CB_CHANGE_WALLET):
        return await ask_wallet(update, context)

    if data in (CB_NETWORK_TRC20, CB_NETWORK_ERC20, CB_NETWORK_BEP20):
        return await capture_network(update, context)

    if data.startswith(CB_ADMIN_APPROVE_DEPOSIT) or data.startswith(CB_ADMIN_REJECT_DEPOSIT) or \       data.startswith(CB_ADMIN_APPROVE_WITHDRAW) or data.startswith(CB_ADMIN_REJECT_WITHDRAW):
        await handle_admin_action(update, context); return

async def handle_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.callback_query.answer("Not allowed.", show_alert=True); return

    parts = update.callback_query.data.split(":")
    action = parts[0]; tg_id = int(parts[1]); amount = float(parts[2])
    db_user = get_user_by_tg(tg_id)
    if not db_user:
        await update.callback_query.answer("User not found.", show_alert=True); return

    if action == CB_ADMIN_APPROVE_DEPOSIT:
        add_transaction(db_user["id"], TX_DEPOSIT, amount, ST_APPROVED)
        await context.bot.send_message(chat_id=tg_id, text="Your deposit is approved and in process.")
        await update.callback_query.answer("Deposit approved."); return

    if action == CB_ADMIN_REJECT_DEPOSIT:
        add_transaction(db_user["id"], TX_REJECT, amount, ST_REJECTED)
        await context.bot.send_message(chat_id=tg_id, text="Deposit rejected. Contact @AiCrypto_Support1")
        await update.callback_query.answer("Deposit rejected."); return

    if action == CB_ADMIN_APPROVE_WITHDRAW:
        add_transaction(db_user["id"], TX_WITHDRAW, amount, ST_PAID)
        await context.bot.send_message(chat_id=tg_id, text="Withdrawal paid.")
        await update.callback_query.answer("Withdrawal approved and paid."); return

    if action == CB_ADMIN_REJECT_WITHDRAW:
        move_between_balances(tg_id, "in_process", "balance", amount)
        add_transaction(db_user["id"], TX_WITHDRAW, amount, ST_REJECTED, admin_note="Rejected")
        await context.bot.send_message(chat_id=tg_id, text="Withdrawal rejected. Reason provided by admin.")
        await update.callback_query.answer("Withdrawal rejected."); return

async def daily_profit_job(context: ContextTypes.DEFAULT_TYPE):
    from .db import get_conn
    conn = get_conn()
    cur = conn.execute("SELECT * FROM users")
    users = cur.fetchall()
    for u in users:
        total_base = float(u["balance"]) + float(u["in_process"])
        if total_base <= 0: continue
        profit = total_base * DAILY_PROFIT_RATE
        conn.execute("UPDATE users SET balance = balance + ?, daily_profit = daily_profit + ?, total_profit = total_profit + ? WHERE id = ?",
                     (profit, profit, profit, u["id"]))
        conn.execute("INSERT INTO transactions (user_id, type, amount, status) VALUES (?, ?, ?, ?)",
                     (u["id"], TX_PROFIT, profit, ST_CREDITED))
    conn.commit(); conn.close()

async def reset_daily_profit_job(context: ContextTypes.DEFAULT_TYPE):
    from .db import get_conn
    conn = get_conn()
    conn.execute("UPDATE users SET daily_profit = 0")
    conn.commit(); conn.close()

def build_app():
    if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN is not set.")
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button))

    invest_conv = ConversationHandler(
        entry_points=[],
        states={
            ASK_DEPOSIT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, deposit_amount)],
            AWAIT_DEPOSIT_PROOF: [
                MessageHandler(filters.PHOTO, deposit_proof),
                MessageHandler(filters.TEXT & ~filters.COMMAND, deposit_proof),
            ],
        },
        fallbacks=[],
        map_to_parent={},
    ); app.add_handler(invest_conv)

    withdraw_conv = ConversationHandler(
        entry_points=[],
        states={
            ASK_WITHDRAW_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_amount)],
        },
        fallbacks=[],
        map_to_parent={},
    ); app.add_handler(withdraw_conv)

    settings_conv = ConversationHandler(
        entry_points=[],
        states={
            ASK_WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, capture_wallet)],
            ASK_NETWORK: [CallbackQueryHandler(capture_network)],
        },
        fallbacks=[],
        map_to_parent={},
    ); app.add_handler(settings_conv)

    job_queue = app.job_queue
    job_queue.run_daily(daily_profit_job, time=time_at_utc(0, 0))
    job_queue.run_daily(reset_daily_profit_job, time=time_at_utc(0, 5))
    return app

def time_at_utc(hour: int, minute: int):
    from datetime import time, timezone
    return time(hour=hour, minute=minute, tzinfo=timezone.utc)

def main():
    app = build_app()
    logger.info("Application built. Starting polling.")
    app.run_polling(allowed_updates=None)

if __name__ == "__main__":
    main()
