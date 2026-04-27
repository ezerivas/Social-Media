from database import get_connection
from datetime import datetime

# Guardar mensaje
def save_message(conversation_id: int, sender: str, text: str):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO messages (conversation_id, sender, text, timestamp)
            VALUES (%s, %s, %s, %s)
            """,
            (conversation_id, sender, text, datetime.utcnow())
        )

        # actualizar última actividad
        cur.execute(
            """
            UPDATE conversations
            SET last_message_at = %s
            WHERE id = %s
            """,
            (datetime.utcnow(), conversation_id)
        )

        conn.commit()

    finally:
        cur.close()
        conn.close()


# Obtener mensajes
def get_messages_by_conversation(conversation_id: int):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT id, sender, text, timestamp
            FROM messages
            WHERE conversation_id = %s
            ORDER BY timestamp ASC
            """,
            (conversation_id,)
        )

        rows = cur.fetchall()

        return [
            {
                "id": r[0],
                "sender": r[1],
                "text": r[2],
                "timestamp": r[3]
            }
            for r in rows
        ]

    finally:
        cur.close()
        conn.close()