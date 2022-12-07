from django.urls import include, path
from rest_framework.routers import DefaultRouter

from sample import views
from sample.sample_views import (
    standard_sample_views,
    stool_sample_views,
    vegetable_sample_views,
    water_sample_views,
)

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
        "standard-samples/<slug:sample_id>/<slug:slide_number>/<slug:image_type>",
        standard_sample_views.StandardSlideImageDetailView.as_view(),
        name="standard_slide_image",
    ),
    path(
        "standard-samples/<slug:sample_id>/<slug:slide_number>/<slug:image_type>/upload",
        standard_sample_views.StandardSlideImageCreateView.as_view(),
        name="standard_slide_image_upload",
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
    path(
        "vegetable-samples/",
        vegetable_sample_views.VegetableListView.as_view(),
        name="vegetable_list",
    ),
    path(
        "vegetable-samples/new/",
        vegetable_sample_views.VegetableFormView.as_view(),
        name="vegetable_create",
    ),
    path(
        "vegetable-samples/<slug:sample_id>/",
        vegetable_sample_views.VegetableDetailView.as_view(),
        name="vegetable_detail",
    ),
    path(
        "vegetable-samples/<slug:sample_id>/<slug:slide_number>/<slug:image_type>/upload",
        vegetable_sample_views.VegetableSlideImageCreateView.as_view(),
        name="vegetable_slide_image_upload",
    ),
    path(
        "vegetable-samples/<slug:sample_id>/<slug:slide_number>/<slug:image_type>",
        vegetable_sample_views.VegetableSlideImageDetailView.as_view(),
        name="vegetable_slide_image",
    ),
    path(
        "stool-samples/",
        stool_sample_views.StoolListView.as_view(),
        name="stool_list",
    ),
    path(
        "stool-samples/new/",
        stool_sample_views.StoolFormView.as_view(),
        name="stool_create",
    ),
    path(
        "stool-samples/<slug:sample_id>/",
        stool_sample_views.StoolDetailView.as_view(),
        name="stool_detail",
    ),
    path(
        "stool-samples/<slug:sample_id>/<slug:slide_number>/<slug:image_type>/upload",
        stool_sample_views.StoolSlideImageCreateView.as_view(),
        name="stool_slide_image_upload",
    ),
    path(
        "stool-samples/<slug:sample_id>/<slug:slide_number>/<slug:image_type>",
        stool_sample_views.StoolSlideImageDetailView.as_view(),
        name="stool_slide_image",
    ),
]
