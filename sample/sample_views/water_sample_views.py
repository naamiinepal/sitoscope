from django.shortcuts import render, redirect
from sample.models import Water, Slide, SlideImage

from sample.const import IMAGE_TYPE_CHOICES, SLIDE_COUNT, IMAGE_COUNT
from django.http import HttpRequest, Http404
from django.contrib.auth.decorators import login_required
from sample.forms.water_sample_forms import WaterForm
from sample.forms.standard_sample_form import SlideImagesForm

from django.core.files.images import ImageFile
from django.contrib import messages

from django.shortcuts import get_object_or_404

from django.db.models import Q
import uuid


# Create your views here
@login_required
def water_home(request: HttpRequest):
    latest_samples_list = Water.objects.order_by("-id")[:5]
    context = {"latest_samples_list": latest_samples_list}
    return render(request, "sample/water_sample/water_sample_home.html", context)


def create_water_sample_id(date, municipality):
    # Utility to create water sample id
    site = f"{municipality.district.province.code}-{municipality.name}"
    sample_number = str(uuid.uuid4())[:5]
    return f"W_{site}_{date.strftime('%Y%m%d')}_{sample_number}"


@login_required
def get_water_form(request):
    if request.method == "POST":
        form = WaterForm(request.POST, request.FILES)
        if form.is_valid():
            validated_data = form.cleaned_data
            validated_data.update({"user": request.user})
            validated_data.update(
                {
                    "sample_id": create_water_sample_id(
                        validated_data.get("date_of_collection"),
                        validated_data.get("site"),
                    )
                }
            )
            water_sample = Water(**validated_data)
            print(f"Saving sample {water_sample}")
            water_sample.save()
            for i in range(SLIDE_COUNT):
                slide = Slide(water_sample=water_sample, slide_number=i + 1)
                print(f"Saving slide {slide}")
                slide.save()
                for j in range(IMAGE_COUNT):
                    for image_type, _ in IMAGE_TYPE_CHOICES:
                        slide_image = SlideImage(
                            uploaded_by=validated_data.get("user"),
                            slide=slide,
                            image="",
                            image_type=image_type,
                            image_id=f"{water_sample}_S{i+1}_I{j+1}_{image_type}",
                            image_number=j + 1,
                        )
                        print(f"Saving image {slide_image}")
                        slide_image.save()
            print(f"Finished creating sample {water_sample}")
            messages.success(request, f"Added new water sample {water_sample}.")
            return redirect("sample:water_samples_home")

    else:
        form = WaterForm()

    return render(request, "sample/water_sample/water_sample_form.html", {"form": form})


@login_required
def water_sample_detail(request, sample_id=None):
    water_sample = get_object_or_404(Water, sample_id=sample_id)
    slides = Slide.objects.filter(water_sample=water_sample)
    for slide in slides:
        smartphone_images_count = SlideImage.objects.filter(
            ~Q(image=""), slide=slide.id, image_type="S"
        ).count()
        brightfield_images_count = SlideImage.objects.filter(
            ~Q(image=""), slide=slide.id, image_type="B"
        ).count()
        slide.smartphone_images_count = smartphone_images_count
        slide.brightfield_images_count = brightfield_images_count
    context = {"water_sample": water_sample, "slides": slides}

    return render(request, "sample/water_sample/water_sample_detail.html", context)


@login_required
def water_slide_image_details(
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
        water_sample = Water.objects.get(sample_id=sample_id)
    except Water.DoesNotExist:
        raise Http404(
            f"Sample {sample_id} is not valid. Please make sure you used the correct sample id."
        )
    slide = Slide.objects.get(water_sample=water_sample, slide_number=slide_number)
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
                messages.error(request, "Number of images must be exactly 15.")
                return redirect(request.path_info)
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
    return render(
        request, "sample/water_sample/water_slide_image_upload_form.html", context
    )
