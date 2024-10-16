import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.files.images import ImageFile
from django.db.models import Q, Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, FormView, ListView
from view_breadcrumbs import (
    BaseBreadcrumbMixin,
    CreateBreadcrumbMixin,
    DetailBreadcrumbMixin,
)

from django.core.exceptions import PermissionDenied

from address.forms import AddressForm
from sample.const import IMAGE_COUNT, IMAGE_TYPE_CHOICES, SLIDE_COUNT, DEFAULT_FILTER_RANGE_START
from sample.forms.standard_sample_form import SlideImagesForm, FilterForm
from sample.forms.vegetable_sample_forms import VegetableForm
from sample.models import Slide, SlideImage, Vegetable
from sample.utils import create_sample_id


# Create your views here
@method_decorator(never_cache, name="dispatch")
class VegetableListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    queryset = Vegetable.objects.order_by("-id")
    template_name: str = "sample/sample_home.html"
    context_object_name = "latest_samples_list"
    permission_required = "sample.view_vegetable"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        vegetable_objects = self.object_list
        context["total_samples"] = vegetable_objects.count()
        # images uploaded for vegetable sample, filter all slide images whose slide is a vegetable sample and has an image
        context["total_images_uploaded"] = SlideImage.objects.filter(
            ~Q(image=""),
            slide__vegetable_sample__isnull=False,
            slide__vegetable_sample__id__in=vegetable_objects,
        ).count()
        # images remaining to upload
        context["total_images_remaining"] = (
            context["total_samples"] * IMAGE_COUNT * SLIDE_COUNT * 2
        ) - context["total_images_uploaded"]
        # total approved images
        context["total_images_approved"] = SlideImage.objects.filter(
            ~Q(image=""),
            slide__vegetable_sample__isnull=False,
            approved=True,
            reviewed=True,
            slide__vegetable_sample__id__in=vegetable_objects,
        ).count()
        # total images pending approval
        context["total_images_pending_approval"] = SlideImage.objects.filter(
            ~Q(image=""),
            slide__vegetable_sample__isnull=False,
            reviewed=False,
            slide__vegetable_sample__id__in=vegetable_objects,
        ).count()
        context["total_images_rejected"] = SlideImage.objects.filter(
            ~Q(image=""),
            slide__vegetable_sample__isnull=False,
            approved=False,
            reviewed=True,
            slide__vegetable_sample__id__in=vegetable_objects,
        ).count()
        context["sample_type"] = "vegetable"
        default_range = self.start_date + " - " + self.end_date
        context["filter_form"] = FilterForm(
            default_range=default_range, province=self.province
        )
        return context

    def get_queryset(self, **kwargs):
        queryset = Vegetable.objects.all().order_by("-id")
        filter_range = self.request.GET.get("filter_date_range", "")
        if filter_range:
            self.start_date, self.end_date = filter_range.split(" - ")
            print(filter_range.split(" - "))
        else:
            self.start_date = self.request.GET.get("from", DEFAULT_FILTER_RANGE_START)
            today_date = datetime.datetime.today().strftime("%Y-%m-%d")
            self.end_date = self.request.GET.get("to", today_date)
        queryset = queryset.filter(
            date_of_collection__range=[self.start_date, self.end_date]
        )

        self.province = self.request.GET.get("province", "")
        user_provinces = self.request.user.profile.provinces.all()
        if self.province:
            if not user_provinces.filter(id=self.province):
                raise PermissionDenied(
                    f"No permission to view items from Province {self.province}"
                )
            queryset = queryset.filter(site__district__province__id=self.province)
        else:
            queryset = queryset.filter(site__district__province__id__in=user_provinces)

        queryset = queryset.annotate(
            total_uploaded=Count(
                "vegetable_slides__slide_image",
                Q(vegetable_slides__slide_image__isnull=False)
                & ~Q(vegetable_slides__slide_image__image=""),
            ),
            total_reviewed=Count(
                "vegetable_slides__slide_image",
                Q(vegetable_slides__slide_image__isnull=False)
                & Q(vegetable_slides__slide_image__reviewed=True),
            ),
        )
        return queryset


class VegetableFormView(
    LoginRequiredMixin, PermissionRequiredMixin, CreateBreadcrumbMixin, FormView
):
    sample_form_class = VegetableForm
    address_form_class = AddressForm
    template_name = "sample/vegetable_sample/vegetable_create.html"
    success_url = reverse_lazy("sample:vegetable_list")
    crumbs = [("Vegetable", success_url), ("New", "")]
    add_home = False
    permission_required = "sample.add_vegetable"

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
            vegetable_sample = sample_form.save(commit=False)
            vegetable_sample.user = request.user
            vegetable_sample.site = address_form.cleaned_data.get("municipality")
            vegetable_sample.ward = address_form.cleaned_data.get("ward")
            vegetable_sample.locality = address_form.cleaned_data.get("locality")
            vegetable_sample.sample_id = create_sample_id(
                "vegetable", vegetable_sample.date_of_collection, vegetable_sample.site
            )
            print(f"Saving sample {vegetable_sample}")
            vegetable_sample.save()
            for i in range(1, SLIDE_COUNT + 1):
                slide = Slide(vegetable_sample=vegetable_sample, slide_number=i)
                slide.save()
                for j in range(1, IMAGE_COUNT + 1):
                    for image_type, _ in IMAGE_TYPE_CHOICES:
                        slide_image = SlideImage(
                            uploaded_by=vegetable_sample.user,
                            slide=slide,
                            image="",
                            image_type=image_type,
                            image_id=f"{vegetable_sample}_S{i}_I{j}_{image_type}",
                            image_number=j,
                        )
                        slide_image.save()
            print(f"Finished creating sample {vegetable_sample}")
            messages.success(request, f"Added new vegetable sample {vegetable_sample}.")
            return redirect(self.success_url)

        return render(
            request,
            self.template_name,
            {"sample_form": sample_form, "address_form": address_form},
        )


@method_decorator(never_cache, name="dispatch")
class VegetableDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, DetailBreadcrumbMixin, DetailView
):
    template_name = "sample/vegetable_sample/vegetable_detail.html"
    slug_url_kwarg = "sample_id"
    slug_field = "sample_id"
    context_object_name = "sample"
    model = Vegetable
    breadcrumb_use_pk = False
    add_home = False
    permission_required = "sample.view_vegetable"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slides = Slide.objects.filter(vegetable_sample=self.get_object()).annotate(
            smartphone_images_count=Count(
                "slide_image",
                ~Q(slide_image__image="") & Q(slide_image__image_type="S"),
            ),
            smartphone_images_approved_count=Count(
                "slide_image",
                ~Q(slide_image__image="")
                & Q(slide_image__image_type="S")
                & Q(slide_image__approved=True)
                & Q(slide_image__reviewed=True),
            ),
            smartphone_images_rejected_count=Count(
                "slide_image",
                ~Q(slide_image__image="")
                & Q(slide_image__image_type="S")
                & Q(slide_image__approved=False)
                & Q(slide_image__reviewed=True),
            ),
            smartphone_images_not_reviewed_count=Count(
                "slide_image",
                ~Q(slide_image__image="")
                & Q(slide_image__image_type="S")
                & Q(slide_image__reviewed=False),
            ),
            brightfield_images_count=Count(
                "slide_image",
                ~Q(slide_image__image="") & Q(slide_image__image_type="B"),
            ),
            brightfield_images_approved_count=Count(
                "slide_image",
                ~Q(slide_image__image="")
                & Q(slide_image__image_type="B")
                & Q(slide_image__approved=True)
                & Q(slide_image__reviewed=True),
            ),
            brightfield_images_rejected_count=Count(
                "slide_image",
                ~Q(slide_image__image="")
                & Q(slide_image__image_type="B")
                & Q(slide_image__approved=False)
                & Q(slide_image__reviewed=True),
            ),
            brightfield_images_not_reviewed_count=Count(
                "slide_image",
                ~Q(slide_image__image="")
                & Q(slide_image__image_type="B")
                & Q(slide_image__reviewed=False),
            ),
        )
        context["slides"] = slides
        context["sample_type"] = "vegetable"
        return context


class VegetableSlideImageCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, BaseBreadcrumbMixin, FormView
):
    template_name = "sample/slide_create.html"
    form_class = SlideImagesForm
    success_url = reverse_lazy("sample:vegetable_list")
    crumbs = [
        ("Vegetable", reverse_lazy("sample:vegetable_list")),
    ]  # OR reverse_lazy
    add_home = False
    permission_required = ("sample.add_vegetable", "sample.add_slideimage")

    def dispatch(self, request, *args, **kwargs):
        self.crumbs = [
            ("Vegetable", reverse_lazy("sample:vegetable_list")),
            (
                self.kwargs["sample_id"],
                reverse_lazy(
                    "sample:vegetable_detail",
                    kwargs={"sample_id": self.kwargs["sample_id"]},
                ),
            ),
            (self.kwargs["slide_number"], ""),
            (self.kwargs["image_type"], ""),
            ("create", ""),
        ]
        self.success_url = reverse_lazy(
            "sample:vegetable_slide_image",
            kwargs={
                "sample_id": self.kwargs["sample_id"],
                "slide_number": self.kwargs["slide_number"],
                "image_type": self.kwargs["image_type"],
            },
        )
        return super(VegetableSlideImageCreateView, self).dispatch(
            request, *args, **kwargs
        )

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
            vegetable_sample = Vegetable.objects.get(sample_id=self.kwargs["sample_id"])
        except Vegetable.DoesNotExist:
            raise Http404(
                f"Sample {self.kwargs['sample_id']} is not valid. Please make sure you used the correct sample id."
            )
        context["slide"] = get_object_or_404(
            Slide,
            vegetable_sample=vegetable_sample,
            slide_number=int(self.kwargs["slide_number"]),
        )
        context["image_type"] = self.kwargs["image_type"]
        context["sample_id"] = self.kwargs["sample_id"]
        context["sample_type"] = "vegetable"
        print(context["slide"])
        return context

    def form_valid(self, form, **kwargs):
        vegetable_sample = Vegetable.objects.get(sample_id=self.kwargs["sample_id"])
        slide = get_object_or_404(
            Slide,
            vegetable_sample=vegetable_sample,
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


class VegetableSlideImageDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, BaseBreadcrumbMixin, ListView
):
    template_name = "sample/slide_detail.html"
    breadcrumb_use_pk = False
    crumbs = [
        ("Vegetable", reverse_lazy("sample:vegetable_list")),
    ]  # OR reverse_lazy
    context_object_name = "images"
    add_home = False
    permission_required = ("sample.view_vegetable", "sample.view_slideimage")

    def dispatch(self, request, *args, **kwargs):
        self.crumbs = [
            ("Vegetable", reverse_lazy("sample:vegetable_list")),
            (
                self.kwargs["sample_id"],
                reverse_lazy(
                    "sample:vegetable_detail",
                    kwargs={"sample_id": self.kwargs["sample_id"]},
                ),
            ),
            (self.kwargs["slide_number"], ""),
            (self.kwargs["image_type"], ""),
        ]
        return super(VegetableSlideImageDetailView, self).dispatch(
            request, *args, **kwargs
        )

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
            vegetable_sample = Vegetable.objects.get(sample_id=self.kwargs["sample_id"])
        except Vegetable.DoesNotExist:
            raise Http404(
                f"Sample {self.kwargs['sample_id']} is not valid. Please make sure you used the correct sample id."
            )
        db_image_type = "B" if self.kwargs["image_type"] == "brightfield" else "S"

        slide = Slide.objects.get(
            vegetable_sample=vegetable_sample, slide_number=self.kwargs["slide_number"]
        )
        return SlideImage.objects.all().filter(
            slide=slide,
            image_type=db_image_type,
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.kwargs["slide_number"] = int(self.kwargs["slide_number"])
        try:
            vegetable_sample = Vegetable.objects.get(sample_id=self.kwargs["sample_id"])
        except Vegetable.DoesNotExist:
            raise Http404(
                f"Sample {self.kwargs['sample_id']} is not valid. Please make sure you used the correct sample id."
            )
        context["slide"] = Slide.objects.get(
            vegetable_sample=vegetable_sample, slide_number=self.kwargs["slide_number"]
        )
        context["image_type"] = self.kwargs["image_type"]
        context["sample_type"] = "vegetable"
        return context
