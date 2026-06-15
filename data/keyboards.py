from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

def menu_kb():
    b = InlineKeyboardBuilder()
    b.add(InlineKeyboardButton(text="📋 ИНСТРУКЦИЯ", callback_data="instruction"))
    b.add(InlineKeyboardButton(text="📞 ПОДДЕРЖКА", callback_data="support"))
    b.add(InlineKeyboardButton(text="🚀 НАЧАТЬ РАБОТУ", callback_data="start_work"))
    b.adjust(1)
    return b.as_markup()

def lists_kb():
    b = InlineKeyboardBuilder()
    for letter in "ABCDEFGHIJ":
        b.add(InlineKeyboardButton(text=f"📁 Список {letter}", callback_data=f"list_{letter}"))
    b.add(InlineKeyboardButton(text="◀️ НАЗАД", callback_data="menu"))
    b.adjust(2)
    return b.as_markup()

def list_actions_kb(letter: str):
    b = InlineKeyboardBuilder()
    b.add(InlineKeyboardButton(text="📱 ВЗЯТЬ НОМЕРА", callback_data=f"take_{letter}"))
    b.add(InlineKeyboardButton(text="➕ ДОБАВИТЬ НОМЕРА", callback_data=f"add_{letter}"))
    b.add(InlineKeyboardButton(text="◀️ НАЗАД", callback_data="start_work"))
    b.adjust(1)
    return b.as_markup()

def number_nav_kb(letter: str, index: int, total: int):
    b = InlineKeyboardBuilder()
    b.add(InlineKeyboardButton(text=f"📱 {index+1}/{total}", callback_data="noop"))
    row = []
    if index > 0:
        row.append(InlineKeyboardButton(text="◀️ НАЗАД", callback_data=f"nav_{letter}_{index-1}"))
    row.append(InlineKeyboardButton(text="❌ НЕ БИЛАЙН", callback_data=f"notbeeline_{letter}_{index}"))
    row.append(InlineKeyboardButton(text="⚠️ ЛИМИТ", callback_data=f"limit_{letter}_{index}"))
    if index < total - 1:
        row.append(InlineKeyboardButton(text="ВПЕРЁД ▶️", callback_data=f"nav_{letter}_{index+1}"))
    b.row(*row)
    b.add(InlineKeyboardButton(text="◀️ К СПИСКУ", callback_data=f"list_{letter}"))
    b.adjust(1)
    return b.as_markup()

def back_menu_kb():
    b = InlineKeyboardBuilder()
    b.add(InlineKeyboardButton(text="◀️ В МЕНЮ", callback_data="menu"))
    return b.as_markup()