
import json
from uuid import UUID, uuid4

from backend.database import Database


class ChatHistory:

    def __init__(self, database: Database):
        self.database = database

    async def create_conversation(self, title="New chat"):
        conversation_id = uuid4()

        async with self.database.connection() as connection:
            await connection.execute(
                """
                INSERT INTO conversations (id, title)
                VALUES ($1, $2)
                """,
                conversation_id,
                title,
            )

        return str(conversation_id)

    async def list_conversations(self):
        async with self.database.connection() as connection:
            rows = await connection.fetch(
                """
                SELECT
                    c.id,
                    c.title,
                    c.created_at,
                    c.updated_at,
                    COUNT(m.id)::INTEGER AS message_count
                FROM conversations c
                LEFT JOIN messages m
                    ON m.conversation_id = c.id
                GROUP BY c.id
                ORDER BY c.updated_at DESC
                """
            )

        return [
            {
                "id": str(row["id"]),
                "title": row["title"],
                "created_at": row["created_at"].isoformat(),
                "updated_at": row["updated_at"].isoformat(),
                "message_count": row["message_count"],
            }
            for row in rows
        ]

    async def get_messages(self, conversation_id):
        try:
            conversation_uuid = UUID(conversation_id)
        except ValueError:
            return None

        async with self.database.connection() as connection:
            exists = await connection.fetchval(
                "SELECT EXISTS(SELECT 1 FROM conversations WHERE id = $1)",
                conversation_uuid,
            )

            if not exists:
                return None

            rows = await connection.fetch(
                """
                SELECT id, role, content, sources, latency, created_at
                FROM messages
                WHERE conversation_id = $1
                ORDER BY created_at, id
                """,
                conversation_uuid,
            )

        return [
            {
                "id": str(row["id"]),
                "role": row["role"],
                "content": row["content"],
                "sources": self._json_value(row["sources"]),
                "latency": self._json_value(row["latency"]),
                "created_at": row["created_at"].isoformat(),
            }
            for row in rows
        ]

    async def add_message(
        self,
        conversation_id,
        role,
        content,
        sources=None,
        latency=None,
    ):
        conversation_uuid = UUID(conversation_id)

        async with self.database.connection() as connection:
            async with connection.transaction():
                await connection.execute(
                    """
                    INSERT INTO messages (
                        id, conversation_id, role, content, sources, latency
                    )
                    VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb)
                    """,
                    uuid4(),
                    conversation_uuid,
                    role,
                    content,
                    json.dumps(sources or []),
                    json.dumps(latency or {}),
                )

                await connection.execute(
                    """
                    UPDATE conversations
                    SET
                        updated_at = NOW(),
                        title = CASE
                            WHEN title = 'New chat' AND $2 = 'user'
                            THEN LEFT($3, 80)
                            ELSE title
                        END
                    WHERE id = $1
                    """,
                    conversation_uuid,
                    role,
                    content,
                )

    async def delete_conversation(self, conversation_id):
        try:
            conversation_uuid = UUID(conversation_id)
        except ValueError:
            return False

        async with self.database.connection() as connection:
            result = await connection.execute(
                "DELETE FROM conversations WHERE id = $1",
                conversation_uuid,
            )

        return result == "DELETE 1"

    @staticmethod
    def _json_value(value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        return value
