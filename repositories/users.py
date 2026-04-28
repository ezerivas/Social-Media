from app.database import get_connection


def get_or_create_user(tenant_id: int, external_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM users WHERE tenant_id = %s AND external_id = %s",
        (tenant_id, external_id),
    )
    user = cur.fetchone()

    if user:
        cur.close()
        conn.close()
        return user

    cur.execute(
        """
        INSERT INTO users (tenant_id, external_id)
        VALUES (%s, %s)
        RETURNING id
        """,
        (tenant_id, external_id),
    )

    user = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()
    return user