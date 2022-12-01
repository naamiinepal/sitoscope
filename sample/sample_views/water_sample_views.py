from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.images import ImageFile
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView
from view_breadcrumbs import (
    BaseBreadcrumbMixin,
    CreateBreadcrumbMixin,
    DetailBreadcrumbMixin,
)

from address.forms import AddressForm
from sample.const import IMAGE_COUNT, IMAGE_TYPE_CHOICES, SLIDE_COUNT
from sample.forms.standard_sample_form import SlideImagesForm
from sample.forms.water_sample_forms import WaterForm
from sample.models import Slide, SlideImage, Water
from sample.utils import create_sample_id


# Create your views here
class WaterListView(LoginRequiredMixin, BaseBreadcrumbMixin, ListView):
    queryset = Water.objects.order_by("-id")
    template_name: str = "sample/sample_home.html"
    context_object_name = "latest_samples_list"
    crumbs = [("Water", reverse_lazy("sample:water_list"))]  # OR reverse_lazy

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sample_type"] = "water"
        return context


class WaterFormView(LoginRequiredMixin, CreateBreadcrumbMixin, FormView):
    sample_form_class = WaterForm
    address_form_class = AddressForm
    template_name = "sample/water_sample/water_create.html"
    success_url = reverse_lazy("sample:water_list")
    crumbs = [("Water", success_url), ("New", "")]

    def get(self, request, *args, **kwargs):
        sample_form = self.sample_form_class()
        address_form = self.address_form_class()
        return render(
            request,
            self.template_name,
            {"sample_form": sample_form, "address_form": address_form},
        )

    def post(self, request, *args, **kwargs):
        sample_form = self.sample_form_class(request.POST, request.FILES)
        address_form = self.address_form_class(request.POST)
        if sample_form.is_valid() and address_form.is_valid():
            water_sample = sample_form.save(commit=False)
            water_sample.user = request.user
            water_sample.site = address_form.cleaned_data.get("municipality")
            water_sample.ward = address_form.cleaned_data.get("ward")
            water_sample.locality = address_form.cleaned_data.get("locality")
            water_sample.sample_id = create_sample_id(
                "water", water_sample.date_of_collection, water_sample.site
            )
            print(f"Saving sample {water_sample}")
            water_sample.save()
            for i in range(1, SLIDE_COUNT + 1):
                slide = Slide(water_sample=water_sample, slide_number=i + 1)
                slide.save()
                for j in range(1, IMAGE_COUNT + 1):
                    for image_type, _ in IMAGE_TYPE_CHOICES:
                        slide_image = SlideImage(
                            uploaded_by=water_sample.user,
                            slide=slide,
                            image="",
                            image_type=image_type,
                            image_id=f"{water_sample}_S{i}_I{j}_{image_type}",
                            image_number=j,
                        )
                        slide_image.save()
            print(f"Finished creating sample {water_sample}")
            messages.success(request, f"Added new water sample {water_sample}.")
            return redirect(self.success_url)

        return render(
            request,
            self.template_name,
            {"sample_form": sample_form, "address_form": address_form},
        )


class WaterDetailView(LoginRequiredMixin, DetailBreadcrumbMixin, DetailView):
    template_name = "sample/water_sample/water_detail.html"
    slug_url_kwarg = "sample_id"
    slug_field = "sample_id"
    context_object_name = "sample"
    model = Water
    breadcrumb_use_pk = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slides = Slide.objects.filter(water_sample=self.get_object())
        for slide in slides:
            slide.smartphone_images_count = SlideImage.objects.filter(
                ~Q(image=""), slide=slide.id, image_type="S"
            ).count()
            slide.brightfield_images_count = SlideImage.objects.filter(
                ~Q(image=""), slide=slide.id, image_type="B"
            ).count()
        context["slides"] = slides
        context["sample_type"] = "water"
        return context


class WaterSlideImageCreateView(LoginRequiredMixin, BaseBreadcrumbMixin, FormView):
    template_name = "sample/slide_create.html"
    form_class = SlideImagesForm
    success_url = reverse_lazy("sample:water_list")
    crumbs = [
        ("Water", reverse_lazy("sample:water_list")),
    ]  # OR reverse_lazy

    def dispatch(self, request, *args, **kwargs):
        self.crumbs = [
            ("Water", reverse_lazy("sample:water_list")),
            (
                self.kwargs["sample_id"],
                reverse_lazy(
                    "sample:water_detail",
                    kwargs={"sample_id": self.kwargs["sample_id"]},
                ),
            ),
            (self.kwargs["slide_number"], ""),
            (self.kwargs["image_type"], ""),
            ("create", ""),
        ]
        self.success_url = reverse_lazy(
            "sample:water_slide_image",
            kwargs={
                "sample_id": self.kwargs["sample_id"],
                "slide_number": self.kwargs["slide_number"],
                "image_type": self.kwargs["image_type"],
            },
        )
        return super(WaterSlideImageCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.kwargs["slide_number"] = int(self.kwargs["slide_number"])
        if self.kwargs["image_type"] not in ["smartphone", "brightfield"]:
            raise Http404(
                f"Image type {self.kwargs['image_type']} is not valid. Please use alid image types: ('smartphone', 'brightfield)"
            )
        if self.kwargs["slide_number"] < 1 or self.kwargs["slide_number"] > 3:
            raise Http404(
                f"Slide number {self.kwargs['slide_number']} is not valid. Valid slide numbers: (1, 2, 3)"
            )
        try:
            water_sample = Water.objects.get(sample_id=self.kwargs["sample_id"])
        except Water.DoesNotExist:
            raise Http404(
                f"Sample {self.kwargs['sample_id']} is not valid. Please make sure you used the correct sample id."
            )
        context["slide"] = get_object_or_404(
            Slide,
            water_sample=water_sample,
            slide_number=int(self.kwargs["slide_number"]),
        )
        context["image_type"] = self.kwargs["image_type"]
        context["sample_id"] = self.kwargs["sample_id"]
        context["sample_type"] = "water"
        print(context["slide"])
        return context

    def form_valid(self, form, **kwargs):
        water_sample = Water.objects.get(sample_id=self.kwargs["sample_id"])
        slide = get_object_or_404(
            Slide,
            water_sample=water_sample,
            slide_number=int(self.kwargs["slide_number"]),
        )
        db_image_type = "B" if self.kwargs["image_type"] == "brightfield" else "S"
        db_images = SlideImage.objects.all().filter(
            slide=slide,
            image_type=db_image_type,
        )
        files = self.request.FILES.getlist("images")
        for file, image in zip(files, db_images):
            print(file)
            slide_image = SlideImage(
                pk=image.pk,
                uploaded_by=self.request.user,
                slide=image.slide,
                image=ImageFile(file),
                image_id=image.image_id,
                image_number=image.image_number,
                image_type=db_image_type,
            )
            slide_image.save()
        messages.success(self.request, "Successfully added images.")
        return super().form_valid(form)


class WaterSlideImageDetailView(LoginRequiredMixin, BaseBreadcrumbMixin, ListView):
    template_name = "sample/slide_detail.html"
    breadcrumb_use_pk = False
    crumbs = [
        ("Water", reverse_lazy("sample:water_list")),
    ]  # OR reverse_lazy
    context_object_name = "images"

    def dispatch(self, request, *args, **kwargs):
        self.crumbs = [
            ("Water", reverse_lazy("sample:water_list")),
            (
                self.kwargs["sample_id"],
                reverse_lazy(
                    "sample:water_detail",
                    kwargs={"sample_id": self.kwargs["sample_id"]},
                ),
            ),
            (self.kwargs["slide_number"], ""),
            (self.kwargs["image_type"], ""),
        ]
        return super(WaterSlideImageDetailView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.kwargs["slide_number"] = int(self.kwargs["slide_number"])
        if self.kwargs["image_type"] not in ["smartphone", "brightfield"]:
            raise Http404(
                f"Image type {self.kwargs['image_type']} is not valid. Please use alid image types: ('smartphone', 'brightfield)"
            )
        if self.kwargs["slide_number"] < 1 or self.kwargs["slide_number"] > 3:
            raise Http404(
                f"Slide number {self.kwargs['slide_number']} is not valid. Valid slide numbers: (1, 2, 3)"
            )
        try:
            water_sample = Water.objects.get(sample_id=self.kwargs["sample_id"])
        except Water.DoesNotExist:
            raise Http404(
                f"Sample {self.kwargs['sample_id']} is not valid. Please make sure you used the correct sample id."
            )
        db_image_type = "B" if self.kwargs["image_type"] == "brightfield" else "S"

        slide = Slide.objects.get(
            water_sample=water_sample, slide_number=self.kwargs["slide_number"]
        )
        return SlideImage.objects.all().filter(
            slide=slide,
            image_type=db_image_type,
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.kwargs["slide_number"] = int(self.kwargs["slide_number"])
        try:
            water_sample = Water.objects.get(sample_id=self.kwargs["sample_id"])
        except Water.DoesNotExist:
            raise Http404(
                f"Sample {self.kwargs['sample_id']} is not valid. Please make sure you used the correct sample id."
            )
        context["slide"] = Slide.objects.get(
            water_sample=water_sample, slide_number=self.kwargs["slide_number"]
        )
        context["image_type"] = self.kwargs["image_type"]
        context["sample_type"] = "water"
        return context
