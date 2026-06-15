from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message
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
    await show_number(call, letter, 0)

async def show_number(call, letter, index):
    numbers = PENDING_NUMBERS.get(letter, [])
    total = len(numbers)
    if not numbers:
        await call.message.edit_text("📋 Номера закончились.", reply_markup=list_actions_kb(letter))
        return
    number = numbers[index]
    beeline = is_beeline(number)
    await call.message.edit_text(
        f"{DISCLAIMER}\n\n"
        f"📱 <b>Список {letter}</b>\n"
        f"┌─────────────────────┐\n"
        f"│  {number}  │\n"
        f"└─────────────────────┘\n"
        f"{'✅ Билайн' if beeline else '❌ Не Билайн'}",
        reply_markup=number_nav_kb(letter, index, total)
    )

@router.callback_query(F.data.startswith("nav_"))
async def navigate(call: CallbackQuery):
    _, letter, idx = call.data.split("_")
    await show_number(call, letter, int(idx))
    await call.answer()

@router.callback_query(F.data.startswith("notbeeline_"))
async def not_beeline(call: CallbackQuery):
    _, letter, idx = call.data.split("_")
    remove_number(letter, int(idx))
    numbers = PENDING_NUMBERS.get(letter, [])
    if numbers:
        await show_number(call, letter, min(int(idx), len(numbers)-1))
    else:
        await call.message.edit_text("📋 Номера закончились.", reply_markup=list_actions_kb(letter))
    await call.answer("❌ Не Билайн — убран")

@router.callback_query(F.data.startswith("limit_"))
async def limit(call: CallbackQuery):
    _, letter, idx = call.data.split("_")
    remove_number(letter, int(idx))
    numbers = PENDING_NUMBERS.get(letter, [])
    if numbers:
        await show_number(call, letter, min(int(idx), len(numbers)-1))
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