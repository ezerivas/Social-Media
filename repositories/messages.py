from database import get_connection


def create_message(conversation_id: int, role: str, content: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO messages (conversation_id, role, content)
        VALUES (%s, %s, %s)
        RETURNING id, conversation_id, role, content, created_at
        """,
        (conversation_id, role, content)
    )

    message = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()
    return message


def get_messages_by_conversation(conversation_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, role, content, created_at
        FROM messages
        WHERE conversation_id = %s
        ORDER BY created_at ASC
        """,
        (conversation_id,)
    )

    rows = cur.fetchall()

    messages = []
    for row in rows:
        messages.append({
            "id": row[0],
            "sender": row[1],
            "text": row[2],
            "created_at": row[3]
        })

    cur.close()
    conn.close()
    return messages