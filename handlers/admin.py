from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import config
import database

router = Router()

class AddInstruction(StatesGroup):
    title_en = State()
    title_ru = State()
    description_en = State()
    description_ru = State()
    price = State()
    content_en = State()
    content_ru = State()

def is_admin(user_id: int) -> bool:
    return user_id == config.ADMIN_ID

@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AddInstruction.title_en)
    await message.answer("Admin: Add instruction\n\nStep 1/7: Title (EN)")

@router.message(AddInstruction.title_en)
async def add_title_en(message: Message, state: FSMContext):
    await state.update_data(title_en=message.text.strip())
    await state.set_state(AddInstruction.title_ru)
    await message.answer("Step 2/7: Title (RU)")

@router.message(AddInstruction.title_ru)
async def add_title_ru(message: Message, state: FSMContext):
    await state.update_data(title_ru=message.text.strip())
    await state.set_state(AddInstruction.description_en)
    await message.answer("Step 3/7: Description (EN)")

@router.message(AddInstruction.description_en)
async def add_desc_en(message: Message, state: FSMContext):
    await state.update_data(description_en=message.text.strip())
    await state.set_state(AddInstruction.description_ru)
    await message.answer("Step 4/7: Description (RU)")

@router.message(AddInstruction.description_ru)
async def add_desc_ru(message: Message, state: FSMContext):
    await state.update_data(description_ru=message.text.strip())
    await state.set_state(AddInstruction.price)
    await message.answer("Step 5/7: Price in USD (number, e.g. 9.99)")

@router.message(AddInstruction.price)
async def add_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", ".").strip())
    except Exception:
        await message.answer("Invalid price. Send a number, e.g. 9.99")
        return
    await state.update_data(price=price)
    await state.set_state(AddInstruction.content_en)
    await message.answer("Step 6/7: Content (EN) - full instruction text")

@router.message(AddInstruction.content_en)
async def add_content_en(message: Message, state: FSMContext):
    await state.update_data(content_en=message.text.strip())
    await state.set_state(AddInstruction.content_ru)
    await message.answer("Step 7/7: Content (RU) - full instruction text")

@router.message(AddInstruction.content_ru)
async def add_content_ru(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await database.add_instruction(
            data['title_en'], data['title_ru'],
            data['description_en'], data['description_ru'],
            data['price'],
            data['content_en'], message.text.strip()
        )
        await state.clear()
        await message.answer("✅ Instruction added!")
    except Exception as e:
        await message.answer(f"❌ Error adding instruction: {e}")
        await state.clear()

@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("Cancelled.")
