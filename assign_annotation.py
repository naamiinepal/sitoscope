import os

import django
from django.db.models import Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parasite.settings")
django.setup()


from annotation.models import Annotation, Annotator
from sample.const import COMMON_ANNOTATION_SAMPLES, IMAGE_TYPE_CHOICES
from sample.models import SlideImage


def assign_annotations():
    annotators = Annotator.objects.all()
    for image_type in IMAGE_TYPE_CHOICES:
        slide_images = SlideImage.objects.filter(
            ~Q(image=""), image_type=image_type[0], approved=True
        ).order_by("?")[:COMMON_ANNOTATION_SAMPLES]
        # print(slide_images)
        for i, annotator in enumerate(annotators):
            print(f"Assigning annotations for {annotator}")
            for slide_image in slide_images:
                annotation, created = Annotation.objects.update_or_create(
                    image=slide_image, annotator=annotator
                )
                if created:
                    print(
                        f"Created annotation for {annotator} on {annotation.image.image_id}"
                    )
                else:
                    print(
                        f"Annotation already exists for {annotator} on {annotation.image.image_id}"
                    )


if __name__ == "__main__":

    assign_annotations()
