from datetime import datetime
from json import dumps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from annotation.models import Annotation, Annotator
from sample.models import SlideImage

from .const import LABELS


# only show the annotation home page if the user is an annotator
@login_required
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

    annotated_images_count = annotations.count()
    not_annotated_images_count = not_annotated_images.count()

    context = {
        "images": {
            "annotations": annotations,
            "not_annotated": not_annotated_images,
            "annotated_count": annotated_images_count,
            "not_annotated_count": not_annotated_images_count,
            "total_count": annotated_images_count + not_annotated_images_count,
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
    except SlideImage.ObjectDoesNotExist:
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
    }
    print(dumps(LABELS))

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
            annot_obj.annotated = True
            annot_obj.annotated_on = datetime.now()
            # annot_obj.labels.set(used_labels)
            annot_obj.save()

        except ObjectDoesNotExist:
            annot_obj = Annotation.objects.create(annotator=annotator, image=img)
            annot_obj.label_file = File(json_file, f"{image_id}_{username}.json")
            annot_obj.annotated = True
            annot_obj.annotated_on = datetime.now()
            # annot_obj.labels.set(used_labels)
            annot_obj.save()

        return JsonResponse({"message": "Annotations Sync Successful"})

    except ObjectDoesNotExist:
        return HttpResponse(
            '<div> <h2>Sorry the image does not exist.</h2> <a href="/dashboard"> Go to Dashboard</a> </div>'
        )
