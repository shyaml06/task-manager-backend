from django.db import connection


def assign_role(user_id, role_id):

    with connection.cursor() as cursor:

        cursor.execute(
            "SELECT assign_role(%s, %s)",
            [user_id, role_id]
        )

        return cursor.fetchone()[0]
