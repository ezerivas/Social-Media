import asyncpg
from datetime import datetime

class MessageRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_or_create_conversation(self, tenant_id: int, user_id: int, channel: str, external_user_id: str):
        """Busca una conversación activa o crea una nueva si no existe [cite: 743]"""
        query = """
            INSERT INTO conversations (tenant_id, user_id, channel, external_user_id, last_message_at)
            VALUES ($1, $2, $3, $4, NOW())
            ON CONFLICT (tenant_id, user_id, channel, external_user_id) 
            DO UPDATE SET last_message_at = NOW()
            RETURNING id
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, tenant_id, user_id, channel, external_user_id)

    async def save_message(self, conversation_id: int, role: str, content: str):
        """Guarda un mensaje en la base de datos (Entrante o Saliente) [cite: 740]"""
        query = """
            INSERT INTO messages (conversation_id, role, content, created_at)
            VALUES ($1, $2, $3, NOW())
            RETURNING id, conversation_id, role, content, created_at
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, conversation_id, role, content)
            return dict(row)

    async def get_conversation_with_config(self, conversation_id: int):
        """Obtiene la configuración del canal (tokens) para poder enviar mensajes de salida [cite: 736]"""
        query = """
            SELECT c.*, ch.config, ch.name as channel_type
            FROM conversations c
            JOIN channels ch ON c.tenant_id = ch.tenant_id AND c.channel = ch.name
            WHERE c.id = $1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, conversation_id)
            return dict(row) if row else None