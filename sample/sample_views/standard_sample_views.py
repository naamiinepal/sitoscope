from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.images import ImageFile
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from sample.const import IMAGE_COUNT, IMAGE_TYPE_CHOICES, SLIDE_COUNT
from sample.forms.standard_sample_form import SlideImagesForm, StandardForm
from sample.models import Slide, SlideImage, Standard
from sample.utils import create_sample_id


# Create your views here
class StandardListView(LoginRequiredMixin, ListView):
    queryset = Standard.objects.order_by("-date_of_collection")
    template_name: str = "sample/sample_home.html"
    context_object_name = "latest_samples_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sample_type"] = "standard"
        return context


class StandardFormView(LoginRequiredMixin, View):
    form_class = StandardForm
    template_name = "sample/standard_sample/standard_sample_form.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            standard_sample = form.save(commit=False)
            standard_sample.user = request.user
            standard_sample.sample_id = create_sample_id(
                "standard", standard_sample.date_of_collection
            )
            print(f"Saving sample {standard_sample}")
            standard_sample.save()

            # Create Slides and SlideImage entries in the database
            for i in range(SLIDE_COUNT):
                slide = Slide(standard_sample=standard_sample, slide_number=i + 1)
                slide.save()
                for j in range(IMAGE_COUNT):
                    for image_type, _ in IMAGE_TYPE_CHOICES:
                        slide_image = SlideImage(
                            uploaded_by=standard_sample.user,
                            slide=slide,
                            image="",
                            image_type=image_type,
                            image_id=f"{standard_sample}_S{i+1}_I{j+1}_{image_type}",
                            image_number=j + 1,
                        )
                        slide_image.save()
            print(f"Finished creating sample {standard_sample}")
            messages.success(
                request, f"Standard sample {standard_sample} successfully saved."
            )
            return redirect("sample:standard_samples_home")

        return render(request, self.template_name, {"form": form})


class StandardDetailView(LoginRequiredMixin, DetailView):
    template_name = "sample/standard_sample/standard_sample_detail.html"
    slug_url_kwarg = "sample_id"
    slug_field = "sample_id"
    context_object_name = "sample"
    model = Standard

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


@login_required
def standard_slide_image_details(
    request, sample_id=None, slide_number=1, image_type="smartphone"
):
    if image_type not in ["smartphone", "brightfield"]:
        raise Http404(
            f"Image type {image_type} is not valid. Please use alid image types: ('smartphone', 'brightfield)"
        )
    if slide_number < 1 or slide_number > 3:
        raise Http404(
            f"Slide number {slide_number} is not valid. Valid slide numbers: (1, 2, 3)"
        )
    try:
        standard_sample = Standard.objects.get(sample_id=sample_id)
    except Standard.DoesNotExist:
        raise Http404(
            f"Sample {sample_id} is not valid. Please make sure you used the correct sample id."
        )
    slide = Slide.objects.get(
        standard_sample=standard_sample, slide_number=slide_number
    )
    db_image_type = "B" if image_type == "brightfield" else "S"
    db_images = SlideImage.objects.all().filter(
        slide=slide,
        image_type=db_image_type,
    )
    show_form = db_images.filter(~Q(image="")).count() != 15

    form = SlideImagesForm()
    if request.method == "POST":
        form = SlideImagesForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist("images")
            print("Lenghts", len(files), len(db_images))
            for file, image in zip(files, db_images):
                slide_image = SlideImage(
                    pk=image.pk,
                    uploaded_by=request.user,
                    slide=slide,
                    image=ImageFile(file),
                    image_id=image.image_id,
                    image_number=image.image_number,
                    image_type=db_image_type,
                )
                slide_image.save()
            return redirect(request.path_info)

    context = {
        "image_type": image_type,
        "sample_id": sample_id,
        "slide": slide,
        "form": form,
        "images": db_images,
        "show_form": show_form,
        "sample_type": "standard",
    }
    return render(request, "sample/slide_image_upload_form.html", context)
