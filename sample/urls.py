from django.urls import include, path
from rest_framework.routers import DefaultRouter

from sample import views
from sample.sample_views import standard_sample_views, water_sample_views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"standard", views.StandardViewSetAPI, basename="standard")
router.register(r"water", views.WaterViewSetAPI, basename="water")
router.register(r"vegetable", views.VegetableViewSetAPI, basename="vegetable")
router.register(r"stool", views.StoolViewSetAPI, basename="stool")


# The API URLs are now determined automatically by the router.
app_name = "sample"
urlpatterns = [
    path("api/samples/", include(router.urls)),
    path(
        "standard-samples/",
        standard_sample_views.StandardListView.as_view(),
        name="standard_list",
    ),
    path(
        "standard-samples/new/",
        standard_sample_views.StandardFormView.as_view(),
        name="standard_create",
    ),
    path(
        "standard-samples/<slug:sample_id>/",
        standard_sample_views.StandardDetailView.as_view(),
        name="standard_detail",
    ),
    path(
        "standard-samples/<str:sample_id>/<int:slide_number>/<str:image_type>",
        standard_sample_views.standard_slide_image_details,
        name="standard_slide_image",
    ),
    path(
        "water-samples/",
        water_sample_views.WaterListView.as_view(),
        name="water_list",
    ),
    path(
        "water-samples/new/",
        water_sample_views.WaterFormView.as_view(),
        name="water_create",
    ),
    path(
        "water-samples/<slug:sample_id>/",
        water_sample_views.WaterDetailView.as_view(),
        name="water_detail",
    ),
    path(
        "water-samples/<slug:sample_id>/<slug:slide_number>/<slug:image_type>/upload",
        water_sample_views.WaterSlideImageCreateView.as_view(),
        name="water_slide_image_upload",
    ),
    path(
        "water-samples/<slug:sample_id>/<slug:slide_number>/<slug:image_type>",
        water_sample_views.WaterSlideImageDetailView.as_view(),
        name="water_slide_image",
    ),
]
