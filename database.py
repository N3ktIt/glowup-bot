import aiosqlite
import config

async def init_db():
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS instructions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            content TEXT,
            is_active INTEGER DEFAULT 1
        )''')
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
        await db.execute("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?,?,?)",
                         (user_id, username, first_name))
        await db.commit()

async def get_instructions():
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM instructions WHERE is_active=1 ORDER BY id") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_instruction(instruction_id):
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM instructions WHERE id=?", (instruction_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

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
