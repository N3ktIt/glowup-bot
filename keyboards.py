from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts import t

def get_title(instr, lang):
    if lang == 'ru':
        return instr.get('title_ru') or instr.get('title_en') or instr.get('title') or 'Instruction'
    return instr.get('title_en') or instr.get('title_ru') or instr.get('title') or 'Instruction'

def main_menu(lang='en'):
    kb = [
        [InlineKeyboardButton(text=t(lang, 'catalog_btn'), callback_data="catalog")],
        [InlineKeyboardButton(text=t(lang, 'my_access_btn'), callback_data="my_access")],
        [InlineKeyboardButton(text=t(lang, 'info_btn'), callback_data="info")],
        [InlineKeyboardButton(text=t(lang, 'lang_btn'), callback_data="lang")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def catalog_kb(instructions, lang='en'):
    kb = []
    for instr in instructions:
        title = get_title(instr, lang)
        kb.append([InlineKeyboardButton(text=f"{title} - ${instr['price']:.2f}", callback_data=f"view_{instr['id']}")])
    kb.append([InlineKeyboardButton(text=t(lang, 'back_menu'), callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def instruction_kb(instr_id, has_access_flag=False, lang='en'):
    kb = []
    if has_access_flag:
        kb.append([InlineKeyboardButton(text=t(lang, 'view_instructions'), callback_data=f"read_{instr_id}")])
    else:
        kb.append([InlineKeyboardButton(text=t(lang, 'buy_crypto'), callback_data=f"buy_{instr_id}")])
    kb.append([InlineKeyboardButton(text=t(lang, 'back_catalog'), callback_data="catalog")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def back_to_main(lang='en'):
    kb = [[InlineKeyboardButton(text=t(lang, 'back_menu'), callback_data="main")]]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def pay_kb(pay_url, payment_id, lang='en'):
    kb = [
        [InlineKeyboardButton(text=t(lang, 'pay_now'), url=pay_url)],
        [InlineKeyboardButton(text=t(lang, 'cancel'), callback_data="catalog")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def lang_kb():
    kb = [
        [InlineKeyboardButton(text="English", callback_data="setlang_en")],
        [InlineKeyboardButton(text="Русский", callback_data="setlang_ru")],
        [InlineKeyboardButton(text="⬅️ Back / Назад", callback_data="main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
