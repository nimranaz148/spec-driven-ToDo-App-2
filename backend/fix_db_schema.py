"""Fix database schema: drop old users table and add FK to user table."""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import ssl as ssl_module
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', '')
print(f'DATABASE_URL prefix: {DATABASE_URL[:50]}...')

# Process URL for asyncpg
parsed = urlparse(DATABASE_URL)
query_params = parse_qs(parsed.query)
ssl_required = 'sslmode' in query_params and query_params['sslmode'][0] in ['require', 'verify-ca', 'verify-full']

if 'sslmode' in query_params:
    del query_params['sslmode']

new_query = urlencode(query_params, doseq=True)
DATABASE_URL = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

if DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)
elif DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+asyncpg://', 1)

engine_kwargs = {}
if ssl_required:
    ssl_context = ssl_module.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl_module.CERT_NONE
    engine_kwargs['connect_args'] = {'ssl': ssl_context}

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

async def fix_schema():
    async with engine.begin() as conn:
        # 1. List all tables
        print("\n=== Current Tables ===")
        result = await conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        for t in tables:
            print(f"  - {t}")

        # 2. Drop the old 'users' table (plural) if it exists
        if 'users' in tables:
            print("\n=== Dropping old 'users' table ===")
            await conn.execute(text('DROP TABLE IF EXISTS "users" CASCADE'))
            print("  Dropped 'users' table")
        else:
            print("\n=== No 'users' table found (already clean) ===")

        # 3. Check if 'user' table exists (Better Auth table)
        if 'user' not in tables:
            print("\nERROR: 'user' table doesn't exist! Better Auth hasn't created it yet.")
            return

        print("\n=== 'user' table structure ===")
        result = await conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'user'
            ORDER BY ordinal_position
        """))
        for row in result.fetchall():
            print(f"  - {row[0]}: {row[1]}")

        # 4. Delete existing tasks (they reference old user IDs)
        print("\n=== Clearing tasks table for fresh start ===")
        await conn.execute(text('DELETE FROM tasks'))
        print("  Cleared all tasks")

        # 5. Add foreign key constraint from tasks.user_id to user.id
        print("\n=== Adding foreign key constraint ===")
        # First check if FK already exists
        result = await conn.execute(text("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'tasks'
            AND constraint_type = 'FOREIGN KEY'
        """))
        existing_fks = [row[0] for row in result.fetchall()]

        if existing_fks:
            print(f"  Existing FKs: {existing_fks}")
            for fk in existing_fks:
                await conn.execute(text(f'ALTER TABLE tasks DROP CONSTRAINT IF EXISTS "{fk}"'))
                print(f"  Dropped: {fk}")

        # Add new FK to 'user' table
        await conn.execute(text("""
            ALTER TABLE tasks
            ADD CONSTRAINT tasks_user_id_fkey
            FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
        """))
        print("  Added FK: tasks.user_id -> user.id")

        # 6. Verify final schema
        print("\n=== Final Tables ===")
        result = await conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        for row in result.fetchall():
            print(f"  - {row[0]}")

        print("\n=== Foreign Keys on tasks table ===")
        result = await conn.execute(text("""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
            WHERE tc.table_name = 'tasks'
            AND tc.constraint_type = 'FOREIGN KEY'
        """))
        for row in result.fetchall():
            print(f"  - {row[0]}: tasks.{row[1]} -> {row[2]}.{row[3]}")

        print("\nDone!")

if __name__ == '__main__':
    asyncio.run(fix_schema())
