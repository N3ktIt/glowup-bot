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

class EditContent(StatesGroup):
    waiting = State()

def is_admin(user_id: int) -> bool:
    return user_id == config.ADMIN_ID

@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AddInstruction.title_en)
    await message.answer("Admin: Add instruction\n\nStep 1/7: Title (EN)\nSend /cancel to stop.")

@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    current = await state.get_state()
    if current is None:
        return
    await state.clear()
    await message.answer("Cancelled.")

@router.message(Command("purchases"))
async def cmd_purchases(message: Message):
    if not is_admin(message.from_user.id):
        return
    rows = await database.list_purchases(20)
    if not rows:
        await message.answer("No purchases yet.")
        return
    lines = ["🧾 Recent purchases:"]
    for r in rows:
        title = r.get('title_en') or f"Instruction #{r['instruction_id']}"
        status = r['status']
        paid = "✅" if status == 'paid' else "⏳"
        lines.append(f"{paid} #{r['id']} | {title} | ${r['amount']:.2f} | user {r['user_id']} | {status}")
    text = "\n".join(lines)
    if len(text) > 4000:
        text = text[:4000]
    await message.answer(text)

@router.message(Command("instructions"))
async def cmd_instructions(message: Message):
    if not is_admin(message.from_user.id):
        return
    rows = await database.get_instructions()
    if not rows:
        await message.answer("No instructions found.")
        return
    lines = ["📚 Instructions:"]
    for r in rows:
        title = r.get('title_en') or r.get('title') or f"#{r['id']}"
        lines.append(f"#{r['id']} | {title} | ${float(r['price']):.2f}")
    await message.answer("\n".join(lines))

@router.message(Command("delinst"))
async def cmd_delinst(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Usage: /delinst <id>")
        return
    try:
        instr_id = int(parts[1])
    except ValueError:
        await message.answer("Invalid id")
        return
    ok = await database.delete_instruction(instr_id)
    await message.answer("Deleted." if ok else "Not found.")

@router.message(Command("viewinst"))
async def cmd_viewinst(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Usage: /viewinst <id>")
        return
    try:
        instr_id = int(parts[1])
    except ValueError:
        await message.answer("Invalid id")
        return
    instr = await database.get_instruction(instr_id)
    if not instr:
        await message.answer("Not found.")
        return
    def trunc(s, n=800):
        s = s or ''
        return s if len(s) <= n else s[:n] + '\n... [truncated]'
    text = (
        f"#{instr['id']} ${float(instr['price']):.2f}\n\n"
        f"EN title: {instr.get('title_en') or ''}\n"
        f"RU title: {instr.get('title_ru') or ''}\n\n"
        f"EN desc: {trunc(instr.get('description_en'), 200)}\n"
        f"RU desc: {trunc(instr.get('description_ru'), 200)}\n\n"
        f"EN content:\n{trunc(instr.get('content_en'), 900)}\n\n"
        f"RU content:\n{trunc(instr.get('content_ru'), 900)}\n\n"
        f"Edit: /setprice {instr['id']} 9.99 | /settitle {instr['id']} en Title | /setcontent {instr['id']} en"
    )
    if len(text) > 4000:
        text = text[:4000]
    await message.answer(text)

@router.message(Command("setprice"))
async def cmd_setprice(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Usage: /setprice <id> <price>")
        return
    try:
        instr_id = int(parts[1])
        price = float(parts[2].replace(',', '.'))
    except ValueError:
        await message.answer("Invalid id or price")
        return
    instr = await database.get_instruction(instr_id)
    if not instr:
        await message.answer("Not found.")
        return
    await database.update_instruction_field(instr_id, 'price', price)
    await message.answer(f"✅ Price updated for #{instr_id}: ${price:.2f}")

@router.message(Command("settitle"))
async def cmd_settitle(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer("Usage: /settitle <id> <en|ru> <title>")
        return
    try:
        instr_id = int(parts[1])
    except ValueError:
        await message.answer("Invalid id")
        return
    lang = parts[2].lower()
    if lang not in ('en', 'ru'):
        await message.answer("Language must be en or ru")
        return
    value = parts[3].strip()
    instr = await database.get_instruction(instr_id)
    if not instr:
        await message.answer("Not found.")
        return
    field = f"title_{lang}"
    await database.update_instruction_field(instr_id, field, value)
    await message.answer(f"✅ Title ({lang}) updated for #{instr_id}")

@router.message(Command("setdesc"))
async def cmd_setdesc(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer("Usage: /setdesc <id> <en|ru> <description>")
        return
    try:
        instr_id = int(parts[1])
    except ValueError:
        await message.answer("Invalid id")
        return
    lang = parts[2].lower()
    if lang not in ('en', 'ru'):
        await message.answer("Language must be en or ru")
        return
    value = parts[3].strip()
    instr = await database.get_instruction(instr_id)
    if not instr:
        await message.answer("Not found.")
        return
    field = f"description_{lang}"
    await database.update_instruction_field(instr_id, field, value)
    await message.answer(f"✅ Description ({lang}) updated for #{instr_id}")

@router.message(Command("setcontent"))
async def cmd_setcontent(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Usage: /setcontent <id> <en|ru>")
        return
    try:
        instr_id = int(parts[1])
    except ValueError:
        await message.answer("Invalid id")
        return
    lang = parts[2].lower()
    if lang not in ('en', 'ru'):
        await message.answer("Language must be en or ru")
        return
    instr = await database.get_instruction(instr_id)
    if not instr:
        await message.answer("Not found.")
        return
    await state.set_state(EditContent.waiting)
    await state.update_data(instr_id=instr_id, lang=lang, buffer="")
    await message.answer(
        f"Send new content ({lang}) for #{instr_id}.\n"
        "You can send multiple messages if it's long.\n"
        "Send /done to save, /cancel to abort."
    )

@router.message(Command("done"))
async def cmd_done(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    current = await state.get_state()
    if current != EditContent.waiting.state:
        return
    data = await state.get_data()
    instr_id = data['instr_id']
    lang = data['lang']
    content = (data.get('buffer') or '').strip()
    if not content:
        await message.answer("Content is empty. Send text first or /cancel.")
        return
    field = f"content_{lang}"
    await database.update_instruction_field(instr_id, field, content)
    await state.clear()
    await message.answer(f"✅ Content ({lang}) updated for #{instr_id} ({len(content)} chars)")

@router.message(EditContent.waiting, F.text, ~F.text.startswith('/'))
async def setcontent_waiting(message: Message, state: FSMContext):
    data = await state.get_data()
    buffer = data.get('buffer') or ''
    chunk = message.text.rstrip()
    if buffer:
        buffer += "\n\n" + chunk
    else:
        buffer = chunk
    await state.update_data(buffer=buffer)
    await message.answer(f"Added ({len(chunk)} chars). Total: {len(buffer)} chars. Send more or /done to save.")

@router.message(Command("fullinst"))
async def cmd_fullinst(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Usage: /fullinst <id> [en|ru]")
        return
    try:
        instr_id = int(parts[1])
    except ValueError:
        await message.answer("Invalid id")
        return
    lang = parts[2].lower() if len(parts) > 2 else 'en'
    if lang not in ('en', 'ru'):
        lang = 'en'
    instr = await database.get_instruction(instr_id)
    if not instr:
        await message.answer("Not found.")
        return
    title = instr.get(f'title_{lang}') or instr.get('title_en') or instr.get('title') or f'#{instr_id}'
    content = instr.get(f'content_{lang}') or ''
    header = f"📖 #{instr_id} {title} ({lang.upper()})\n\n"
    text = header + (content if content else '[empty]')
    # split into chunks
    for i in range(0, len(text), 4000):
        await message.answer(text[i:i+4000])

@router.message(Command("grant"))
async def cmd_grant(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Usage: /grant <user_id_or_@username> <instruction_id>")
        return
    target = parts[1].strip()
    try:
        instr_id = int(parts[2])
    except ValueError:
        await message.answer("Invalid instruction id")
        return
    instr = await database.get_instruction(instr_id)
    if not instr:
        await message.answer("Instruction not found.")
        return

    # resolve user
    user_id = None
    if target.lstrip('-').isdigit():
        user_id = int(target)
    else:
        u = await database.find_user_by_username(target)
        if not u:
            await message.answer("User not found in database. They must start the bot first, or use numeric user ID.")
            return
        user_id = u['user_id']

    created = await database.grant_access(user_id, instr_id)
    if not created:
        await message.answer(f"User {user_id} already has access to #{instr_id}.")
    else:
        await message.answer(f"✅ Access granted: user {user_id} -> instruction #{instr_id}")
    # notify user
    try:
        lang = await database.get_user_lang(user_id)
        title = instr.get(f'title_{lang}') or instr.get('title_en') or instr.get('title') or f'#{instr_id}'
        content = instr.get(f'content_{lang}') or instr.get('content_en') or 'Content will be added soon.'
        msg = f"🎁 You received access!\n\n📖 {title}\n\n{content}"
        for i in range(0, len(msg), 4000):
            await message.bot.send_message(user_id, msg[i:i+4000])
    except Exception as e:
        await message.answer(f"(Granted, but could not notify user: {e})")

@router.message(AddInstruction.title_en, F.text, ~F.text.startswith('/'))
async def add_title_en(message: Message, state: FSMContext):
    await state.update_data(title_en=message.text.strip())
    await state.set_state(AddInstruction.title_ru)
    await message.answer("Step 2/7: Title (RU)")

@router.message(AddInstruction.title_ru, F.text, ~F.text.startswith('/'))
async def add_title_ru(message: Message, state: FSMContext):
    await state.update_data(title_ru=message.text.strip())
    await state.set_state(AddInstruction.description_en)
    await message.answer("Step 3/7: Description (EN)")

@router.message(AddInstruction.description_en, F.text, ~F.text.startswith('/'))
async def add_desc_en(message: Message, state: FSMContext):
    await state.update_data(description_en=message.text.strip())
    await state.set_state(AddInstruction.description_ru)
    await message.answer("Step 4/7: Description (RU)")

@router.message(AddInstruction.description_ru, F.text, ~F.text.startswith('/'))
async def add_desc_ru(message: Message, state: FSMContext):
    await state.update_data(description_ru=message.text.strip())
    await state.set_state(AddInstruction.price)
    await message.answer("Step 5/7: Price in USD (number, e.g. 9.99)")

@router.message(AddInstruction.price, F.text, ~F.text.startswith('/'))
async def add_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", ".").strip())
    except Exception:
        await message.answer("Invalid price. Send a number, e.g. 9.99")
        return
    await state.update_data(price=price)
    await state.set_state(AddInstruction.content_en)
    await message.answer("Step 6/7: Content (EN) - full instruction text")

@router.message(AddInstruction.content_en, F.text, ~F.text.startswith('/'))
async def add_content_en(message: Message, state: FSMContext):
    try:
        content = message.text.strip()
        await state.update_data(content_en=content)
        await state.set_state(AddInstruction.content_ru)
        await message.answer(f"Step 7/7: Content (RU) - full instruction text\n(EN saved: {len(content)} chars)")
    except Exception as e:
        await message.answer(f"❌ Error at step 6: {e}")

@router.message(AddInstruction.content_ru, F.text, ~F.text.startswith('/'))
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
