import aiosqlite
import config

async def init_db():
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            lang TEXT DEFAULT 'en',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        # Migration for existing users table
        try:
            await db.execute("ALTER TABLE users ADD COLUMN lang TEXT DEFAULT 'en'")
        except Exception:
            pass

        await db.execute('''CREATE TABLE IF NOT EXISTS instructions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_en TEXT,
            title_ru TEXT,
            description_en TEXT,
            description_ru TEXT,
            price REAL NOT NULL,
            content_en TEXT,
            content_ru TEXT,
            is_active INTEGER DEFAULT 1
        )''')
        # Migrations for old schema
        for col in ["title_en", "title_ru", "description_en", "description_ru", "content_en", "content_ru"]:
            try:
                if col == "price":
                    continue
                await db.execute(f"ALTER TABLE instructions ADD COLUMN {col} TEXT")
            except Exception:
                pass

        await db.execute('''CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            instruction_id INTEGER,
            payment_id TEXT UNIQUE,
            amount REAL,
            status TEXT DEFAULT 'pending',
            paid_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (instruction_id) REFERENCES instructions (id)
        )''')
        await db.commit()

async def add_user(user_id, username, first_name):
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, lang) VALUES (?,?,?,?)",
                         (user_id, username, first_name, 'en'))
        await db.commit()

async def get_user_lang(user_id):
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        async with db.execute("SELECT lang FROM users WHERE user_id=?", (user_id,)) as c:
            row = await c.fetchone()
            return row[0] if row and row[0] else 'en'

async def set_user_lang(user_id, lang):
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        await db.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
        await db.commit()

def _normalize_instruction(row):
    if not row:
        return None
    d = dict(row)
    # Backward compatibility
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
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM instructions WHERE is_active=1 ORDER BY id") as cursor:
            rows = await cursor.fetchall()
            return [_normalize_instruction(r) for r in rows]

async def get_instruction(instruction_id):
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM instructions WHERE id=?", (instruction_id,)) as cursor:
            row = await cursor.fetchone()
            return _normalize_instruction(row)

async def add_instruction(title_en, title_ru, description_en, description_ru, price, content_en, content_ru):
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        await db.execute('''INSERT INTO instructions 
            (title_en, title_ru, description_en, description_ru, price, content_en, content_ru, title, description, content) 
            VALUES (?,?,?,?,?,?,?,?,?,?)''',
            (title_en, title_ru, description_en, description_ru, price, content_en, content_ru, title_en, description_en, content_en))
        await db.commit()

async def has_access(user_id, instruction_id):
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        async with db.execute("SELECT id FROM purchases WHERE user_id=? AND instruction_id=? AND status='paid'",
                             (user_id, instruction_id)) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def create_payment(user_id, instruction_id, payment_id, amount):
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        await db.execute("INSERT INTO purchases (user_id, instruction_id, payment_id, amount) VALUES (?,?,?,?)",
                         (user_id, instruction_id, payment_id, amount))
        await db.commit()

async def mark_paid(payment_id):
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        await db.execute("UPDATE purchases SET status='paid', paid_at=CURRENT_TIMESTAMP WHERE payment_id=?", (payment_id,))
        await db.commit()
        async with db.execute("SELECT user_id, instruction_id FROM purchases WHERE payment_id=?", (payment_id,)) as cursor:
            row = await cursor.fetchone()
            return row
