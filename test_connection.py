import asyncio

from sqlalchemy import text

from app.core.database import engine


async def check_connection():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    finally:
        await engine.dispose()


def main():
    try:
        asyncio.run(check_connection())
    except Exception as exc:
        print(f"Connection failed: {exc}")
        raise SystemExit(1) from exc

    print("Successfully connected to Supabase!")


if __name__ == "__main__":
    main()