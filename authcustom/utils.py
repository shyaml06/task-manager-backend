from django.db import connection


def get_user_role(user_id):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT r.name
            FROM roles r
            JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = %s
        """, [user_id])

        row = cursor.fetchone()

    return row[0] if row else None
