from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from .constants import (
    MIN_DEPOSIT, MAIN_TRC20_WALLET,
    CB_ADMIN_APPROVE_DEPOSIT, CB_ADMIN_REJECT_DEPOSIT, ADMIN_ID,
)
from .db import get_or_create_user, add_transaction
from .keyboards import submenu_kb

ASK_DEPOSIT_AMOUNT = 1001
AWAIT_DEPOSIT_PROOF = 1002

def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except Exception:
        return False

async def start_invest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "Enter the amount you want to invest, minimum 10 USDT.",
        reply_markup=submenu_kb()
    )
    return ASK_DEPOSIT_AMOUNT

async def deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not is_number(text):
        await update.message.reply_text("Amount must be a number. Try again.", reply_markup=submenu_kb())
        return ASK_DEPOSIT_AMOUNT
    amount = float(text)
    if amount < MIN_DEPOSIT:
        await update.message.reply_text(f"Minimum deposit is {MIN_DEPOSIT} USDT. Try again.", reply_markup=submenu_kb())
        return ASK_DEPOSIT_AMOUNT

    context.user_data["invest_amount"] = amount
    info = (
        f"Deposit {amount:.2f} USDT to:\n\n"
        f"Wallet TRC20: {MAIN_TRC20_WALLET}\n"
        "Network: TRON TRC20\n"
        "Expires in 30 minutes\n\n"
        "After payment, send a screenshot of the transaction or the transaction hash."
    )
    await update.message.reply_text(info, reply_markup=submenu_kb())
    return AWAIT_DEPOSIT_PROOF

async def deposit_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_user = get_or_create_user(update.effective_user.id)
    amount = float(context.user_data.get("invest_amount", 0))
    txid = None
    screenshot_file_id = None

    if update.message.photo:
        screenshot_file_id = update.message.photo[-1].file_id
    elif update.message.text:
        txid = update.message.text.strip()

    add_transaction(
        user_id=db_user["id"],
        tx_type="deposit",
        amount=amount,
        status="pending",
        txid=txid,
        wallet=MAIN_TRC20_WALLET,
        network="TRC20",
        screenshot_file_id=screenshot_file_id,
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Approve", callback_data=f"{CB_ADMIN_APPROVE_DEPOSIT}:{db_user['tg_id']}:{amount}")],
        [InlineKeyboardButton("Reject", callback_data=f"{CB_ADMIN_REJECT_DEPOSIT}:{db_user['tg_id']}:{amount}")],
    ])
    admin_text = (
        "Deposit request\n"
        f"User: {update.effective_user.full_name} id {db_user['tg_id']}\n"
        f"Amount: {amount:.2f} USDT\n"
        "Wallet: TRC20\n"
        f"Addr: {MAIN_TRC20_WALLET}\n"
        f"TxID or Note: {txid if txid else 'screenshot attached' }"
    )
    try:
        if screenshot_file_id:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=screenshot_file_id, caption=admin_text, reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=kb)
    except Exception:
        pass

    await update.message.reply_text("Your deposit has been submitted. Await admin approval.", reply_markup=submenu_kb())
    return ConversationHandler.END

async def cancel_invest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.", reply_markup=submenu_kb())
    return ConversationHandler.END
