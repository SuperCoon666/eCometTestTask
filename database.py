import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")


async def create_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)
