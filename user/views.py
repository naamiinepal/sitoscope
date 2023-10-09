from django.http import HttpRequest
from django.shortcuts import render

from annotation.models import Annotator


# Create your views here
def index(request: HttpRequest):
    if request.user.is_authenticated:
        # check if user is annotator
        is_annotator = Annotator.objects.filter(user=request.user).exists()
        return render(request, "sample/home.html", {"is_annotator": is_annotator})
    else:
        return render(request, "sample/index.html")
