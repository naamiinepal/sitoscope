from django.http import HttpRequest
from django.shortcuts import render


# Create your views here
def index(request: HttpRequest):
    if request.user.is_authenticated:
        return render(request, "sample/home.html")
    else:
        return render(request, "sample/index.html")
