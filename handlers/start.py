from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from data.texts import *
from data.keyboards import *

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(MENU, reply_markup=menu_kb())

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