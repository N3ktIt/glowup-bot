from aiogram import Router, F
from aiogram.types import CallbackQuery
import aiohttp
import uuid

import config
import database
import keyboards as kb
from keyboards import get_title
from texts import t

router = Router()

@router.callback_query(F.data.startswith("buy_"))
async def create_invoice(call: CallbackQuery):
    lang = await database.get_user_lang(call.from_user.id)
    instr_id = int(call.data.split("_")[1])
    instr = await database.get_instruction(instr_id)
    if not instr:
        await call.answer(t(lang, 'not_found'), show_alert=True)
        return

    order_id = str(uuid.uuid4())
    price = float(instr['price'])
    title = get_title(instr, lang)

    url = "https://api.nowpayments.io/v1/invoice"
    headers = {
        "x-api-key": config.NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "price_amount": price,
        "price_currency": "usd",
        "order_id": order_id,
        "order_description": f"GlowUp Center - {get_title(instr, 'en')}",
        "ipn_callback_url": f"{config.WEBHOOK_URL}/ipn" if config.WEBHOOK_URL else "",
        "success_url": f"https://t.me/{(await call.bot.get_me()).username}",
        "cancel_url": f"https://t.me/{(await call.bot.get_me()).username}"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                if resp.status in (200, 201) and data.get("invoice_url"):
                    pay_url = data["invoice_url"]
                    payment_id = order_id
                    await database.create_payment(call.from_user.id, instr_id, payment_id, price)
                    text = t(lang, 'invoice_created', title=title, price=price)
                    await call.message.edit_text(text, reply_markup=kb.pay_kb(pay_url, payment_id, lang))
                    await call.answer()
                else:
                    err = data.get('message') or data.get('error') or 'Failed'
                    await call.answer(f"Payment error: {err}", show_alert=True)
                    print(data)
    except Exception as e:
        await call.answer("Error creating payment", show_alert=True)
        print(e)
