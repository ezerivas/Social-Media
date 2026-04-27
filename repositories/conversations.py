from database import get_connection


def get_or_create_conversation(user_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, user_id, last_message_at
        FROM conversations
        WHERE user_id = %s
        LIMIT 1
        """,
        (user_id,)
    )
    conversation = cur.fetchone()

    if conversation:
        cur.close()
        conn.close()
        return conversation

    cur.execute(
        """
        INSERT INTO conversations (user_id)
        VALUES (%s)
        RETURNING id, user_id, last_message_at
        """,
        (user_id,)
    )

    conversation = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()
    return conversation


def update_last_message(conversation_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE conversations
        SET last_message_at = NOW()
        WHERE id = %s
        """,
        (conversation_id,)
    )

    conn.commit()
    cur.close()
    conn.close()


def get_all_conversations():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            c.id,
            u.name,
            u.external_id,
            c.last_message_at
        FROM conversations c
        JOIN users u ON u.id = c.user_id
        ORDER BY c.last_message_at DESC NULLS LAST
    """)

    rows = cur.fetchall()

    conversations = []
    for row in rows:
        conversations.append({
            "id": row[0],
            "name": row[1],
            "external_id": row[2],
            "last_message_at": row[3]
        })

    cur.close()
    conn.close()
    return conversations