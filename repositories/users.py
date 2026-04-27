from database import get_connection

# Obtener o crear usuario
def get_or_create_user(external_id: str, name: str = None):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT id FROM users WHERE external_id = %s",
            (external_id,)
        )
        user = cur.fetchone()

        if user:
            return user[0]

        cur.execute(
            """
            INSERT INTO users (external_id, name)
            VALUES (%s, %s)
            RETURNING id
            """,
            (external_id, name)
        )

        user_id = cur.fetchone()[0]
        conn.commit()

        return user_id

    finally:
        cur.close()
        conn.close()