# app/utils.py
from typing import Optional
from telegram import InlineKeyboardMarkup
from telegram.error import BadRequest

def _serialize_markup(markup: Optional[InlineKeyboardMarkup]) -> str:
    if not markup:
        return ""
    try:
        data = markup.to_dict()
    except Exception:
        return ""
    # Keep only fields that matter for equality
    rows = []
    for row in data.get("inline_keyboard", []):
        row_norm = []
        for btn in row:
            row_norm.append((
                btn.get("text", ""),
                btn.get("callback_data", ""),
                btn.get("url", ""),
                btn.get("switch_inline_query", ""),
                btn.get("switch_inline_query_current_chat", ""),
            ))
        rows.append(tuple(row_norm))
    return str(tuple(rows))

async def safe_edit_message_text(
    query,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = None,
):
    """
    Edits the callback message only if something actually changed.
    Silently ignores the Telegram, message is not modified, error.
    """
    msg = query.message
    current_text = msg.text or ""
    current_markup = msg.reply_markup

    same_text = current_text == text
    same_markup = _serialize_markup(current_markup) == _serialize_markup(reply_markup)

    if same_text and same_markup:
        # Nothing to change, just answer the callback and return
        try:
            await query.answer()
        except Exception:
            pass
        return

    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    except BadRequest as e:
        # The most common case is the same content, which we already guarded, but keep this robust
        if "message is not modified" in str(e).lower():
            try:
                await query.answer()
            except Exception:
                pass
        else:
            raise
