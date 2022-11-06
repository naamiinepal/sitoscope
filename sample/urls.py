from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = "sample"
urlpatterns = [
    path("", views.index, name="index"),
    path(
        "symptoms/", 
        views.SymptomsView.as_view(), 
        name="get_diarrhea_symptoms"
    ),
    path(
        "symptom/",
        login_required(views.SymptomFormView.as_view()),
        name="symptom_form"
    )
]