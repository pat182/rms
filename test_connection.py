import asyncio
from sqlalchemy import text
from app.core.database import engine

async def test_connection():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
            print("Successfully connected to Supabase!")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        await engine.dispose()

asyncio.run(test_connection())