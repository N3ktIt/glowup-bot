from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

import database
import keyboards as kb
from texts import t

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await database.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    lang = await database.get_user_lang(message.from_user.id)
    text = t(lang, 'welcome', name=message.from_user.first_name)
    await message.answer(text, reply_markup=kb.main_menu(lang))

@router.callback_query(F.data == "main")
async def back_main(call: CallbackQuery):
    lang = await database.get_user_lang(call.from_user.id)
    text = t(lang, 'welcome', name=call.from_user.first_name)
    await call.message.edit_text(text, reply_markup=kb.main_menu(lang))
    await call.answer()

@router.callback_query(F.data == "info")
async def info(call: CallbackQuery):
    lang = await database.get_user_lang(call.from_user.id)
    await call.message.edit_text(t(lang, 'info_text'), reply_markup=kb.back_to_main(lang))
    await call.answer()

@router.callback_query(F.data == "lang")
async def choose_lang(call: CallbackQuery):
    lang = await database.get_user_lang(call.from_user.id)
    await call.message.edit_text(t(lang, 'choose_lang'), reply_markup=kb.lang_kb())
    await call.answer()

@router.callback_query(F.data.startswith("setlang_"))
async def set_lang(call: CallbackQuery):
    new_lang = call.data.split("_")[1]
    await database.set_user_lang(call.from_user.id, new_lang)
    text = t(new_lang, 'welcome', name=call.from_user.first_name)
    await call.message.edit_text(text, reply_markup=kb.main_menu(new_lang))
    await call.answer(t(new_lang, 'lang_set'))
