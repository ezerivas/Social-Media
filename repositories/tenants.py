from app.database import get_connection


def get_tenant(tenant_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM tenants WHERE id = %s", (tenant_id,))
    tenant = cur.fetchone()

    cur.close()
    conn.close()
    return tenant