from django.urls import path
from .views import (
    AdminStatsView,
    AdminUserList,
    AdminAssignRole,
    Roleview,
    LoginactivityView
)

urlpatterns = [

    path("stats/", AdminStatsView.as_view()),

    path("users/", AdminUserList.as_view()),

    path("assign-role/", AdminAssignRole.as_view()),
    path("role/", Roleview.as_view()),
    path ("loginactivity/",LoginactivityView.as_view())

]
