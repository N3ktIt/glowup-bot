from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    kb = [
        [InlineKeyboardButton(text="📚 Instructions", callback_data="catalog")],
        [InlineKeyboardButton(text="💼 My Access", callback_data="my_access")],
        [InlineKeyboardButton(text="ℹ️ Info", callback_data="info")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def catalog_kb(instructions):
    kb = []
    for instr in instructions:
        kb.append([InlineKeyboardButton(text=f"{instr['title']} - ${instr['price']:.2f}", callback_data=f"view_{instr['id']}")])
    kb.append([InlineKeyboardButton(text="⬅️ Back", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def instruction_kb(instr_id, has_access_flag=False):
    kb = []
    if has_access_flag:
        kb.append([InlineKeyboardButton(text="📖 View Instructions", callback_data=f"read_{instr_id}")])
    else:
        kb.append([InlineKeyboardButton(text="💳 Buy with Crypto", callback_data=f"buy_{instr_id}")])
    kb.append([InlineKeyboardButton(text="⬅️ Back to Catalog", callback_data="catalog")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def back_to_main():
    kb = [[InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="main")]]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def pay_kb(pay_url, payment_id):
    kb = [
        [InlineKeyboardButton(text="💰 Pay Now", url=pay_url)],
        [InlineKeyboardButton(text="⬅️ Cancel", callback_data="catalog")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
