import asyncpg
import json
from typing import Any, Dict, List, Optional


class MessageRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def save_message(self, tenant_id: int, user_external_id: str, channel: str, content: str, role: str):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                user_id = await conn.fetchval(
                    """
                    INSERT INTO users (tenant_id, external_id)
                    VALUES ($1, $2)
                    ON CONFLICT (tenant_id, external_id) DO UPDATE SET external_id = EXCLUDED.external_id
                    RETURNING id
                    """,
                    tenant_id,
                    user_external_id,
                )

                conv_id = await conn.fetchval(
                    """
                    INSERT INTO conversations (tenant_id, user_id, channel, external_user_id, last_message_at)
                    VALUES ($1, $2, $3, $4, NOW())
                    ON CONFLICT (tenant_id, user_id, channel, external_user_id)
                    DO UPDATE SET last_message_at = NOW()
                    RETURNING id
                    """,
                    tenant_id,
                    user_id,
                    channel,
                    user_external_id,
                )

                row = await conn.fetchrow(
                    """
                    INSERT INTO messages (conversation_id, role, content, created_at)
                    VALUES ($1, $2, $3, NOW())
                    RETURNING id, conversation_id, role, content, created_at
                    """,
                    conv_id,
                    role,
                    content,
                )

                result = dict(row)
                result["tenant_id"] = tenant_id
                return result

    async def get_conversation_details(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT tenant_id, channel, external_user_id
            FROM conversations
            WHERE id = $1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, conversation_id)
            return dict(row) if row else None

    async def get_channel_config(self, tenant_id: int, channel_name: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT config
            FROM channels
            WHERE tenant_id = $1 AND name = $2
        """
        async with self.pool.acquire() as conn:
            config_json = await conn.fetchval(query, tenant_id, channel_name)
            return json.loads(config_json) if isinstance(config_json, str) else config_json

    async def save_outbound_message(self, conversation_id: int, content: str, role: str = "agent"):
        query = """
            INSERT INTO messages (conversation_id, role, content, created_at)
            VALUES ($1, $2, $3, NOW())
            RETURNING id, conversation_id, role, content, created_at
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, conversation_id, role, content)
            return dict(row)

    async def list_conversations(self, tenant_id: int, channel: str) -> List[Dict[str, Any]]:
        query = """
            SELECT c.id, c.channel, c.external_user_id, c.last_message_at,
                   COALESCE(m.content, '') AS last_message,
                   COALESCE(m.role, 'user') AS last_message_role
            FROM conversations c
            LEFT JOIN LATERAL (
                SELECT content, role
                FROM messages
                WHERE conversation_id = c.id
                ORDER BY created_at DESC
                LIMIT 1
            ) m ON TRUE
            WHERE c.tenant_id = $1 AND c.channel = $2
            ORDER BY c.last_message_at DESC NULLS LAST
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, tenant_id, channel)
            return [dict(row) for row in rows]

    async def list_messages(self, tenant_id: int, conversation_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT m.id, m.conversation_id, m.role, m.content, m.created_at
            FROM messages m
            INNER JOIN conversations c ON c.id = m.conversation_id
            WHERE c.tenant_id = $1 AND m.conversation_id = $2
            ORDER BY m.created_at ASC
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, tenant_id, conversation_id)
            return [dict(row) for row in rows]
