from database import get_connection


def get_or_create_conversation(
    tenant_id: int,
    user_id: int,
    channel: str,
    external_user_id: str
):
    conn = get_connection()
    cur = conn.cursor()

    # buscar existente
    cur.execute(
        """
        SELECT id
        FROM conversations
        WHERE tenant_id = %s
        AND user_id = %s
        AND channel = %s
        """,
        (tenant_id, user_id, channel)
    )

    row = cur.fetchone()

    if row:
        cur.close()
        conn.close()
        return row

    # crear nueva
    cur.execute(
        """
        INSERT INTO conversations (tenant_id, user_id, channel, external_user_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (tenant_id, user_id, channel, external_user_id)
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

    cur.execute(
        """
        SELECT
            c.id,
            c.channel,
            c.external_user_id,
            c.last_message_at
        FROM conversations c
        ORDER BY c.last_message_at DESC NULLS LAST
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "channel": r[1],
            "user_external_id": r[2],
            "last_message_at": r[3]
        }
        for r in rows
    ]


def get_conversation(conversation_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, channel, external_user_id
        FROM conversations
        WHERE id = %s
        """,
        (conversation_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "id": row[0],
        "channel": row[1],
        "external_user_id": row[2]
    }