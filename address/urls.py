from django.urls import path
from . import views

app_name = "address"
urlpatterns = [
    path("", views.index, name="index"),
    path(
        "province/", 
        views.get_provinces, 
        name="get_provinces"
    ),
    path(
        "province/<int:province_id>/", 
        views.get_districts, 
        name="get_districts"),
    path(
        "district/<int:district_id>/",
        views.get_sites,
        name="get_sites",
    ),
]