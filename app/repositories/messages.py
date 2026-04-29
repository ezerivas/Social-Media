import asyncpg
import json
from datetime import datetime
from typing import Dict, Any, Optional

class MessageRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def save_message(self, tenant_id: int, user_external_id: str, channel: str, content: str, role: str):
        """
        Orquesta el guardado completo: 
        1. Asegura que el usuario existe.
        2. Asegura que la conversación existe.
        3. Guarda el mensaje.
        """
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # 1. Obtener o crear el usuario (identificado por su ID externo de la red social)
                user_id = await conn.fetchval("""
                    INSERT INTO users (tenant_id, external_id)
                    VALUES ($1, $2)
                    ON CONFLICT (tenant_id, external_id) DO UPDATE SET external_id = EXCLUDED.external_id
                    RETURNING id
                """, tenant_id, user_external_id)

                # 2. Obtener o crear la conversación
                conv_id = await conn.fetchval("""
                    INSERT INTO conversations (tenant_id, user_id, channel, external_user_id, last_message_at)
                    VALUES ($1, $2, $3, $4, NOW())
                    ON CONFLICT (tenant_id, user_id, channel, external_user_id) 
                    DO UPDATE SET last_message_at = NOW()
                    RETURNING id
                """, tenant_id, user_id, channel, user_external_id)

                # 3. Guardar el mensaje
                query = """
                    INSERT INTO messages (conversation_id, role, content, created_at)
                    VALUES ($1, $2, $3, NOW())
                    RETURNING id, conversation_id, role, content, created_at
                """
                row = await conn.fetchrow(query, conv_id, role, content)
                
                # Devolvemos un diccionario con el mensaje y el tenant_id (útil para el WebSocket)
                result = dict(row)
                result["tenant_id"] = tenant_id
                return result

    async def get_conversation_details(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos críticos para el envío de salida (Outbound).
        """
        query = """
            SELECT tenant_id, channel, external_user_id 
            FROM conversations 
            WHERE id = $1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, conversation_id)
            return dict(row) if row else None

    async def get_channel_config(self, tenant_id: int, channel_name: str) -> Optional[Dict[str, Any]]:
        """
        Recupera el JSON de configuración (tokens) del canal para un tenant específico.
        """
        query = """
            SELECT config 
            FROM channels 
            WHERE tenant_id = $1 AND name = $2
        """
        async with self.pool.acquire() as conn:
            config_json = await conn.fetchval(query, tenant_id, channel_name)
            return json.loads(config_json) if isinstance(config_json, str) else config_json

    async def save_outbound_message(self, conversation_id: int, content: str, role: str = "agent"):
        """
        Guarda un mensaje enviado por un agente desde el dashboard.
        """
        query = """
            INSERT INTO messages (conversation_id, role, content, created_at)
            VALUES ($1, $2, $3, NOW())
            RETURNING id, conversation_id, role, content, created_at
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, conversation_id, role, content)
            return dict(row)