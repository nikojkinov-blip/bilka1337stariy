from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery
from data.texts import *
from data.keyboards import *
from data.numbers_db import get_random_numbers, add_numbers, is_beeline, ALL_NUMBERS, USED_NUMBERS

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(MENU, reply_markup=menu_kb())

# ==================== ГРУППОВЫЕ КОМАНДЫ (без спама) ====================
@router.message(Command("num"))
async def cmd_num(message: Message, command: CommandObject):
    """Взять 1 номер: /num A"""
    args = command.args
    if not args:
        await message.reply("❌ /num A", disable_notification=True)
        return
    
    letter = args.strip().upper()
    numbers = get_random_numbers(letter, 1)
    if not numbers:
        await message.reply(f"❌ Список {letter} пуст.", disable_notification=True)
        return
    
    num = numbers[0]
    beeline = "✅" if is_beeline(num) else "❌"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ НЕ БИЛАЙН", callback_data=f"chat_notbeeline_{letter}_0")],
        [InlineKeyboardButton(text="⚠️ ЛИМИТ", callback_data=f"chat_limit_{letter}_0")],
        [InlineKeyboardButton(text=f"📋 КОПИРОВАТЬ {num}", callback_data=f"copy_{num}")],
    ])
    
    await message.reply(
        f"📱 {num} {beeline}",
        reply_markup=kb,
        disable_notification=True
    )

@router.callback_query(F.data.startswith("chat_notbeeline_"))
async def chat_notbeeline(call: CallbackQuery):
    _, letter, idx = call.data.split("_")[2:]
    remove_number(letter, int(idx))
    await call.message.edit_text(call.message.text + "\n❌ Убран")
    await call.answer("❌ Убран")

@router.callback_query(F.data.startswith("chat_limit_"))
async def chat_limit(call: CallbackQuery):
    _, letter, idx = call.data.split("_")[2:]
    remove_number(letter, int(idx))
    await call.message.edit_text(call.message.text + "\n⚠️ Убран")
    await call.answer("⚠️ Убран")

@router.message(Command("addnums"))
async def cmd_addnums(message: Message, command: CommandObject):
    args = command.args
    if not args:
        await message.reply("❌ /addnums A +7999..., +7999...", disable_notification=True)
        return
    
    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("❌ /addnums A +7999..., +7999...", disable_notification=True)
        return
    
    letter = parts[0].strip().upper()
    import re
    numbers = re.split(r'[,;\n]+', parts[1])
    numbers = [n.strip() for n in numbers if n.strip()]
    
    if not numbers:
        await message.reply("❌ Не указаны номера.", disable_notification=True)
        return
    
    add_numbers(letter, numbers)
    await message.reply(f"✅ +{len(numbers)} в {letter}!", disable_notification=True)

@router.message(Command("lists"))
async def cmd_lists(message: Message):
    text = "📁 "
    for letter in "ABCDEFGHIJ":
        total = len(ALL_NUMBERS.get(letter, []))
        used = len(USED_NUMBERS.get(letter, []))
        text += f"{letter}:{total-used}/{total} "
    await message.reply(text, disable_notification=True)

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply("/num A | /addnums A номера | /lists", disable_notification=True)

# ==================== ЛИЧКА ====================
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
