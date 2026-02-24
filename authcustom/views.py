from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated 
from authcustom.serializers import LoginSerializer, RegiserSerializer
from django.contrib.auth.hashers import make_password,check_password
from authcustom.services import userService
from indextest import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .services import insert_role,assign_role
from .utils import get_user_role
from .permissions import IsAdmin
# Create your view
#  here.

class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegiserSerializer
    
    
    def post(self, request):
        # Registration logic goes here
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        hashed_password = make_password(password)
        user_service = userService()
        user = user_service.RegisterUser(username, email, hashed_password)
        if not user:
            return Response({"error": "Registration failed"}, status=status.HTTP_400_BAD_REQUEST)
        print(user["register_user"])
        role_id=insert_role(user["register_user"]);
        
        
        
        return Response({"message": "User registered successfully", "user": user}, status=status.HTTP_201_CREATED)



class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        print(password)

        user_service = userService()
        user = user_service.Get_user_by_username(username)
        print(user)

        if not user:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ✅ Password check (hashed)
        if not check_password(password, user["hashed_password"]):
            return Response(
                {"error": "Invalid password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ✅ Create JWT tokens (NO ORM usage)
        refresh = RefreshToken()
        refresh["user_id"] = user["user_id"]
        role=get_user_role(user["user_id"])
        refresh["role"]=role# 👈 important
        #refresh["username"] = user["username"]  # optional claim

        access_token = refresh.access_token

        response = Response(
            {
                "message": "User logged in successfully"
            },
            status=status.HTTP_200_OK
        )

        # 🍪 Access token cookie
        response.set_cookie(
            key="access_token",
            value=str(access_token),
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            path="/"
        )

        # 🍪 Refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            path="/"
        )

        return response


class MeView(APIView):
    


    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username
        })





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status


class LogoutView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        print("INSIDE LOGOUT COOKIES:", request.COOKIES)

        response = Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )

        # ✅ Delete cookies (Django 6 compatible)
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

        return response













class AssignRoleView(APIView):

    permission_classes = [IsAdmin]

    def post(self, request):

        user_id = request.data.get("user_id")
        role_id = request.data.get("role_id")

        if not user_id or not role_id:
            return Response(
                {"error": "Missing fields"},
                status=400
            )

        assign_role(user_id, role_id)

        return Response({
            "success": True,
            "message": "Role updated"
        })
