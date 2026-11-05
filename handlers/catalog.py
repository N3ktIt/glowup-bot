from aiogram import Router, F
from aiogram.types import CallbackQuery

import database
import keyboards as kb
from texts import t
from keyboards import get_title

router = Router()

def get_field(instr, field, lang):
    if lang == 'ru':
        return instr.get(f'{field}_ru') or instr.get(f'{field}_en') or instr.get(field) or ''
    return instr.get(f'{field}_en') or instr.get(f'{field}_ru') or instr.get(field) or ''

@router.callback_query(F.data == "catalog")
async def show_catalog(call: CallbackQuery):
    lang = await database.get_user_lang(call.from_user.id)
    instructions = await database.get_instructions()
    if not instructions:
        await call.message.edit_text(t(lang, 'catalog_empty'), reply_markup=kb.back_to_main(lang))
        await call.answer()
        return
    await call.message.edit_text(t(lang, 'choose_instruction'), reply_markup=kb.catalog_kb(instructions, lang))
    await call.answer()

@router.callback_query(F.data.startswith("view_"))
async def view_instruction(call: CallbackQuery):
    lang = await database.get_user_lang(call.from_user.id)
    instr_id = int(call.data.split("_")[1])
    instr = await database.get_instruction(instr_id)
    if not instr:
        await call.answer(t(lang, 'not_found'), show_alert=True)
        return
    has_access = await database.has_access(call.from_user.id, instr_id)
    title = get_title(instr, lang)
    desc = get_field(instr, 'description', lang) or ('Glow-up instructions pack.' if lang == 'en' else 'Инструкция по улучшению внешности.')
    text = f"📦 {title}\n\n{desc}\n\n{t(lang, 'price')}: ${instr['price']:.2f}"
    await call.message.edit_text(text, reply_markup=kb.instruction_kb(instr_id, has_access, lang))
    await call.answer()

@router.callback_query(F.data.startswith("read_"))
async def read_instruction(call: CallbackQuery):
    lang = await database.get_user_lang(call.from_user.id)
    instr_id = int(call.data.split("_")[1])
    has_access = await database.has_access(call.from_user.id, instr_id)
    if not has_access:
        await call.answer(t(lang, 'no_access'), show_alert=True)
        return
    instr = await database.get_instruction(instr_id)
    title = get_title(instr, lang)
    content = get_field(instr, 'content', lang) or ('Content will be added soon.' if lang == 'en' else 'Контент скоро будет добавлен.')
    text = f"📖 {title}\n\n{content}"
    # Telegram message limit handling: split if too long? For now just send
    if len(text) > 4000:
        await call.message.edit_text(text[:4000], reply_markup=kb.back_to_main(lang))
    else:
        await call.message.edit_text(text, reply_markup=kb.back_to_main(lang))
    await call.answer()

@router.callback_query(F.data == "my_access")
async def my_access(call: CallbackQuery):
    lang = await database.get_user_lang(call.from_user.id)
    instructions = await database.get_instructions()
    owned = []
    for instr in instructions:
        if await database.has_access(call.from_user.id, instr['id']):
            owned.append(instr)
    if not owned:
        await call.message.edit_text(f"{t(lang, 'your_access')}\n\n{t(lang, 'no_purchases')}", reply_markup=kb.back_to_main(lang))
        await call.answer()
        return
    text = f"{t(lang, 'your_access')}\n\n{t(lang, 'you_have_access')}"
    for o in owned:
        text += f"\n• {get_title(o, lang)}"
    text += f"\n\n{t(lang, 'go_to_catalog')}"
    await call.message.edit_text(text, reply_markup=kb.back_to_main(lang))
    await call.answer()
