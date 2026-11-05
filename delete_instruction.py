import asyncio
import aiosqlite
import config

async def delete():
    async with aiosqlite.connect(config.DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, title, price FROM instructions") as c:
            rows = await c.fetchall()
            if not rows:
                print("No instructions found")
                return
            for r in rows:
                print(f"{r['id']}: {r['title']} - ${r['price']}")
        instr_id = int(input("Enter ID to delete: "))
        await db.execute("DELETE FROM instructions WHERE id=?", (instr_id,))
        await db.commit()
        print("Deleted")

if __name__ == "__main__":
    asyncio.run(delete())
