from aiogram import Router, F
from aiogram.types import CallbackQuery

import database
import keyboards as kb

router = Router()

@router.callback_query(F.data == "catalog")
async def show_catalog(call: CallbackQuery):
    instructions = await database.get_instructions()
    if not instructions:
        text = "📚 Catalog is empty at the moment.\n\nNew instructions coming soon!"
        await call.message.edit_text(text, reply_markup=kb.back_to_main())
        await call.answer()
        return
    text = "📚 Choose an instruction pack:"
    await call.message.edit_text(text, reply_markup=kb.catalog_kb(instructions))
    await call.answer()

@router.callback_query(F.data.startswith("view_"))
async def view_instruction(call: CallbackQuery):
    instr_id = int(call.data.split("_")[1])
    instr = await database.get_instruction(instr_id)
    if not instr:
        await call.answer("Instruction not found", show_alert=True)
        return
    has_access = await database.has_access(call.from_user.id, instr_id)
    text = f"📦 {instr['title']}\n\n{instr['description'] or 'Glow-up instructions pack.'}\n\nPrice: ${instr['price']:.2f}"
    await call.message.edit_text(text, reply_markup=kb.instruction_kb(instr_id, has_access))
    await call.answer()

@router.callback_query(F.data.startswith("read_"))
async def read_instruction(call: CallbackQuery):
    instr_id = int(call.data.split("_")[1])
    has_access = await database.has_access(call.from_user.id, instr_id)
    if not has_access:
        await call.answer("You don't have access to this", show_alert=True)
        return
    instr = await database.get_instruction(instr_id)
    text = f"📖 {instr['title']}\n\n{instr['content'] or 'Content will be added soon.'}"
    await call.message.edit_text(text, reply_markup=kb.back_to_main())
    await call.answer()

@router.callback_query(F.data == "my_access")
async def my_access(call: CallbackQuery):
    instructions = await database.get_instructions()
    owned = []
    for instr in instructions:
        if await database.has_access(call.from_user.id, instr['id']):
            owned.append(instr)
    if not owned:
        text = "💼 Your Access\n\nYou haven't purchased any instructions yet.\n\nCheck the catalog to get started!"
        await call.message.edit_text(text, reply_markup=kb.back_to_main())
        await call.answer()
        return
    text = "💼 Your Access\n\nYou have access to:"
    for o in owned:
        text += f"\n• {o['title']}"
    text += "\n\nGo to catalog and click 'View Instructions' to read."
    await call.message.edit_text(text, reply_markup=kb.back_to_main())
    await call.answer()
