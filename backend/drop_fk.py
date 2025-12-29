"""Drop foreign key constraint on tasks table."""
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

async def drop_fk():
    async with engine.begin() as conn:
        # Check for existing foreign key constraints on tasks table
        result = await conn.execute(text('''
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'tasks'
            AND constraint_type = 'FOREIGN KEY'
        '''))
        fk_constraints = [row[0] for row in result.fetchall()]
        print(f'Found foreign key constraints: {fk_constraints}')

        for fk in fk_constraints:
            print(f'Dropping constraint: {fk}')
            await conn.execute(text(f'ALTER TABLE tasks DROP CONSTRAINT IF EXISTS "{fk}"'))

        print('Done!')

if __name__ == '__main__':
    asyncio.run(drop_fk())
