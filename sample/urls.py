from django.urls import path, include
from sample import views
from sample.sample_views import standard_sample_views, water_sample_views
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"standard", views.StandardViewSet, basename="standard")
router.register(r"water", views.WaterViewSet, basename="water")
router.register(r"vegetable", views.VegetableViewSet, basename="vegetable")
router.register(r"stool", views.StoolViewSet, basename="stool")


# The API URLs are now determined automatically by the router.
app_name = "sample"
urlpatterns = [
    path("api/samples/", include(router.urls)),
    path(
        "standard-samples/",
        standard_sample_views.standard_home,
        name="standard_samples_home",
    ),
    path(
        "standard-samples/new/",
        standard_sample_views.get_standard_form,
        name="add_standard_sample",
    ),
    path(
        "standard-samples/<str:sample_id>/",
        standard_sample_views.standard_sample_detail,
        name="standard_sample_detail",
    ),
    path(
        "standard-samples/<str:sample_id>/<int:slide_number>/<str:image_type>",
        standard_sample_views.standard_slide_image_details,
        name="standard_slide_image",
    ),
    path(
        "water-samples/",
        water_sample_views.water_home,
        name="water_samples_home",
    ),
    path(
        "water-samples/new/",
        water_sample_views.get_water_form,
        name="add_water_sample",
    ),
    path(
        "water-samples/<str:sample_id>/",
        water_sample_views.water_sample_detail,
        name="water_sample_detail",
    ),
    path(
        "water-samples/<str:sample_id>/<int:slide_number>/<str:image_type>",
        water_sample_views.water_slide_image_details,
        name="water_slide_image",
    ),
]
