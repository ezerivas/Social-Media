from database import get_connection
import json


def get_channel_config(tenant_id: int, channel: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT config
        FROM channels
        WHERE tenant_id = %s AND type = %s
    """, (tenant_id, channel))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return None

    return row[0]  # JSON → dict