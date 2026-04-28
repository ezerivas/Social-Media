from app.database import get_connection


def create_message(conversation_id: int, role: str, content: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO messages (conversation_id, role, content)
        VALUES (%s, %s, %s)
        RETURNING id, role, content, created_at
        """,
        (conversation_id, role, content),
    )

    msg = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()
    return msg


def get_messages(conversation_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT role, content, created_at
        FROM messages
        WHERE conversation_id = %s
        ORDER BY created_at ASC
        """,
        (conversation_id,),
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {"role": r[0], "content": r[1], "created_at": r[2]} for r in rows
    ]