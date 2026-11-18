from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from handwriting.style import STYLES


def style_keyboard() -> InlineKeyboardMarkup:
    rows = []
    for key, style in STYLES.items():
        rows.append([InlineKeyboardButton(text=style.name, callback_data=f"style:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
