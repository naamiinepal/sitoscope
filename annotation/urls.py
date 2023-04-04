from django.urls import path

from . import views

app_name = "annotation"
urlpatterns = [
    path("", views.annotation_home, name="annotation_home"),
    path("via_get/<img>", views.via_get, name="via_annotation_get"),
    path("via_post", views.via_post, name="via_annotation_post"),
]
