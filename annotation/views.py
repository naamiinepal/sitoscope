from datetime import datetime
from json import dumps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from annotation.models import Annotation, Annotator
from sample.models import SlideImage

from .const import LABELS


# only show the annotation home page if the user is an annotator
@login_required
@never_cache
def annotation_home(request: HttpRequest):
    try:
        Annotator.objects.get(user=request.user)
    except Annotator.DoesNotExist:
        # 403 Forbidden
        return render(request, "403.html")

    annotations = Annotation.objects.filter(
        annotator__user=request.user, annotated=True
    ).prefetch_related("image")

    not_annotated_images = Annotation.objects.filter(
        annotator__user=request.user, annotated=False
    ).prefetch_related("image")

    # filter out smartphone and brightfield images
    brightfield_annotated = annotations.exclude(image__image_type="S")
    brightfield_not_annotated = not_annotated_images.exclude(image__image_type="S")

    smartphone_annotated = annotations.exclude(image__image_type="B")
    smartphone_not_annotated = not_annotated_images.exclude(image__image_type="B")

    annotated_count_brightfield = brightfield_annotated.count()
    not_annotated_count_brightfield = brightfield_not_annotated.count()

    annotated_count_smartphone = smartphone_annotated.count()
    not_annotated_count_smartphone = smartphone_not_annotated.count()

    context = {
        "images": {
            "brightfield_annotated": brightfield_annotated,
            "brightfield_not_annotated": brightfield_not_annotated,
            "smartphone_annotated": smartphone_annotated,
            "smartphone_not_annotated": smartphone_not_annotated,
            "annotated_count_brightfield": annotated_count_brightfield,
            "not_annotated_count_brightfield": not_annotated_count_brightfield,
            "annotated_count_smartphone": annotated_count_smartphone,
            "not_annotated_count_smartphone": not_annotated_count_smartphone,
        },
        "media_path": settings.MEDIA_URL,
    }

    return render(request, "annotation/annotation_home.html", context=context)


@login_required
def via_get(request: HttpRequest, img: str) -> HttpResponse:
    user = request.user
    try:
        annotator = Annotator.objects.get(user=user)
    except Annotator.DoesNotExist:
        return HttpRequest(status=403, content="You are not an annotator.")

    try:
        image = SlideImage.objects.get(image_id=img)
    except SlideImage.DoesNotExist:
        return HttpResponse(status=404, content="Image not found.")

    try:
        annotation = Annotation.objects.get(image=image, annotator=annotator)
    except Annotation.DoesNotExist:
        return HttpResponse(
            status=404,
            content="Either the annotation does not exist or you are not assigned this annotation.",
        )

    context = {
        "annotation_url": annotation.label_file,
        "media_path": settings.MEDIA_URL,
        "labels": dumps(LABELS),
        "has_cyst": annotation.has_cyst,
    }

    return render(
        request=request, template_name="annotation/via_annotation.html", context=context
    )


@login_required
@csrf_exempt
def via_post(request: HttpRequest) -> HttpResponse:
    try:
        image_id = request.POST["img"]
        print(image_id)
        img = SlideImage.objects.get(image_id=image_id)
        user = request.user
        username = user.username
        json_file = request.FILES["label_file"]
        # json_obj = loads(json_file.read())
        # regions = list(json_obj.values())[0]["regions"]
        # used_labels = []

        # for r in regions:
        #     attr = list(r["region_attributes"].values())[0]
        #     used_labels.append(attr)
        # used_labels = list(set(used_labels))
        # used_labels = Label.objects.filter(name__in=used_labels)
        annotator = Annotator.objects.get(user=user)
        try:
            annot_obj = Annotation.objects.get(annotator=annotator, image=img)
            annot_obj.label_file.delete()
            annot_obj.label_file = File(json_file, f"{image_id}_{username}.json")
            annot_obj.has_cyst = True
            annot_obj.annotated = True
            annot_obj.annotated_on = datetime.now()
            # annot_obj.labels.set(used_labels)
            annot_obj.save()

        except ObjectDoesNotExist:
            annot_obj = Annotation.objects.create(annotator=annotator, image=img)
            annot_obj.label_file = File(json_file, f"{image_id}_{username}.json")
            annot_obj.has_cyst = True
            annot_obj.annotated = True
            annot_obj.annotated_on = datetime.now()
            # annot_obj.labels.set(used_labels)
            annot_obj.save()

        return JsonResponse({"message": "Annotations Sync Successful"})

    except ObjectDoesNotExist:
        return HttpResponse(
            '<div> <h2>Sorry the image does not exist.</h2> <a href="/dashboard"> Go to Dashboard</a> </div>'
        )


@login_required
@csrf_exempt
def no_cyst_present(request: HttpRequest) -> HttpResponse:
    image_id = request.POST["img"]
    try:
        img = SlideImage.objects.get(image_id=image_id)
    except ObjectDoesNotExist:
        return HttpResponse(
            '<div> <h2>Sorry the image does not exist.</h2> <a href="/dashboard"> Go to Dashboard</a> </div>'
        )
    user = request.user
    try:
        annotator = Annotator.objects.get(user=user)
    except ObjectDoesNotExist:
        return HttpResponse(
            '<div> <h2>Sorry you are not an annotator.</h2> <a href="/dashboard"> Go to Dashboard</a> </div>'
        )
    try:
        annot_obj = Annotation.objects.get(annotator=annotator, image=img)
    except ObjectDoesNotExist:
        return HttpResponse(
            '<div> <h2>Sorry you are not assigned this image.</h2> <a href="/dashboard"> Go to Dashboard</a> </div>'
        )
    if annot_obj.label_file:
        annot_obj.label_file.delete()

    annot_obj.has_cyst = False
    annot_obj.annotated = True
    annot_obj.annotated_on = datetime.now()
    annot_obj.save()

    return JsonResponse(
        {"message": "Annotations Sync Successful. This image does not have a cyst."}
    )


@login_required
def change_image(request: HttpRequest) -> HttpResponse:
    user = request.user
    img, step = request.GET["img"], request.GET["step"]
    try:
        annotator = Annotator.objects.get(user=user)
    except Annotator.DoesNotExist:
        return HttpRequest(status=403, content="You are not an annotator.")

    try:
        image = SlideImage.objects.get(image_id=img)
    except SlideImage.DoesNotExist:
        return HttpResponse(status=404, content="Image not found.")
    try:
        annotation = Annotation.objects.get(image=image, annotator=annotator)
    except Annotation.DoesNotExist:
        return HttpResponse(
            status=404,
            content="Either the annotation does not exist or you are not assigned this annotation.",
        )

    if step == "next":
        kwargs = dict(id__gt=annotation.id)
    else:
        kwargs = dict(id__lt=annotation.id)
    order_by = "id"

    new_image = (
        Annotation.objects.filter(
            **kwargs,
            image__image_type=image.image_type,
            annotator=annotator,
            annotated=False,
        )
        .order_by(order_by)
        .first()
    )

    if new_image is None:
        return HttpResponse(status=404, content="No more images in this category.")

    return JsonResponse(
        {
            "img": new_image.image.image_id,
        }
    )
