from database import get_connection


def get_tenant_by_id(tenant_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name FROM tenants WHERE id = %s",
        (tenant_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "name": row[1]
    }