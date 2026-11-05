import asyncio
import logging
import json
import hmac
import hashlib
from aiohttp import web

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import TelegramObject
from typing import Any, Awaitable, Callable, Dict

import config
import database
from handlers import start, catalog, payment, admin
from keyboards import get_title
from handlers.catalog import get_field

logging.basicConfig(level=logging.INFO)

class EnsureUserMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        user = data.get('event_from_user')
        if user:
            try:
                await database.ensure_user(user.id, user.username, user.first_name)
            except Exception:
                pass
        return await handler(event, data)

async def health(request):
    return web.Response(text="OK")

def verify_ipn_signature(body: dict, signature: str) -> bool:
    if not config.NOWPAYMENTS_IPN_SECRET:
        return True  # skip verification if not set
    sorted_body = json.dumps(body, separators=(',', ':'), sort_keys=True)
    digest = hmac.new(
        config.NOWPAYMENTS_IPN_SECRET.encode(),
        sorted_body.encode(),
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(digest, signature)

async def ipn_handler(request):
    try:
        body = await request.json()
        signature = request.headers.get('x-nowpayments-sig', '')
        if config.NOWPAYMENTS_IPN_SECRET and not verify_ipn_signature(body, signature):
            logging.warning("IPN signature verification failed")
            return web.Response(status=400, text="invalid signature")

        payment_status = body.get('payment_status')
        order_id = body.get('order_id') or body.get('payment_id')
        if payment_status in ('finished', 'confirmed') and order_id:
            result = await database.mark_paid(order_id)
            if result:
                user_id, instruction_id = result
                bot: Bot = request.app['bot']
                instr = await database.get_instruction(instruction_id)
                if instr and bot:
                    lang = await database.get_user_lang(user_id)
                    title = get_title(instr, lang)
                    content = get_field(instr, 'content', lang) or ('Content will be added soon.' if lang == 'en' else 'Контент скоро будет добавлен.')
                    text = f"✅ Payment confirmed!\n\n📖 {title}\n\n{content}"
                    try:
                        await bot.send_message(user_id, text[:4096])
                    except Exception as e:
                        logging.error(f"Failed to send instruction to {user_id}: {e}")
        return web.Response(text="OK")
    except Exception as e:
        logging.error(f"IPN error: {e}")
        return web.Response(status=200, text="OK")

async def start_web_server(bot: Bot):
    app = web.Application()
    app['bot'] = bot
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    app.router.add_post("/ipn", ipn_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.PORT)
    await site.start()
    logging.info(f"Web server started on port {config.PORT}")

async def main():
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    await database.init_db()

    dp.update.middleware(EnsureUserMiddleware())

    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(payment.router)

    logging.info("Bot starting...")
    await start_web_server(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
