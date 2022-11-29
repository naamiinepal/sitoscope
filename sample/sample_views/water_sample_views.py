from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.images import ImageFile
from django.db.models import Q
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from address.forms import AddressForm
from sample.const import IMAGE_COUNT, IMAGE_TYPE_CHOICES, SLIDE_COUNT
from sample.forms.standard_sample_form import SlideImagesForm
from sample.forms.water_sample_forms import WaterForm
from sample.models import Slide, SlideImage, Water
from sample.utils import create_sample_id


# Create your views here
@login_required
def water_home(request: HttpRequest):
    latest_samples_list = Water.objects.order_by("-id")[:5]
    context = {"latest_samples_list": latest_samples_list, "sample_type": "water"}
    return render(request, "sample/sample_home.html", context)


@login_required
def get_water_form(request):
    address_form = AddressForm(request.POST or None)
    if request.method == "POST":
        sample_form = WaterForm(request.POST, request.FILES)
        if sample_form.is_valid() and address_form.is_valid():
            validated_data = sample_form.cleaned_data
            validated_data.update({"user": request.user})
            validated_data.update(
                {
                    "site": address_form.cleaned_data.get("municipality"),
                    "ward": address_form.cleaned_data.get("ward"),
                    "locality": address_form.cleaned_data.get("locality"),
                }
            )
            validated_data.update(
                {
                    "sample_id": create_sample_id(
                        "water",
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
        sample_form = WaterForm()

    return render(
        request,
        "sample/water_sample/water_sample_form.html",
        {"sample_form": sample_form, "address_form": address_form},
    )


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
    context = {"sample": water_sample, "slides": slides, "sample_type": "water"}

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
    show_form = db_images.filter(~Q(image="")).count() != 15

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
        "sample_type": "water",
    }
    return render(request, "sample/slide_image_upload_form.html", context)
