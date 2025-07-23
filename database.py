
import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS coordinates (
            id SERIAL PRIMARY KEY,
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION
        );
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL
        );
    """)
    await conn.close()

async def save_geo(coord: tuple):
    lat, lon = coord
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("INSERT INTO coordinates (lat, lon) VALUES ($1, $2)", lat, lon)
    await conn.close()

async def get_random_geo():
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT lat, lon FROM coordinates ORDER BY random() LIMIT 1")
    await conn.close()
    return f"{row['lat']},{row['lon']}" if row else None

async def get_all_geo():
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT lat, lon FROM coordinates ORDER BY id DESC LIMIT 10")
    await conn.close()
    return [f"{r['lat']},{r['lon']}" for r in rows]

async def save_fact(text: str):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("INSERT INTO facts (text) VALUES ($1)", text)
    await conn.close()

async def get_all_facts():
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT * FROM facts ORDER BY id")
    await conn.close()
    return rows

async def get_random_fact():
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT text FROM facts ORDER BY random() LIMIT 1")
    await conn.close()
    return row["text"] if row else None

async def delete_fact(fact_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    result = await conn.execute("DELETE FROM facts WHERE id=$1", fact_id)
    await conn.close()
    return result.startswith("DELETE")
