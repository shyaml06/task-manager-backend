from django.shortcuts import render
from project.serializers import ProjectSerializer, TaskSerializer
from .services import create_project, get_all_projects, get_tasks_by_project, create_task
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from authcustom.permissions import IsAdmin,IsEmployee

# Create your views here.


class Createprojectview(APIView):
    serializer_class = ProjectSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        name = serializer.validated_data['name']
        description = serializer.validated_data['description']
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        project = create_project(name, description, start_date, end_date)
        return Response(project, status=status.HTTP_201_CREATED)
    

class Listprojectview(APIView):
    serializer_class = ProjectSerializer
    permission_classes=[IsEmployee|IsAdmin]

    def get(self, request):
        projects = get_all_projects()
        
        
        return Response({
            "data":projects}, status=status.HTTP_200_OK)


   
    
    

class Getprojecttask(APIView):
    permission_classes=[IsEmployee|IsAdmin]

    
    def get(self, request, project_id):
        tasks = get_tasks_by_project(project_id)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from authcustom.permissions import IsEmployee
from .serializers import TaskSerializer
from .services import create_task


class CreateTask(APIView):

    permission_classes = [IsEmployee]
    serializer_class = TaskSerializer


    def post(self, request):

        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            project_id = serializer.validated_data["project_id"]
            title = serializer.validated_data["title"]
            description = serializer.validated_data.get("description", "")
            due_date = serializer.validated_data.get("due_date")

            # Let DB handle status (default = pending)
            task = create_task(
                project_id,
                title,
                description,
                due_date
            )

            return Response(
                {
                    "success": True,
                    "data": task
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:

            print("CreateTask error:", e)

            return Response(
                {
                    "success": False,
                    "error": "Failed to create task"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
   
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class LogoutView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        response = Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )

        # Get refresh token from cookie
        refresh_token = request.COOKIES.get("refresh_token")

        # 🔐 Blacklist refresh token (if enabled)
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass  # Token already invalid/expired

        # 🍪 Delete cookies
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

        return response


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from authcustom.permissions import IsEmployee
from .services import get_tasks_by_project


class ProjectsTaskView(APIView):

    permission_classes = [IsEmployee|IsAdmin]

    def get(self, request, project_id):

        try:
            # Fetch tasks
            tasks = get_tasks_by_project(project_id)

            return Response(
                {
                    "success": True,
                    "data": tasks
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print("ERROR in ProjectsTaskView:", e)



            return Response(
                {
                    "success": False,
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    
        


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services import (
    get_task_status_summary,
    get_tasks_per_project
)


class DashboardAnalyticsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "status_summary": get_task_status_summary(),
            "tasks_per_project": get_tasks_per_project()
        })



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Import your service function (adjust the import path based on your folder structure)
from .services import update_task_status_db 

class UpdateTaskStatusView(APIView):
    def put(self, request, task_id):
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {"success": False, "message": "Status is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Call your raw SQL service
            updated = update_task_status_db(task_id, new_status)
            
            if updated:
                return Response(
                    {"success": True, "message": "Task updated successfully"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"success": False, "message": "Task not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except ValueError as e:
            # Catches the "Invalid status provided" error from the service
            return Response(
                {"success": False, "message": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Catch unexpected database errors
            return Response(
                {"success": False, "message": "Database error occurred"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import assign_task_db

class AssignTaskView(APIView):
    permission_classes=[IsAdmin]
    def patch(self, request, task_id):
        # We expect {"assigned_to": 5} or {"assigned_to": null} from React
        user_id = request.data.get('assigned_to') 

        try:
            updated = assign_task_db(task_id, user_id)
            if updated:
                return Response({"success": True, "message": "Task assignment updated"})
            return Response({"success": False, "message": "Task not found"}, status=404)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=500)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import get_assignable_users_db

class AssignableUsersView(APIView):
    def get(self, request):
        try:
            # Fetch the users using our raw SQL service
            users = get_assignable_users_db()
            
            # Return the data in the format React expects: res.data.data
            return Response({
                "success": True,
                "data": users
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Catch any database errors and return a 500 response
            return Response({
                "success": False,
                "message": "Failed to fetch assignable users",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)