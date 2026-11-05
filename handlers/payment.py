from aiogram import Router, F
from aiogram.types import CallbackQuery
import aiohttp
import uuid

import config
import database
import keyboards as kb

router = Router()

@router.callback_query(F.data.startswith("buy_"))
async def create_invoice(call: CallbackQuery):
    instr_id = int(call.data.split("_")[1])
    instr = await database.get_instruction(instr_id)
    if not instr:
        await call.answer("Instruction not found", show_alert=True)
        return
    
    order_id = str(uuid.uuid4())
    price = float(instr['price'])
    
    url = "https://api.nowpayments.io/v1/invoice"
    headers = {
        "x-api-key": config.NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "price_amount": price,
        "price_currency": "usd",
        "order_id": order_id,
        "order_description": f"GlowUp Center - {instr['title']}",
        "ipn_callback_url": f"{config.WEBHOOK_URL}/ipn",
        "success_url": f"https://t.me/{(await call.bot.get_me()).username}",
        "cancel_url": f"https://t.me/{(await call.bot.get_me()).username}"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                if resp.status == 200 and data.get("invoice_url"):
                    pay_url = data["invoice_url"]
                    payment_id = order_id
                    await database.create_payment(call.from_user.id, instr_id, payment_id, price)
                    text = f"💳 Invoice created for {instr['title']}\n\nAmount: ${price:.2f} USD\n\nClick 'Pay Now' to complete payment with crypto."
                    await call.message.edit_text(text, reply_markup=kb.pay_kb(pay_url, payment_id))
                    await call.answer()
                else:
                    await call.answer("Failed to create invoice. Try again later.", show_alert=True)
    except Exception as e:
        await call.answer("Error creating payment", show_alert=True)
        print(e)
