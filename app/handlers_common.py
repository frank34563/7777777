# app/handlers_common.py

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from .constants import (
    CB_BACK,
    ADMIN_ID,
)
from .db import get_user_by_tg
from .keyboards import main_menu_kb  # fixed to relative import

logger = logging.getLogger(__name__)

MAIN_MENU_TEXT = (
    "AiCrypto Investment Bot\n\n"
    "Use the menu buttons below."
)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Always use this helper to render the main menu inside the chat.
    If called from a callback button, try editing the existing message.
    If Telegram reports the message is not modified, just acknowledge the callback.
    If called from a normal message, send a fresh message.
    """
    kb = main_menu_kb()
    try:
        if update.callback_query:
            # Called from a button tap
            await update.callback_query.edit_message_text(
                text=MAIN_MENU_TEXT,
                reply_markup=kb
            )
            await update.callback_query.answer()
        else:
            # Called from a command or plain message
            await update.effective_message.reply_text(
                text=MAIN_MENU_TEXT,
                reply_markup=kb
            )
    except BadRequest as e:
        # Typical case, Message is not modified
        if "Message is not modified" in str(e):
            if update.callback_query:
                await update.callback_query.answer()
            return
        raise

def _fmt_balance(db_user) -> str:
    if not db_user:
        return "Balance\n\nYour Balance: 0$\nBalance in process: 0$\nDaily Profit: 0$\nTotal Profit: 0$\n\nYour personal manager: @AiCrypto_Support1"
    return (
        "Balance\n\n"
        f"Your Balance: {db_user['balance']:.2f}$\n"
        f"Balance in process: {db_user['in_process']:.2f}$\n"
        f"Daily Profit: {db_user['daily_profit']:.2f}$\n"
        f"Total Profit: {db_user['total_profit']:.2f}$\n\n"
        "Your personal manager: @AiCrypto_Support1"
    )

async def on_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    db_user = get_user_by_tg(tg_id)
    text = _fmt_balance(db_user)

    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(text=text, reply_markup=main_menu_kb())
            await update.callback_query.answer()
        else:
            await update.effective_message.reply_text(text=text, reply_markup=main_menu_kb())
    except BadRequest as e:
        if "Message is not modified" in str(e):
            if update.callback_query:
                await update.callback_query.answer()
            return
        raise

async def on_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Minimal placeholder, your history renderer may be elsewhere
    text = "Transaction History\n\nNo records yet."
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(text=text, reply_markup=main_menu_kb())
            await update.callback_query.answer()
        else:
            await update.effective_message.reply_text(text=text, reply_markup=main_menu_kb())
    except BadRequest as e:
        if "Message is not modified" in str(e):
            if update.callback_query:
                await update.callback_query.answer()
            return
        raise

async def on_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "AiCrypto Investment Bot\n\n"
        "Earn passive income with AI powered crypto strategies.\n\n"
        "Minimum Deposit: 10 USDT\n"
        "Daily Profit: 1.5 percent on all deposited amounts\n"
        "Funds Secured via Smart Contracts\n"
        "Support, 24, 7\n\n"
        "Start small, grow big. Your financial future begins now.\n\n"
        "Contact: @AiCrypto_Support1"
    )
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(text=text, reply_markup=main_menu_kb())
            await update.callback_query.answer()
        else:
            await update.effective_message.reply_text(text=text, reply_markup=main_menu_kb())
    except BadRequest as e:
        if "Message is not modified" in str(e):
            if update.callback_query:
                await update.callback_query.answer()
            return
        raise

async def on_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Need help, Chat with your personal manager,\n\n"
        "Message @AiCrypto_Support1"
    )
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(text=text, reply_markup=main_menu_kb())
            await update.callback_query.answer()
        else:
            await update.effective_message.reply_text(text=text, reply_markup=main_menu_kb())
    except BadRequest as e:
        if "Message is not modified" in str(e):
            if update.callback_query:
                await update.callback_query.answer()
            return
        raise
