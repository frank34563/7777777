from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .constants import (
    CB_BALANCE, CB_INVEST, CB_WITHDRAW, CB_HISTORY, CB_SETTINGS, CB_INFO, CB_HELP, CB_BACK,
    CB_SET_WALLET, CB_CHANGE_WALLET,
    CB_NETWORK_TRC20, CB_NETWORK_ERC20, CB_NETWORK_BEP20,
    SUPPORT_HANDLE,
)

BTN_BALANCE = "Balance"
BTN_INVEST = "Invest"
BTN_WITHDRAW = "Withdraw"
BTN_HISTORY = "History"
BTN_SETTINGS = "Settings"
BTN_INFO = "Information"
BTN_HELP = "Help"
BTN_BACK = "Back"

def main_menu_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(BTN_BALANCE, callback_data=CB_BALANCE),
         InlineKeyboardButton(BTN_INVEST, callback_data=CB_INVEST)],
        [InlineKeyboardButton(BTN_WITHDRAW, callback_data=CB_WITHDRAW),
         InlineKeyboardButton(BTN_HISTORY, callback_data=CB_HISTORY)],
        [InlineKeyboardButton(BTN_SETTINGS, callback_data=CB_SETTINGS),
         InlineKeyboardButton(BTN_INFO, callback_data=CB_INFO)],
        [InlineKeyboardButton(BTN_HELP, callback_data=CB_HELP),
         InlineKeyboardButton(BTN_BACK, callback_data=CB_BACK)],
    ]
    return InlineKeyboardMarkup(rows)

def submenu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(BTN_BACK, callback_data=CB_BACK)]])

def settings_kb(wallet_is_set: bool) -> InlineKeyboardMarkup:
    if wallet_is_set:
        rows = [
            [InlineKeyboardButton("Set Wallet", callback_data=CB_SET_WALLET),
             InlineKeyboardButton("Change Wallet", callback_data=CB_CHANGE_WALLET)],
            [InlineKeyboardButton(BTN_BACK, callback_data=CB_BACK)],
        ]
    else:
        rows = [
            [InlineKeyboardButton("Set Wallet", callback_data=CB_SET_WALLET)],
            [InlineKeyboardButton(BTN_BACK, callback_data=CB_BACK)],
        ]
    return InlineKeyboardMarkup(rows)

def networks_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("TRON TRC20", callback_data=CB_NETWORK_TRC20)],
        [InlineKeyboardButton("Ethereum ERC20", callback_data=CB_NETWORK_ERC20)],
        [InlineKeyboardButton("BSC BEP20", callback_data=CB_NETWORK_BEP20)],
    ]
    return InlineKeyboardMarkup(rows)

def help_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Message {SUPPORT_HANDLE}", url=f"https://t.me/{SUPPORT_HANDLE[1:]}")],
        [InlineKeyboardButton(BTN_BACK, callback_data=CB_BACK)],
    ])
