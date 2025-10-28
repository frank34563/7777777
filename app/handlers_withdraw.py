from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from .db import get_or_create_user, add_transaction, move_between_balances
from .constants import (
    CB_ADMIN_APPROVE_WITHDRAW, CB_ADMIN_REJECT_WITHDRAW,
    ADMIN_ID,
)
from .keyboards import submenu_kb

ASK_WITHDRAW_AMOUNT = 2001

def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except Exception:
        return False

async def start_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_user = get_or_create_user(update.effective_user.id)
    if not db_user["wallet"]:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "You must set your withdrawal wallet first.\nGo to Settings, Set Wallet.",
            reply_markup=submenu_kb()
        )
        return ConversationHandler.END

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        f"Enter withdrawal amount.\nAvailable: {db_user['balance']:.2f}$",
        reply_markup=submenu_kb()
    )
    return ASK_WITHDRAW_AMOUNT

async def withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_user = get_or_create_user(update.effective_user.id)
    text = update.message.text.strip()
    if not is_number(text):
        await update.message.reply_text("Amount must be a number. Try again.", reply_markup=submenu_kb())
        return ASK_WITHDRAW_AMOUNT
    amount = float(text)
    if amount <= 0 or amount > db_user["balance"]:
        await update.message.reply_text("Invalid amount. Check your available balance.", reply_markup=submenu_kb())
        return ASK_WITHDRAW_AMOUNT

    move_between_balances(db_user["tg_id"], "balance", "in_process", amount)

    add_transaction(
        user_id=db_user["id"],
        tx_type="withdraw",
        amount=amount,
        status="pending",
        wallet=db_user["wallet"],
        network=db_user["network"],
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Pay and Approve", callback_data=f"{CB_ADMIN_APPROVE_WITHDRAW}:{db_user['tg_id']}:{amount}")],
        [InlineKeyboardButton("Reject with Note", callback_data=f"{CB_ADMIN_REJECT_WITHDRAW}:{db_user['tg_id']}:{amount}")],
    ])
    admin_text = (
        "Withdrawal request\n"
        f"User: {update.effective_user.full_name} id {db_user['tg_id']}\n"
        f"Amount: {amount:.2f} USDT\n"
        f"Wallet: {db_user['wallet']} {db_user['network']}\n"
        "Status: Pending"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=kb)
    except Exception:
        pass

    await update.message.reply_text(
        "Withdrawal Request Submitted\n"
        f"Amount: {amount:.2f} USDT\n"
        f"Wallet: {db_user['wallet']} {db_user['network']}\n"
        "Status: Pending Approval\n\n"
        "Funds moved to Balance in process.",
        reply_markup=submenu_kb()
    )
    return ConversationHandler.END

async def cancel_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.", reply_markup=submenu_kb())
    return ConversationHandler.END
