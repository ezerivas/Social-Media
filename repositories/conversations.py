from database import get_connection

def get_conversation_by_user(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM conversations
        WHERE user_id = %s
    """, (user_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    return {"id": row[0]} if row else None


def create_conversation(user_id, external_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO conversations (user_id, external_id, canal, estado)
        VALUES (%s, %s, 'facebook', 'open')
        RETURNING id
    """, (user_id, external_id))

    conv_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return {"id": conv_id}


def get_all_conversations():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.external_id, u.name, c.last_message_at
        FROM conversations c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.last_message_at DESC NULLS LAST
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "external_id": r[1],
            "name": r[2],
            "last_message_at": r[3]
        }
        for r in rows
    ]