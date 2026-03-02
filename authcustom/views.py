from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated 
from authcustom.serializers import LoginSerializer, RegiserSerializer,ForgotPasswordSerializer,ResetPasswordSerializer  
from django.contrib.auth.hashers import make_password,check_password
from authcustom.services import userService,generate_reset_link,Send_reset_link,verify_reset_token,mark_token_used
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


from django.db import connection
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import uuid


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT")
        print(ip_address)
        print(user_agent)

        user_service = userService()
        user = user_service.Get_user_by_username(username)

        # ❌ User not found
        if not user:
            print("User not found")

            user_service.log_login_activity(
                user_id=None,
                email=username,
                ip=ip_address,
                user_agent=user_agent,
                status_value="FAILED",
                reason="User not found"
            )

            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ❌ Password incorrect
        if not check_password(password, user["hashed_password"]):
            print("Password incorrect")
            user_service.log_login_activity(
                user_id=user["user_id"],
                email=username,
                ip=ip_address,
                user_agent=user_agent,
                status_value="FAILED",
                reason="Invalid password"
            )

            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        session_id = str(uuid.uuid4())
        try:
            user_service.log_login_activity(
            user_id=user["user_id"],
            email=username,
            ip=ip_address,
            user_agent=user_agent,
            status_value="SUCCESS",
            reason=None,
            session_id=session_id
            )
        except Exception as e:
            print(e)

        # 🔐 Generate JWT
        refresh = RefreshToken()
        refresh["user_id"] = user["user_id"]
        role = get_user_role(user["user_id"])
        refresh["role"] = role
        refresh["session_id"] = session_id
        



        access_token = refresh.access_token

        response = Response(
            {"message": "User logged in successfully"},
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
    permission_classes = [IsAuthenticated]
   


    def post(self, request):
        print(request.user.id)

        session_id = request.user.session_id
        print("session_id",session_id)


        if session_id:
              

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE login_activity
                    SET logout_time = NOW(),
                        is_active = FALSE
                    WHERE session_id = %s
                    AND is_active = TRUE
                """, [session_id])

        response = Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )

        # Delete cookies
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


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        print("inside")
       
        if not serializer.is_valid(raise_exception=True):
            print("inside2")    
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data['email']
        try:
            user_service = userService()
            user = user_service.Get_user_by_email(email)
            
            
            reset_link = generate_reset_link(user)
            Send_reset_link(email, reset_link)
             


            
            return Response({"message": "User found"}, status=status.HTTP_200_OK )

        except Exception as e:
            print(e)
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )   
        
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request,uid,token):
        serializer = self.serializer_class(data=request.data)
        print("inside")
        print(uid)
        print(token)

       
        if not serializer.is_valid(raise_exception=True):
            print("inside2")    
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data['email']
        try:
            user_service = userService()
            
            user_id=verify_reset_token(token)
            print(user_id)
            if not user_id:
                return Response(
                    {"error": "Invalid token"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = user_service.reset_password(email, serializer.validated_data['password'])
            mark_token_used(token)


            if not user:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK )

        except Exception as e:  
            print(e)
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )   

