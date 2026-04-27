from database import get_connection

# Obtiene un usuario o lo crea si no existe
def get_or_create_user(external_id: str, name: str = None):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Buscar usuario existente
        cur.execute(
            "SELECT id FROM users WHERE external_id = %s",
            (external_id,)
        )
        user = cur.fetchone()

        if user:
            return user[0]

        # Crear usuario nuevo
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