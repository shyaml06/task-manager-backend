from django.db import connections
from django.db import connection,transaction


def makeDict(cursor, row):
    return dict((cursor.description[i][0], value) for i, value in enumerate(row))



class userService:
    
    def RegisterUser(self, username, email, password):
        with connections['default'].cursor() as cursor:
            cursor.execute("select * from register_user(%s, %s, %s);", [username, email, password])
             
            row= cursor.fetchone()
            if row:
                 return makeDict(cursor, row)
            return None


   
        return True
    
    
    def Get_user_by_username(self, username):
        with connections['default'].cursor() as cursor:
            cursor.execute("select * from get_user_for_login(%s);", [username])
            row= cursor.fetchone()
            if row:
                 return makeDict(cursor, row)
            return None
        
    def get_user_by_id(self, user_id):

        query = "SELECT id, username FROM users WHERE id = %s"

        with connection.cursor() as cursor:
            cursor.execute(query, [user_id])
            row = cursor.fetchone()

        if not row:
            return None

        return {
        "id": row[0],
        "username": row[1],
        
            }


def insert_role(user_id, role_id=3):
    """
    Assign role to user and return role_id
    Default role_id = 3 (employee)
    """

    query = """
        INSERT INTO user_roles (user_id, role_id)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """
    print(user_id)
    
    with transaction.atomic():
        with connection.cursor() as cursor:

            # Insert role
            cursor.execute(query, [user_id, role_id])

            # Fetch role
            cursor.execute(
                "SELECT get_user_role_id(%s)",
                [user_id]
            )

            role = cursor.fetchone()[0]

    return role
    

    



def assign_role(user_id: int, role_id: int) -> int:

    query = "SELECT assign_role(%s, %s);"
    
    
    with connection.cursor() as cursor:
        cursor.execute(query, [user_id, role_id])
        assigned_role = cursor.fetchone()[0]

    return assigned_role    
    
        
        
    
    
    
        
