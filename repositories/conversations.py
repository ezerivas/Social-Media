from app.database import get_connection


def get_or_create_conversation(tenant_id: int, user_id: int, channel: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id FROM conversations
        WHERE tenant_id = %s AND user_id = %s AND channel = %s
        """,
        (tenant_id, user_id, channel),
    )
    conv = cur.fetchone()

    if conv:
        cur.close()
        conn.close()
        return conv[0]

    cur.execute(
        """
        INSERT INTO conversations (tenant_id, user_id, channel)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (tenant_id, user_id, channel),
    )

    conv_id = cur.fetchone()[0]
    conn.commit()

    cur.close()
    conn.close()
    return conv_id


def update_last_message(conversation_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE conversations SET last_message_at = NOW() WHERE id = %s",
        (conversation_id,),
    )

    conn.commit()
    cur.close()
    conn.close()


def get_all_conversations(tenant_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT c.id, u.external_id, c.channel, c.last_message_at
        FROM conversations c
        JOIN users u ON u.id = c.user_id
        WHERE c.tenant_id = %s
        ORDER BY c.last_message_at DESC
        """,
        (tenant_id,),
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "user_external_id": r[1],
            "channel": r[2],
            "last_message_at": r[3],
        }
        for r in rows
    ]