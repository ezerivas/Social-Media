from database import get_connection

def get_user_by_external_id(external_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, external_id, name
        FROM users
        WHERE external_id = %s
    """, (external_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return {
            "id": row[0],
            "external_id": row[1],
            "name": row[2]
        }

    return None


def create_user(external_id, name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (external_id, name)
        VALUES (%s, %s)
        RETURNING id
    """, (external_id, name))

    user_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return {"id": user_id, "external_id": external_id, "name": name}