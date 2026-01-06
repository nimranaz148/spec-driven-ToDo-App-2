#!/usr/bin/env python3
"""
Quick fix to add missing title column to conversations table.
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment")
    exit(1)

# Convert SQLAlchemy URL to asyncpg format
if DATABASE_URL.startswith('postgresql+asyncpg://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')

async def add_title_column():
    """Add title column to conversations table if it doesn't exist."""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if title column exists
        result = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'conversations' AND column_name = 'title'
        """)
        
        if not result:
            print("Adding title column to conversations table...")
            await conn.execute("""
                ALTER TABLE conversations 
                ADD COLUMN title VARCHAR(200)
            """)
            print("✅ Title column added successfully!")
        else:
            print("✅ Title column already exists")
            
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(add_title_column())
