"""Drop old user table to fix Better Auth conflict."""
from sqlalchemy import text, create_engine

# Use actual DATABASE_URL from backend/.env
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not found!")
    print("Set DATABASE_URL in backend/.env file")
    exit(1)

def drop_user_table_sync():
    """Drop old user table using synchronous connection."""
    engine = create_engine(DATABASE_URL)

    try:
        with engine.begin() as conn:
            # Drop user table if it exists - use quoted "user" because user is reserved keyword
            conn.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
            print("Success: Old user table dropped (if existed)")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Database URL: {DATABASE_URL}")
        exit(1)
    finally:
        engine.dispose()
        print("Done! Better Auth can now create its own user table.")

if __name__ == "__main__":
    drop_user_table_sync()
