from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUser
from .services import assign_role

class AdminStatsView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        with connection.cursor() as cursor:

            # Users
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            # Projects
            cursor.execute("SELECT COUNT(*) FROM projects")
            total_projects = cursor.fetchone()[0]

            # Tasks
            cursor.execute("SELECT COUNT(*) FROM tasks")
            total_tasks = cursor.fetchone()[0]

            # Completed
            cursor.execute("""
                SELECT COUNT(*) FROM tasks
                WHERE status='completed'
            """)
            completed = cursor.fetchone()[0]


        return Response({
            "total_users": total_users,
            "total_projects": total_projects,
            "total_tasks": total_tasks,
            "completed_tasks": completed
        })



class AdminUserList(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT u.id, u.username, u.email, r.name
                FROM users u
                LEFT JOIN user_roles ur ON u.id = ur.user_id
                LEFT JOIN roles r ON ur.role_id = r.id
            """)

            rows = cursor.fetchall()


        users = [
            {
                "id": r[0],
                "username": r[1],
                "email": r[2],
                "role": r[3]
            }
            for r in rows
        ]


        return Response(users)












class AdminAssignRole(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request):

        user_id = request.data.get("user_id")
        role_id = request.data.get("role_id")

        if not user_id or not role_id:
            return Response(
                {"error": "Missing fields"},
                status=400
            )

        new_role = assign_role(user_id, role_id)

        return Response({
            "success": True,
            "role_id": new_role
        })

from django.db import connection


class Roleview(APIView):
     permission_classes = [IsAuthenticated]
     
     def get(self,request):
        user_id=request.user.id;
        with connection.cursor() as cursor:

           cursor.execute(
                    "select r.name from roles r inner join user_roles ur on r.id=ur.role_id where ur.user_id=%s;",
                    [user_id]
                )
           role=cursor.fetchone()[0]
        return Response({
            "Role":role
            
        })
         
    
    