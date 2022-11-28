from django.urls import path, include
from address import views
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"provinces", views.ProvinceViewSet, basename="province")
router.register(r"districts", views.DistrictViewSet, basename="district")
router.register(r"municipalities", views.MunicipalityViewSet, basename="municipality")
router.register(r"wards", views.WardViewSet, basename="ward")


# The API URLs are now determined automatically by the router.
urlpatterns = [path("", include(router.urls))]
