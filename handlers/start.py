from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

import database
import keyboards as kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await database.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    text = f"👋 Welcome to GlowUp Center, {message.from_user.first_name}!\n\nHere you'll find exclusive beauty & glow-up instructions.\n\nChoose an option below:"
    await message.answer(text, reply_markup=kb.main_menu())

@router.callback_query(F.data == "main")
async def back_main(call: CallbackQuery):
    text = f"👋 Welcome to GlowUp Center, {call.from_user.first_name}!\n\nChoose an option below:"
    await call.message.edit_text(text, reply_markup=kb.main_menu())
    await call.answer()

@router.callback_query(F.data == "info")
async def info(call: CallbackQuery):
    text = "ℹ️ GlowUp Center\n\nDigital instructions for your glow-up journey.\n\nAll purchases are final. Access is granted instantly after successful payment."
    await call.message.edit_text(text, reply_markup=kb.back_to_main())
    await call.answer()
