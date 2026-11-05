import asyncio
import aiosqlite
import config

async def add():
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        title = input("Instruction title: ")
        description = input("Short description: ")
        price = float(input("Price USD: "))
        content = input("Content (single line for test): ")
        await db.execute("INSERT INTO instructions (title, description, price, content) VALUES (?,?,?,?)",
                         (title, description, price, content))
        await db.commit()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(add())
