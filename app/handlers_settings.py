from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from .db import get_or_create_user, update_user_wallet
from .keyboards import settings_kb, networks_kb, submenu_kb
from .constants import CB_SET_WALLET, CB_CHANGE_WALLET, CB_NETWORK_TRC20, CB_NETWORK_ERC20, CB_NETWORK_BEP20

ASK_WALLET = 3001
ASK_NETWORK = 3002

async def open_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_or_create_user(update.effective_user.id)
    w = u["wallet"] or "Not set"
    text = f"Settings\n\nWithdrawal Wallet: {w}"
    await update.callback_query.edit_message_text(text, reply_markup=settings_kb(wallet_is_set=bool(u["wallet"])))
    await update.callback_query.answer()

async def ask_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "Send your withdrawal wallet address.\nExample: TAbc123...xyz789",
        reply_markup=submenu_kb()
    )
    return ASK_WALLET

async def capture_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    addr = update.message.text.strip()
    if len(addr) < 10:
        await update.message.reply_text("Wallet looks invalid. Send again.", reply_markup=submenu_kb())
        return ASK_WALLET
    context.user_data["pending_wallet"] = addr
    await update.message.reply_text("Select network.", reply_markup=networks_kb())
    return ASK_NETWORK

async def capture_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    net_map = {
        CB_NETWORK_TRC20: "TRC20",
        CB_NETWORK_ERC20: "ERC20",
        CB_NETWORK_BEP20: "BEP20",
    }
    network = net_map.get(q.data)
    addr = context.user_data.get("pending_wallet")
    if not addr or not network:
        await q.edit_message_text("Something went wrong. Try again.", reply_markup=submenu_kb())
        return ConversationHandler.END

    update_user_wallet(update.effective_user.id, addr, network)
    await q.edit_message_text(f"Wallet saved.\n{addr} {network}", reply_markup=submenu_kb())
    return ConversationHandler.END

async def cancel_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.", reply_markup=submenu_kb())
    return ConversationHandler.END
