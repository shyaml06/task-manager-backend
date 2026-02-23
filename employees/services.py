import json
from django.db import connection

# PATH A: The Fast Path (Postgres handles JSON)
def get_employees_fast(dept_id):
    with connection.cursor() as cursor:
        # UDF returns a single JSON string/object
        cursor.execute("SELECT get_dept_employees(%s)", [dept_id])
        return cursor.fetchone()[0]

# PATH B: The Standard Path (Python handles Conversion)
def get_employees_standard(dept_id):
    with connection.cursor() as cursor:
        # Returns a list of tuples
        cursor.execute("SELECT id, name, salary FROM employees WHERE department_id = %s", [dept_id])
        columns = [col[0] for col in cursor.description]
        # This loop is the bottleneck:
        return [dict(zip(columns, row)) for row in cursor.fetchall()]