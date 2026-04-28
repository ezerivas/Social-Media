from database import get_connection


def get_user_by_external_id(tenant_id: int, external_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, external_id
        FROM users
        WHERE tenant_id = %s AND external_id = %s
        """,
        (tenant_id, external_id)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()
    return user


def create_user(tenant_id: int, external_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users (tenant_id, external_id)
        VALUES (%s, %s)
        RETURNING id, external_id
        """,
        (tenant_id, external_id)
    )

    user = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()
    return user


def get_or_create_user(tenant_id: int, external_id: str):
    user = get_user_by_external_id(tenant_id, external_id)

    if user:
        return user

    return create_user(tenant_id, external_id)