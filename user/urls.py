from django.contrib.auth import views as auth_views
from django.urls import path

from user import views

app_name = "user"
urlpatterns = [
    path("", views.index, name="index"),
    path("samples/", views.home, name="home"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
