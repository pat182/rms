from sqlalchemy import text
from app.core.database import engine

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print(result.scalar())
        print("Connected successfully!")
except Exception as e:
    print(f"Connection failed: {e}")