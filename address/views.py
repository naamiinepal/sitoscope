from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.http import require_safe

from . import models


# Create your views here.
def index(request):
    return HttpResponse("Hello World")

@require_safe
def get_provinces(request: HttpRequest):
    provinces = [
        (p.id, str(p))
        for p in models.Province.objects.all()
    ]
    return JsonResponse({"data": provinces})

@require_safe
def get_districts(request: HttpRequest, province_id: int):
    districts = [
        (d.id, str(d))
        for d in models.District.objects.filter(province_id=province_id).only("name")
    ]
    return JsonResponse({"province_id": province_id, "data": districts})



@require_safe
def get_sites(request: HttpRequest, district_id: int):
    sites = [
        (m.id, str(m))
        for m in models.Site.objects.filter(district_id=district_id).only(
            "name"
        )
    ]
    return JsonResponse({"district_id": district_id, "data": sites})