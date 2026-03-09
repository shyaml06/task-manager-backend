from django.urls import path
from . import views
from .views import RefreshView
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('me/', views.MeView.as_view(), name='me'),
    path('logout/',views.LogoutView.as_view()),
    path('forgot-password/',views.ForgotPasswordView.as_view()), 
    path('reset-password/<str:uid>/<str:token>/',views.ResetPasswordView.as_view()),
    path("refresh/", RefreshView.as_view(), name="token_refresh"),


    
    

    
]
