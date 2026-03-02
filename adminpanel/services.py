from django.db import connection


def assign_role(user_id, role_id):

    with connection.cursor() as cursor:

        cursor.execute(
            "SELECT assign_role(%s, %s)",
            [user_id, role_id]
        )

        return cursor.fetchone()[0]



def makedictionary(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def get_login_activity():
    try:
        with connection.cursor() as cursor:
            cursor.execute("select * from login_activity;")
            data=makedictionary(cursor);
    except Exception as e:
        print(e)
        return None
    
   
    return data
    