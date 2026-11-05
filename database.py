import asyncpg
import config

pool = None

async def init_db():
    global pool
    if not config.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")
    pool = await asyncpg.create_pool(config.DATABASE_URL, min_size=1, max_size=5)
    async with pool.acquire() as conn:
        await conn.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            lang TEXT DEFAULT 'en',
            joined_at TIMESTAMPTZ DEFAULT NOW()
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS instructions (
            id SERIAL PRIMARY KEY,
            title TEXT,
            description TEXT,
            content TEXT,
            title_en TEXT,
            title_ru TEXT,
            description_en TEXT,
            description_ru TEXT,
            price DOUBLE PRECISION NOT NULL,
            content_en TEXT,
            content_ru TEXT,
            is_active INTEGER DEFAULT 1
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS purchases (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            instruction_id INTEGER,
            payment_id TEXT UNIQUE,
            amount DOUBLE PRECISION,
            status TEXT DEFAULT 'pending',
            paid_at TIMESTAMPTZ
        )''')

async def close_db():
    global pool
    if pool:
        await pool.close()

async def add_user(user_id, username, first_name):
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO users (user_id, username, first_name, lang)
               VALUES ($1, $2, $3, 'en')
               ON CONFLICT (user_id) DO UPDATE SET username=COALESCE($2, users.username), first_name=COALESCE($3, users.first_name)""",
            user_id, username, first_name
        )

async def ensure_user(user_id, username=None, first_name=None):
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO users (user_id, username, first_name, lang)
               VALUES ($1, $2, $3, 'en')
               ON CONFLICT (user_id) DO NOTHING""",
            user_id, username, first_name
        )

async def get_user_lang(user_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT lang FROM users WHERE user_id=$1", user_id)
        return row['lang'] if row and row['lang'] else 'en'

async def set_user_lang(user_id, lang):
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO users (user_id, lang) VALUES ($1, $2)
               ON CONFLICT (user_id) DO UPDATE SET lang=$2""",
            user_id, lang
        )

def _normalize_instruction(row):
    if not row:
        return None
    d = dict(row)
    if not d.get('title_en') and d.get('title'):
        d['title_en'] = d['title']
        d['title_ru'] = d.get('title_ru') or d['title']
    if not d.get('description_en') and d.get('description'):
        d['description_en'] = d['description']
        d['description_ru'] = d.get('description_ru') or d['description']
    if not d.get('content_en') and d.get('content'):
        d['content_en'] = d['content']
        d['content_ru'] = d.get('content_ru') or d['content']
    return d

async def get_instructions():
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM instructions WHERE is_active=1 ORDER BY id")
        return [_normalize_instruction(r) for r in rows]

async def get_instruction(instruction_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM instructions WHERE id=$1", instruction_id)
        return _normalize_instruction(row)

async def add_instruction(title_en, title_ru, description_en, description_ru, price, content_en, content_ru):
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO instructions
               (title_en, title_ru, description_en, description_ru, price, content_en, content_ru, title, description, content)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$1,$3,$6)""",
            title_en, title_ru, description_en, description_ru, price, content_en, content_ru
        )

async def has_access(user_id, instruction_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id FROM purchases WHERE user_id=$1 AND instruction_id=$2 AND status='paid'",
            user_id, instruction_id
        )
        return row is not None

async def create_payment(user_id, instruction_id, payment_id, amount):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO purchases (user_id, instruction_id, payment_id, amount) VALUES ($1,$2,$3,$4)",
            user_id, instruction_id, payment_id, amount
        )

async def mark_paid(payment_id):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE purchases SET status='paid', paid_at=NOW() WHERE payment_id=$1", payment_id)
        row = await conn.fetchrow("SELECT user_id, instruction_id FROM purchases WHERE payment_id=$1", payment_id)
        return (row['user_id'], row['instruction_id']) if row else None

async def list_purchases(limit=20):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT p.id, p.user_id, p.instruction_id, p.payment_id, p.amount, p.status, p.paid_at,
                      i.title_en
               FROM purchases p
               LEFT JOIN instructions i ON p.instruction_id = i.id
               ORDER BY p.id DESC LIMIT $1""",
            limit
        )
        return [dict(r) for r in rows]
