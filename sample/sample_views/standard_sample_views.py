from django.shortcuts import render, redirect
from sample.models import Standard, Slide, SlideImage
from sample.const import IMAGE_TYPE_CHOICES, SLIDE_COUNT, IMAGE_COUNT
from django.http import HttpRequest, Http404
from django.contrib.auth.decorators import login_required
from sample.forms.standard_sample_form import (
    StandardForm,
    SlideImagesForm,
)
from django.core.files.images import ImageFile
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models import Q
import uuid


# Create your views here
def standard_home(request: HttpRequest):
    latest_samples_list = Standard.objects.order_by("-id")[:5]
    context = {"latest_samples_list": latest_samples_list}
    return render(request, "sample/standard_sample_home.html", context)


def create_standard_sample_id(date):
    # Utility to create standard sample id
    sample_number = str(uuid.uuid4())[:5]
    return f"Standard_{date.strftime('%Y%m%d')}_{sample_number}"


@login_required
def get_standard_form(request):
    if request.method == "POST":
        form = StandardForm(request.POST)
        if form.is_valid():
            validated_data = form.cleaned_data
            print(type(validated_data["date_of_collection"]))
            validated_data.update({"user": request.user})
            validated_data.update(
                {
                    "sample_id": create_standard_sample_id(
                        validated_data.get("date_of_collection")
                    )
                }
            )
            standard_sample = Standard(**validated_data)
            print(f"Saving sample {standard_sample}")
            standard_sample.save()
            for i in range(SLIDE_COUNT):
                slide = Slide(standard_sample=standard_sample, slide_number=i + 1)
                print(f"Saving slide {slide}")
                slide.save()
                for j in range(IMAGE_COUNT):
                    for image_type, _ in IMAGE_TYPE_CHOICES:
                        slide_image = SlideImage(
                            uploaded_by=validated_data.get("user"),
                            slide=slide,
                            image="",
                            image_type=image_type,
                            image_id=f"{standard_sample}_S{i+1}_I{j+1}_{image_type}",
                            image_number=j + 1,
                        )
                        print(f"Saving image {slide_image}")
                        slide_image.save()
            print(f"Finished creating sample {standard_sample}")
            messages.success(request, "Changes successfully saved.")
            return redirect("sample:standard_samples_home")

    else:
        form = StandardForm()

    return render(request, "sample/standard_sample_form.html", {"form": form})


@login_required
def standard_sample_detail(request, sample_id=None):
    standard_sample = get_object_or_404(Standard, sample_id=sample_id)
    slides = Slide.objects.filter(standard_sample=standard_sample)
    for slide in slides:
        smartphone_images_count = SlideImage.objects.filter(
            ~Q(image=""), slide=slide.id, image_type="S"
        ).count()
        brightfield_images_count = SlideImage.objects.filter(
            ~Q(image=""), slide=slide.id, image_type="B"
        ).count()
        slide.smartphone_images_count = smartphone_images_count
        slide.brightfield_images_count = brightfield_images_count
    context = {"standard_sample": standard_sample, "slides": slides}

    return render(request, "sample/standard_sample_detail.html", context)


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
    show_form = False if db_images.filter(~Q(image="")).count() == 15 else True

    form = SlideImagesForm()
    if request.method == "POST":
        form = SlideImagesForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist("images")
            if len(files) != 15:
                raise Http404("Number of images must be exactly 15.")
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
    }
    return render(request, "sample/standard_slide_image_upload_form.html", context)
