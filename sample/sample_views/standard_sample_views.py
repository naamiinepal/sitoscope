from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.images import ImageFile
from django.db.models import Q
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from sample.const import IMAGE_COUNT, IMAGE_TYPE_CHOICES, SLIDE_COUNT
from sample.forms.standard_sample_form import SlideImagesForm, StandardForm
from sample.models import Slide, SlideImage, Standard
from sample.utils import create_sample_id


# Create your views here
def standard_home(request: HttpRequest):
    latest_samples_list = Standard.objects.order_by("-id")[:5]
    context = {"latest_samples_list": latest_samples_list, "sample_type": "standard"}
    return render(request, "sample/sample_home.html", context)


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
                    "sample_id": create_sample_id(
                        "standard", validated_data.get("date_of_collection")
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
            messages.success(
                request, f"Standard sample {standard_sample} successfully saved."
            )
            return redirect("sample:standard_samples_home")

    else:
        form = StandardForm()

    return render(
        request, "sample/standard_sample/standard_sample_form.html", {"form": form}
    )


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
    context = {
        "sample": standard_sample,
        "slides": slides,
        "sample_type": "standard",
    }

    return render(
        request, "sample/standard_sample/standard_sample_detail.html", context
    )


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
        "sample_type": "standard",
    }
    return render(request, "sample/slide_image_upload_form.html", context)
