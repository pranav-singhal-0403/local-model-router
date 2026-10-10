
import os
from contextlib import asynccontextmanager

import asyncpg
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    database_host = os.getenv("POSTGRES_HOST", "localhost")
    database_port = os.getenv("POSTGRES_PORT", "5432")
    database_name = os.getenv("POSTGRES_DB", "rag_router")
    database_user = os.getenv("POSTGRES_USER", "raguser")
    database_password = os.getenv("POSTGRES_PASSWORD")

    if not database_password:
        raise RuntimeError("POSTGRES_PASSWORD is not configured.")

    DATABASE_URL = (
        f"postgresql://{database_user}:{database_password}"
        f"@{database_host}:{database_port}/{database_name}"
    )


SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL DEFAULT 'New chat',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL
        REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    latency JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_updated_at
    ON conversations (updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
    ON messages (conversation_id, created_at);
"""


class Database:

    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            dsn=DATABASE_URL,
            min_size=1,
            max_size=10,
            command_timeout=30,
        )

        async with self.pool.acquire() as connection:
            await connection.execute(SCHEMA)

    async def close(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    @asynccontextmanager
    async def connection(self):
        if self.pool is None:
            raise RuntimeError("Database is not connected.")

        async with self.pool.acquire() as connection:
            yield connection
