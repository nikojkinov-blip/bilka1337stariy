from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data.texts import DISCLAIMER
from data.keyboards import *
from data.numbers_db import *

router = Router()

class AddNums(StatesGroup):
    waiting = State()

@router.callback_query(F.data.startswith("list_"))
async def show_list(call: CallbackQuery):
    letter = call.data.split("_")[1]
    total = len(ALL_NUMBERS.get(letter, []))
    used = len(USED_NUMBERS.get(letter, []))
    await call.message.edit_text(
        f"📁 <b>СПИСОК {letter}</b>\n\n📱 Всего: {total}\n✅ Доступно: {total - used}",
        reply_markup=list_actions_kb(letter)
    )
    await call.answer()

@router.callback_query(F.data.startswith("take_"))
async def take_numbers(call: CallbackQuery):
    letter = call.data.split("_")[1]
    numbers = get_random_numbers(letter, 20)
    if not numbers:
        await call.message.edit_text("❌ Нет доступных номеров.", reply_markup=list_actions_kb(letter))
        return
    await show_number(call.message, letter, 0, edit=True)

async def show_number(message_or_call, letter, index, edit=False):
    numbers = PENDING_NUMBERS.get(letter, [])
    total = len(numbers)
    if not numbers:
        text = "📋 Номера закончились."
        kb = list_actions_kb(letter)
        if edit:
            await message_or_call.edit_text(text, reply_markup=kb)
        else:
            await message_or_call.answer(text, reply_markup=kb)
        return
    
    number = numbers[index]
    beeline = is_beeline(number)
    
    # Кнопка копирования
    copy_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📋 КОПИРОВАТЬ {number}", callback_data=f"copy_{number}")]
    ])
    
    text = (
        f"{DISCLAIMER}\n\n"
        f"📱 <b>Список {letter}</b>\n"
        f"┌─────────────────────┐\n"
        f"│  {number}  │\n"
        f"└─────────────────────┘\n"
        f"{'✅ Билайн' if beeline else '❌ Не Билайн'}"
    )
    
    nav_kb = number_nav_kb(letter, index, total)
    
    # Объединяем клавиатуры
    builder = InlineKeyboardBuilder()
    builder.attach(InlineKeyboardBuilder.from_markup(copy_kb))
    builder.attach(InlineKeyboardBuilder.from_markup(nav_kb))
    
    if edit:
        await message_or_call.edit_text(text, reply_markup=builder.as_markup())
    else:
        await message_or_call.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("copy_"))
async def copy_number(call: CallbackQuery):
    number = call.data.replace("copy_", "")
    await call.answer(f"📋 {number}", show_alert=True)

@router.callback_query(F.data.startswith("nav_"))
async def navigate(call: CallbackQuery):
    _, letter, idx = call.data.split("_")
    await show_number(call.message, letter, int(idx), edit=True)
    await call.answer()

@router.callback_query(F.data.startswith("notbeeline_"))
async def not_beeline(call: CallbackQuery):
    _, letter, idx = call.data.split("_")
    remove_number(letter, int(idx))
    numbers = PENDING_NUMBERS.get(letter, [])
    if numbers:
        new_idx = min(int(idx), len(numbers)-1)
        await show_number(call.message, letter, new_idx, edit=True)
    else:
        await call.message.edit_text("📋 Номера закончились.", reply_markup=list_actions_kb(letter))
    await call.answer("❌ Не Билайн — убран")

@router.callback_query(F.data.startswith("limit_"))
async def limit(call: CallbackQuery):
    _, letter, idx = call.data.split("_")
    remove_number(letter, int(idx))
    numbers = PENDING_NUMBERS.get(letter, [])
    if numbers:
        new_idx = min(int(idx), len(numbers)-1)
        await show_number(call.message, letter, new_idx, edit=True)
    else:
        await call.message.edit_text("📋 Номера закончились.", reply_markup=list_actions_kb(letter))
    await call.answer("⚠️ Лимит — убран")

@router.callback_query(F.data == "noop")
async def noop(call: CallbackQuery):
    await call.answer()

@router.callback_query(F.data.startswith("add_"))
async def add_start(call: CallbackQuery, state: FSMContext):
    letter = call.data.split("_")[1]
    await state.update_data(letter=letter)
    await state.set_state(AddNums.waiting)
    await call.message.edit_text(
        f"➕ <b>ДОБАВИТЬ В СПИСОК {letter}</b>\n\nОтправьте номера (каждый с новой строки):",
        reply_markup=InlineKeyboardBuilder().button(text="◀️ ОТМЕНА", callback_data=f"list_{letter}").as_markup()
    )
    await call.answer()

@router.message(AddNums.waiting)
async def add_process(message: Message, state: FSMContext):
    data = await state.get_data()
    letter = data['letter']
    new = [n.strip() for n in message.text.split("\n") if n.strip()]
    add_numbers(letter, new)
    await state.clear()
    await message.answer(f"✅ Добавлено {len(new)} номеров в список {letter}!", reply_markup=list_actions_kb(letter))
