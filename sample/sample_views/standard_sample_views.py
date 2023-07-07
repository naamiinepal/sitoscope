from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.files.images import ImageFile
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, FormView, ListView
from view_breadcrumbs import (
    BaseBreadcrumbMixin,
    CreateBreadcrumbMixin,
    DetailBreadcrumbMixin,
)

from sample.const import IMAGE_COUNT, IMAGE_TYPE_CHOICES, STANDARD_SAMPLE_SLIDE_COUNT
from sample.forms.standard_sample_form import SlideImagesForm, StandardForm
from sample.models import Slide, SlideImage, Standard
from sample.utils import create_standard_sample_id


# Create your views here
@method_decorator(never_cache, name="dispatch")
class StandardListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    queryset = Standard.objects.order_by("-id")
    template_name: str = "sample/sample_home.html"
    context_object_name = "latest_samples_list"
    permission_required = "sample.view_standard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sample_type"] = "standard"
        context["total_samples"] = Standard.objects.count()

        context["total_images_uploaded"] = SlideImage.objects.filter(
            ~Q(image=""), slide__standard_sample__isnull=False
        ).count()
        # images remaining to upload
        context["total_images_remaining"] = (
            context["total_samples"] * IMAGE_COUNT * STANDARD_SAMPLE_SLIDE_COUNT * 2
        ) - context["total_images_uploaded"]
        # total approved images
        context["total_images_approved"] = SlideImage.objects.filter(
            ~Q(image=""),
            slide__standard_sample__isnull=False,
            approved=True,
        ).count()
        # total images pending approval
        context["total_images_pending_approval"] = (
            context["total_images_uploaded"] - context["total_images_approved"]
        )
        return context


class StandardFormView(
    LoginRequiredMixin, PermissionRequiredMixin, CreateBreadcrumbMixin, FormView
):
    form_class = StandardForm
    template_name = "sample/standard_sample/standard_create.html"
    success_url = reverse_lazy("sample:standard_list")
    crumbs = [("Standard", success_url), ("New", "")]
    add_home = False
    permission_required = ("sample.add_standard", "sample.change_standard")

    def form_valid(self, form):
        standard_sample = form.save(commit=False)
        standard_sample.user = self.request.user
        standard_sample.sample_id = create_standard_sample_id(
            standard_sample.date_of_collection,
            standard_sample.sample_type,
            standard_sample.dilution_factor,
        )
        print(f"Saving sample {standard_sample}")
        standard_sample.save()

        # Create Slides and SlideImage entries in the database
        for i in range(1, STANDARD_SAMPLE_SLIDE_COUNT + 1):
            slide = Slide(standard_sample=standard_sample, slide_number=i)
            slide.save()
            for j in range(1, IMAGE_COUNT + 1):
                for image_type, _ in IMAGE_TYPE_CHOICES:
                    slide_image = SlideImage(
                        uploaded_by=standard_sample.user,
                        slide=slide,
                        image="",
                        image_type=image_type,
                        image_id=f"{standard_sample}_S{i}_I{j}_{image_type}",
                        image_number=j,
                    )
                    slide_image.save()
        print(f"Finished creating sample {standard_sample}")
        messages.success(
            self.request, f"Standard sample {standard_sample} successfully saved."
        )
        return super().form_valid(form)


@method_decorator(never_cache, name="dispatch")
class StandardDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, DetailBreadcrumbMixin, DetailView
):
    template_name = "sample/standard_sample/standard_detail.html"
    slug_url_kwarg = "sample_id"
    slug_field = "sample_id"
    context_object_name = "sample"
    model = Standard
    breadcrumb_use_pk = False
    add_home = False
    permission_required = "sample.view_standard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slides = Slide.objects.filter(standard_sample=self.get_object())
        for slide in slides:
            slide.smartphone_images_count = SlideImage.objects.filter(
                ~Q(image=""), slide=slide.id, image_type="S"
            ).count()
            slide.brightfield_images_count = SlideImage.objects.filter(
                ~Q(image=""), slide=slide.id, image_type="B"
            ).count()
        context["slides"] = slides
        context["sample_type"] = "standard"
        return context


class StandardSlideImageCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, BaseBreadcrumbMixin, FormView
):
    template_name = "sample/slide_create.html"
    form_class = SlideImagesForm
    success_url = reverse_lazy("sample:standard_list")
    crumbs = [
        ("Standard", reverse_lazy("sample:standard_list")),
    ]  # OR reverse_lazy
    add_home = False
    permission_required = ("sample.add_standard", "sample.add_slideimage")

    def dispatch(self, request, *args, **kwargs):
        self.crumbs = [
            ("Standard", reverse_lazy("sample:standard_list")),
            (
                self.kwargs["sample_id"],
                reverse_lazy(
                    "sample:standard_detail",
                    kwargs={"sample_id": self.kwargs["sample_id"]},
                ),
            ),
            (self.kwargs["slide_number"], ""),
            (self.kwargs["image_type"], ""),
            ("create", ""),
        ]
        self.success_url = reverse_lazy(
            "sample:standard_slide_image",
            kwargs={
                "sample_id": self.kwargs["sample_id"],
                "slide_number": self.kwargs["slide_number"],
                "image_type": self.kwargs["image_type"],
            },
        )
        return super(StandardSlideImageCreateView, self).dispatch(
            request, *args, **kwargs
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.kwargs["slide_number"] = int(self.kwargs["slide_number"])
        if self.kwargs["image_type"] not in ["smartphone", "brightfield"]:
            raise Http404(
                f"Image type {self.kwargs['image_type']} is not valid. Please use alid image types: ('smartphone', 'brightfield)"
            )
        if self.kwargs["slide_number"] < 1 or self.kwargs["slide_number"] > 25:
            raise Http404(
                f"Slide number {self.kwargs['slide_number']} is not valid. Valid slide numbers: (1 to 25)"
            )
        try:
            standard_sample = Standard.objects.get(sample_id=self.kwargs["sample_id"])
        except Standard.DoesNotExist:
            raise Http404(
                f"Sample {self.kwargs['sample_id']} is not valid. Please make sure you used the correct sample id."
            )
        context["slide"] = get_object_or_404(
            Slide,
            standard_sample=standard_sample,
            slide_number=int(self.kwargs["slide_number"]),
        )
        context["image_type"] = self.kwargs["image_type"]
        context["sample_id"] = self.kwargs["sample_id"]
        context["sample_type"] = "standard"
        print(context["slide"])
        return context

    def form_valid(self, form, **kwargs):
        standard_sample = Standard.objects.get(sample_id=self.kwargs["sample_id"])
        slide = get_object_or_404(
            Slide,
            standard_sample=standard_sample,
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


class StandardSlideImageDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, BaseBreadcrumbMixin, ListView
):
    template_name = "sample/slide_detail.html"
    breadcrumb_use_pk = False
    crumbs = [
        ("Standard", reverse_lazy("sample:standard_list")),
    ]  # OR reverse_lazy
    context_object_name = "images"
    add_home = False
    permission_required = ("sample.view_standard", "sample.view_slideimage")

    def dispatch(self, request, *args, **kwargs):
        self.crumbs = [
            ("Standard", reverse_lazy("sample:standard_list")),
            (
                self.kwargs["sample_id"],
                reverse_lazy(
                    "sample:standard_detail",
                    kwargs={"sample_id": self.kwargs["sample_id"]},
                ),
            ),
            (self.kwargs["slide_number"], ""),
            (self.kwargs["image_type"], ""),
        ]
        return super(StandardSlideImageDetailView, self).dispatch(
            request, *args, **kwargs
        )

    def get_queryset(self):
        self.kwargs["slide_number"] = int(self.kwargs["slide_number"])
        if self.kwargs["image_type"] not in ["smartphone", "brightfield"]:
            raise Http404(
                f"Image type {self.kwargs['image_type']} is not valid. Please use alid image types: ('smartphone', 'brightfield)"
            )
        if self.kwargs["slide_number"] < 1 or self.kwargs["slide_number"] > 25:
            raise Http404(
                f"Slide number {self.kwargs['slide_number']} is not valid. Valid slide numbers: (1 to 25)"
            )
        try:
            standard_sample = Standard.objects.get(sample_id=self.kwargs["sample_id"])
        except Standard.DoesNotExist:
            raise Http404(
                f"Sample {self.kwargs['sample_id']} is not valid. Please make sure you used the correct sample id."
            )
        db_image_type = "B" if self.kwargs["image_type"] == "brightfield" else "S"

        slide = Slide.objects.get(
            standard_sample=standard_sample, slide_number=self.kwargs["slide_number"]
        )
        return SlideImage.objects.all().filter(
            slide=slide,
            image_type=db_image_type,
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.kwargs["slide_number"] = int(self.kwargs["slide_number"])
        try:
            standard_sample = Standard.objects.get(sample_id=self.kwargs["sample_id"])
        except Standard.DoesNotExist:
            raise Http404(
                f"Sample {self.kwargs['sample_id']} is not valid. Please make sure you used the correct sample id."
            )
        context["slide"] = Slide.objects.get(
            standard_sample=standard_sample, slide_number=self.kwargs["slide_number"]
        )
        context["image_type"] = self.kwargs["image_type"]
        context["sample_type"] = "standard"
        return context
