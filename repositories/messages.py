from database import get_connection

def insert_message(conversation_id, sender, text):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO messages (conversation_id, sender, text)
        VALUES (%s, %s, %s)
    """, (conversation_id, sender, text))

    cur.execute("""
        UPDATE conversations
        SET last_message_at = NOW()
        WHERE id = %s
    """, (conversation_id,))

    conn.commit()
    cur.close()
    conn.close()


def get_messages(conversation_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, sender, text, timestamp
        FROM messages
        WHERE conversation_id = %s
        ORDER BY timestamp ASC
    """, (conversation_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "sender": r[1],
            "text": r[2],
            "timestamp": r[3].isoformat() if r[3] else None
        }
        for r in rows
    ]