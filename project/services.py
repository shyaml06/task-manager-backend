from django.db import connection

def makedictionary(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def create_project(name, description, start_date, end_date):
    with connection.cursor() as cursor:
        cursor.execute(
            "select * from sp_create_project(%s, %s, %s, %s)",
            [name, description, start_date, end_date]
        )
        return makedictionary(cursor)

def get_all_projects():
    with connection.cursor() as cursor:
        cursor.execute(
            "select * from sp_get_all_projects()",
        )
        projects=makedictionary(cursor)
        return projects



def create_task(project_id,title, description, status, due_date):
    with connection.cursor() as cursor:
        cursor.execute(
            "select * from sp_create_task(%s, %s, %s, %s, %s)",
            [project_id, title, description, status, due_date]
        )
        return makedictionary(cursor)

from django.db import connection


def get_tasks_by_project(project_id, status=None, limit=20, offset=0):
    print("get_tasks_by_project")


    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM tasks where project_id=%s;",
            [project_id]
        )

        cols = [c[0] for c in cursor.description]
        rows = cursor.fetchall()

    return [
        dict(zip(cols, row))
        for row in rows
    ]

    



from django.db import connection


def create_task(project_id, title, description, due_date):

    query = """
        INSERT INTO tasks (project_id, title, description, due_date)
        VALUES (%s, %s, %s, %s)
        RETURNING id, project_id, title, description, status, due_date
    """

    with connection.cursor() as cursor:

        cursor.execute(
            query,
            [project_id, title, description, due_date]
        )

        row = cursor.fetchone()

        columns = [col[0] for col in cursor.description]

    return dict(zip(columns, row))




from django.db import connection


def project_exists(project_id: int) -> bool:
    query = """
        SELECT 1
        FROM projects
        WHERE id = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [project_id])
        result = cursor.fetchone()

    return result is not None


from django.db import connection


def get_task_status_summary():

    query = """
        SELECT status, COUNT(*) as count
        FROM tasks
        GROUP BY status
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    return [
        {"status": row[0], "count": row[1]}
        for row in rows
    ]





def get_tasks_per_project():

    query = """
        SELECT p.name, COUNT(t.id)
        FROM projects p
        LEFT JOIN tasks t ON p.id = t.project_id
        GROUP BY p.name
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    return [
        {"project": row[0], "tasks": row[1]}
        for row in rows
    ]



from django.db import connection

def update_task_status_db(task_id, new_status):
    """
    Updates the status of a task using raw SQL.
    Returns True if the task was updated, False if the task_id wasn't found.
    """
    # Define allowed statuses to prevent invalid data from entering the DB
    allowed_statuses = ['pending', 'in_progress', 'completed']
    if new_status not in allowed_statuses:
        raise ValueError("Invalid status provided")

    # Using 'with' ensures the cursor is closed automatically
    with connection.cursor() as cursor:
        # We use %s to safely parameterize the variables
        cursor.execute(
            """
            UPDATE tasks 
            SET status = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
            """,
            [new_status, task_id]
        )
        
        # cursor.rowcount tells us how many rows were actually affected
        return cursor.rowcount > 0





from django.db import connection

def assign_task_db(task_id, user_id):
    """
    Assigns a task to a specific user. 
    user_id can be None/Null to unassign a task.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE tasks 
            SET assigned_to = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
            """,
            [user_id, task_id]  # If user_id is None, it saves as NULL in Postgres
        )
        return cursor.rowcount > 0


from django.db import connection

from django.db import connection

def get_assignable_users_db():
    """
    Fetches assignable users by joining the users table with the user_roles table.
    Filters for roles 1 (admin), 2 (manager), and 3 (employee).
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                u.id, 
                u.username, 
                ur.role_id 
            FROM users u
            JOIN user_roles ur ON u.id = ur.user_id
            WHERE ur.role_id IN (1, 2, 3)
            ORDER BY u.username ASC
        """)
        
        # Maps the raw rows to a list of dictionaries: [{"id": 1, "username": "admin", "role_id": 1}, ...]
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        