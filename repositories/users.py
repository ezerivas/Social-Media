from db import get_connection


def get_user_by_external_id(external_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, external_id, name FROM users WHERE external_id = %s",
        (external_id,)
    )
    user = cur.fetchone()

    cur.close()
    conn.close()
    return user


def create_user(external_id: str, name: str = None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users (external_id, name)
        VALUES (%s, %s)
        RETURNING id, external_id, name
        """,
        (external_id, name)
    )

    user = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()
    return user


def get_or_create_user(external_id: str, name: str = None):
    user = get_user_by_external_id(external_id)

    if user:
        return user

    return create_user(external_id, name)