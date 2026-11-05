TEXTS = {
    'en': {
        'welcome': "👋 Welcome to GlowUp Center, {name}!\n\nHere you'll find exclusive beauty & glow-up instructions.\n\nChoose an option below:",
        'catalog_btn': "📚 Instructions",
        'my_access_btn': "💼 My Access",
        'info_btn': "ℹ️ Info",
        'lang_btn': "🌐 Language",
        'back': "⬅️ Back",
        'back_menu': "⬅️ Back to Menu",
        'back_catalog': "⬅️ Back to Catalog",
        'catalog_empty': "📚 Catalog is empty at the moment.\n\nNew instructions coming soon!",
        'choose_instruction': "📚 Choose an instruction pack:",
        'not_found': "Instruction not found",
        'price': "Price",
        'buy_crypto': "💳 Buy with Crypto",
        'view_instructions': "📖 View Instructions",
        'no_access': "You don't have access to this",
        'your_access': "💼 Your Access",
        'no_purchases': "You haven't purchased any instructions yet.\n\nCheck the catalog to get started!",
        'you_have_access': "You have access to:",
        'go_to_catalog': "Go to catalog and click 'View Instructions' to read.",
        'info_text': "ℹ️ GlowUp Center\n\nDigital instructions for your glow-up journey.\n\nAll purchases are final. Access is granted instantly after successful payment.",
        'invoice_created': "💳 Invoice created for {title}\n\nAmount: ${price:.2f} USD\n\nClick 'Pay Now' to complete payment with crypto.",
        'pay_now': "💰 Pay Now",
        'cancel': "⬅️ Cancel",
        'choose_lang': "🌐 Choose language / Выберите язык:",
        'lang_set': "Language set to English."
    },
    'ru': {
        'welcome': "👋 Добро пожаловать в GlowUp Center, {name}!\n\nЗдесь ты найдёшь эксклюзивные инструкции по улучшению внешности.\n\nВыбери действие ниже:",
        'catalog_btn': "📚 Инструкции",
        'my_access_btn': "💼 Мои покупки",
        'info_btn': "ℹ️ Инфо",
        'lang_btn': "🌐 Язык",
        'back': "⬅️ Назад",
        'back_menu': "⬅️ В меню",
        'back_catalog': "⬅️ К каталогу",
        'catalog_empty': "📚 Каталог пока пуст.\n\nСкоро появятся новые инструкции!",
        'choose_instruction': "📚 Выбери инструкцию:",
        'not_found': "Инструкция не найдена",
        'price': "Цена",
        'buy_crypto': "💳 Купить за крипту",
        'view_instructions': "📖 Открыть инструкцию",
        'no_access': "У тебя нет доступа",
        'your_access': "💼 Мои покупки",
        'no_purchases': "Ты ещё ничего не покупал.\n\nЗагляни в каталог!",
        'you_have_access': "У тебя есть доступ к:",
        'go_to_catalog': "Открой каталог и нажми 'Открыть инструкцию'.",
        'info_text': "ℹ️ GlowUp Center\n\nЦифровые инструкции для твоего преображения.\n\nВсе покупки окончательны. Доступ выдаётся сразу после оплаты.",
        'invoice_created': "💳 Счёт создан для {title}\n\nСумма: ${price:.2f} USD\n\nНажми 'Оплатить', чтобы оплатить криптой.",
        'pay_now': "💰 Оплатить",
        'cancel': "⬅️ Отмена",
        'choose_lang': "🌐 Choose language / Выберите язык:",
        'lang_set': "Язык переключён на русский."
    }
}

def t(lang, key, **kwargs):
    lang = lang if lang in TEXTS else 'en'
    text = TEXTS[lang].get(key, TEXTS['en'].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
