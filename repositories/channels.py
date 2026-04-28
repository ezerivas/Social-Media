# preparado para futuro (tokens por tenant en DB)

from database import get_connection


def get_channel_config(tenant_id: int, channel: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT config
        FROM channels
        WHERE tenant_id = %s AND name = %s
        """,
        (tenant_id, channel)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return None

    return row[0]  # JSON