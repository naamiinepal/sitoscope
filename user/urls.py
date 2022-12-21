from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from user import views

app_name = "user"
urlpatterns = (
    [
        path("", views.index, name="index"),
        path("login/", auth_views.LoginView.as_view(), name="login"),
        path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
