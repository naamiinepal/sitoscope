from django.contrib.auth.models import User
from django.db import models

from sample.models import SlideImage

# Create your models here.


# Annotator is a user who can annotate samples
class Annotator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Annotation(models.Model):
    image = models.ForeignKey(
        SlideImage, on_delete=models.CASCADE, related_name="annotation_image"
    )
    annotator = models.ForeignKey(Annotator, on_delete=models.PROTECT)
    label_file = models.FileField(upload_to="annotation/labels")
    has_cyst = models.BooleanField(default=False)
    annotated = models.BooleanField(default=False)
    annotated_on = models.DateTimeField(null=True, blank=True)
    annotation_phase = models.CharField(null=True, max_length=200)

    # constraint for unique (image, annotator) pair
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["image", "annotator"], name="unique_image_annotator_pair"
            )
        ]
