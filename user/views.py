from django.shortcuts import render
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required

# Create your views here
def index(request: HttpRequest):
    return render(request, 'sample/index.html')
