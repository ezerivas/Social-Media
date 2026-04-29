class MessageRepository:
    # Para saber a qué cuenta de Facebook responder
    async def get_conversation_details(self, conversation_id: int):
        query = """
            SELECT c.external_user_id, ch.config 
            FROM conversations c
            JOIN channels ch ON c.channel_id = ch.id
            WHERE c.id = :conversation_id
        """
        return await fetch_one(query, {"conversation_id": conversation_id})

    # Para persistir el historial
    async def create_message(self, conversation_id: int, role: str, content: str, external_id: str = None):
        query = """
            INSERT INTO messages (conversation_id, role, content, external_id)
            VALUES (:conversation_id, :role, :content, :external_id)
            RETURNING id
        """
        return await execute_query(query, locals())