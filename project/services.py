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
        
import json
from google import genai
from django.conf import settings
from django.db import connection
import datetime    


def generate_workflow_from_ai(project_id, prompt):
    
    """
    Calls the Gemini API to generate a list of tasks for the project based on the given prompt.
    Returns structurally created tasks.
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in your environment.")
        
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name
            FROM projects
            WHERE id = %s
        """, [project_id])
        project_name = cursor.fetchone()[0] 

    print(project_name)
    current_date = datetime.date.today().strftime("%Y-%m-%d")   
    
    # We use a standard text model for structured output
    system_prompt = system_prompt = f"""You are an elite Agile Project Manager and System Architect. Your objective is to break down a high-level project request into a logical, sequential, and executable workflow.

PROJECT CONTEXT:
- Project Name: {project_name}
- Current Date: {current_date}

INSTRUCTIONS:
1. Analyze the project request and divide it into actionable, self-contained tasks.
2. Sequence the tasks logically from start to finish.
3. Assign a realistic 'due_date' for each task, calculating sequentially forward starting from the Current Date provided above. 
4. Ensure the 'description' clearly explains the exact outcome expected for that task.

OUTPUT CONSTRAINTS:
You must return strictly a valid, raw JSON array containing the task objects.
Do not wrap the output in markdown code blocks. Do not include any conversational text, introductions, or explanations. 

SCHEMA REQUIREMENT:
Every object in the array MUST contain exactly these three keys:
- "title" (string): A short, action-oriented title.
- "description" (string): A detailed explanation of the work to be done.
- "due_date" (string): The deadline in strict "YYYY-MM-DD" format.
"""
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"{system_prompt}\n\nUser request: {prompt}"
    )
    
    response_text = response.text.strip()
    # Strip markdown if AI generated it (just in case)
    if response_text.startswith("```json"):
        response_text = response_text.replace("```json", "", 1)
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    response_text = response_text.strip()
        
    try:
        task_list = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response into JSON. Response was: {response_text}") from e
        
    created_tasks = []
    for t in task_list:
        # Create task via existing service
        task = create_task(
            project_id=project_id,
            title=t.get("title", "Untitled AI Task"),
            description=t.get("description", ""),
            due_date=t.get("due_date", None)
        )
        created_tasks.append(task)
        
    return created_tasks
