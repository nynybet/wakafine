from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
