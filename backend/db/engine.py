import os
import asyncpg
from fastapi import Request

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/reefsync")

async def get_db_conn():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

async def execute_query_all(sql: str, **params):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        return await conn.fetch(sql, *params.values())
    finally:
        await conn.close()

async def execute_query_one(sql: str, **params):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        return await conn.fetchrow(sql, *params.values())
    finally:
        await conn.close()
