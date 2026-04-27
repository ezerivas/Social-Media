from database import get_connection

# Obtiene o crea conversación
def get_or_create_conversation(user_id: int, canal: str = "facebook"):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT id FROM conversations
            WHERE user_id = %s
            """,
            (user_id,)
        )
        conv = cur.fetchone()

        if conv:
            return conv[0]

        cur.execute(
            """
            INSERT INTO conversations (user_id, canal, estado)
            VALUES (%s, %s, 'open')
            RETURNING id
            """,
            (user_id, canal)
        )

        conv_id = cur.fetchone()[0]
        conn.commit()

        return conv_id

    finally:
        cur.close()
        conn.close()


# Inbox de conversaciones
def get_all_conversations():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT 
                c.id,
                u.external_id,
                u.name,
                c.canal,
                c.estado,
                c.last_message_at,
                (
                    SELECT text
                    FROM messages
                    WHERE conversation_id = c.id
                    ORDER BY timestamp DESC
                    LIMIT 1
                ) as last_message
            FROM conversations c
            JOIN users u ON u.id = c.user_id
            ORDER BY c.last_message_at DESC NULLS LAST
        """)

        rows = cur.fetchall()

        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "external_id": r[1],
                "name": r[2],
                "canal": r[3],
                "estado": r[4],
                "last_message_at": r[5],
                "last_message": r[6]
            })

        return result

    finally:
        cur.close()
        conn.close()