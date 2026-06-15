from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery
from data.texts import *
from data.keyboards import *

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(MENU, reply_markup=menu_kb())

# ==================== ГРУППОВЫЕ КОМАНДЫ ====================
@router.message(Command("numbers"))
async def cmd_numbers(message: Message, command: CommandObject):
    """Взять номера в чате: /numbers A"""
    args = command.args
    if not args:
        await message.reply("❌ Укажите список: /numbers A")
        return
    
    letter = args.strip().upper()
    if letter not in "ABCDEFGHIJ":
        await message.reply("❌ Неверный список. Доступны: A, B, C, D, E, F, G, H, I, J")
        return
    
    from data.numbers_db import get_random_numbers, PENDING_NUMBERS
    numbers = get_random_numbers(letter, 5)  # В чат выдаём по 5 номеров
    
    if not numbers:
        await message.reply(f"❌ В списке {letter} нет доступных номеров.")
        return
    
    text = f"📱 <b>НОМЕРА (Список {letter}):</b>\n\n"
    for i, num in enumerate(numbers, 1):
        beeline = "✅" if __import__('data.numbers_db').is_beeline(num) else "❌"
        text += f"{i}. {num} {beeline}\n"
    
    text += f"\n{DISCLAIMER}"
    await message.reply(text)

@router.message(Command("addnums"))
async def cmd_addnums(message: Message, command: CommandObject):
    """Добавить номера в чате: /addnums A номер1 номер2..."""
    args = command.args
    if not args:
        await message.reply("❌ Формат: /addnums A +7 999 111-22-33, +7 999 111-22-34")
        return
    
    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("❌ Формат: /addnums A +7 999 111-22-33, +7 999 111-22-34")
        return
    
    letter = parts[0].strip().upper()
    nums_str = parts[1]
    
    # Разделяем по запятым или пробелам
    import re
    numbers = re.split(r'[,;\n]+', nums_str)
    numbers = [n.strip() for n in numbers if n.strip()]
    
    if not numbers:
        await message.reply("❌ Не указаны номера.")
        return
    
    from data.numbers_db import add_numbers
    add_numbers(letter, numbers)
    await message.reply(f"✅ Добавлено {len(numbers)} номеров в список {letter}!")

@router.message(Command("lists"))
async def cmd_lists(message: Message):
    """Показать все списки и количество номеров"""
    from data.numbers_db import ALL_NUMBERS, USED_NUMBERS
    text = "📁 <b>СПИСКИ НОМЕРОВ:</b>\n\n"
    for letter in "ABCDEFGHIJ":
        total = len(ALL_NUMBERS.get(letter, []))
        used = len(USED_NUMBERS.get(letter, []))
        text += f"📁 {letter}: {total} всего, {total-used} доступно\n"
    await message.reply(text)

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = """📋 <b>КОМАНДЫ В ЧАТЕ:</b>

/numbers A — взять 5 номеров из списка A
/addnums A номер1, номер2 — добавить номера в список A
/lists — показать все списки
/help — эта справка"""
    await message.reply(text)

@router.callback_query(F.data == "menu")
async def menu(call: CallbackQuery):
    await call.message.edit_text(MENU, reply_markup=menu_kb())
    await call.answer()

@router.callback_query(F.data == "instruction")
async def instruction(call: CallbackQuery):
    await call.message.edit_text(INSTRUCTION, reply_markup=back_menu_kb())
    await call.answer()

@router.callback_query(F.data == "support")
async def support(call: CallbackQuery):
    await call.message.edit_text(SUPPORT, reply_markup=back_menu_kb())
    await call.answer()

@router.callback_query(F.data == "start_work")
async def start_work(call: CallbackQuery):
    await call.message.edit_text("📁 <b>ВЫБЕРИТЕ СПИСОК:</b>", reply_markup=lists_kb())
    await call.answer()
