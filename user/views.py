from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render


# Create your views here
def index(request: HttpRequest):
    return render(request, "sample/index.html")


@login_required
def home(request: HttpRequest):
    return render(request, "sample/home.html")
