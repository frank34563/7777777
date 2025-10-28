from telegram import Update
from telegram.ext import ContextTypes
from .keyboards import main_menu_kb, submenu_kb, help_kb
from .db import get_or_create_user, list_transactions
from .constants import SUPPORT_HANDLE

def format_balance_row(u) -> str:
    return (
        "Balance\n\n"
        f"Your Balance: {u['balance']:.2f}$\n"
        f"Balance in process: {u['in_process']:.2f}$\n"
        f"Daily Profit: {u['daily_profit']:.2f}$\n"
        f"Total Profit: {u['total_profit']:.2f}$\n\n"
        f"Your personal manager: {SUPPORT_HANDLE}"
    )

from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_menu_kb
from utils import safe_edit_message_text

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "AiCrypto Investment Bot\n\n"
        "Select an option below."
    )
    if update.callback_query:
        await safe_edit_message_text(update.callback_query, text, reply_markup=main_menu_kb())
    else:
        await update.message.reply_text(text=text, reply_markup=main_menu_kb())


async def on_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(update.effective_user.id)
    text = format_balance_row(user)
    await update.callback_query.edit_message_text(text, reply_markup=submenu_kb())
    await update.callback_query.answer()

async def on_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_user = get_or_create_user(update.effective_user.id)
    rows = list_transactions(db_user["id"], limit=30)
    if not rows:
        text = "Transaction History\nNo transactions yet."
    else:
        lines = ["Transaction History"]
        for r in rows:
            sign = "+" if r["type"] in ("deposit", "profit") else "-"
            lines.append(
                f"{sign} {r['created_at']} | {r['type'].capitalize()} | {r['amount']:.2f}$ | {r['status'].capitalize()}"
            )
        text = "\n".join(lines)
    await update.callback_query.edit_message_text(text, reply_markup=submenu_kb())
    await update.callback_query.answer()

async def on_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "AiCrypto Investment Bot\n\n"
        "Earn passive income with AI powered crypto strategies.\n\n"
        "Minimum Deposit: 10 USDT\n"
        "Daily Profit: 1.5 percent on all deposited amounts\n"
        "Funds secured via smart contracts\n"
        "24 by 7 support\n\n"
        "Start small, grow big. Your financial future begins now.\n\n"
        f"Contact: {SUPPORT_HANDLE}"
    )
    await update.callback_query.edit_message_text(text, reply_markup=submenu_kb())
    await update.callback_query.answer()

async def on_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Need help. Chat with your personal manager."
    await update.callback_query.edit_message_text(text, reply_markup=help_kb())
    await update.callback_query.answer()
