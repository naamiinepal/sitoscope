from datetime import date

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from address.models import Municipality
from sample.const import (
    GENDER_CHOICES,
    IMAGE_TYPE_CHOICES,
    STANDARD_SAMPLE_TYPES,
    VEGETABLE_CHOICES,
    WATER_TYPE_CHOICES,
)
from sample.utils import upload_samples


# Create your models here.
class Sample(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name="Created By",
    )
    date_of_collection = models.DateField(default=date.today)
    sample_id = models.CharField(max_length=500, unique=True)
    site_image = models.ImageField(upload_to="site_images")  # TODO: Change this
    site = models.ForeignKey(Municipality, on_delete=models.PROTECT, null=True)
    locality = models.CharField(max_length=500, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.sample_id


class Standard(models.Model):
    """
    Model to describe standard samples.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name="Created By",
    )
    date_of_collection = models.DateField(default=date.today)
    sample_type = models.CharField(max_length=1, choices=STANDARD_SAMPLE_TYPES)
    sample_id = models.CharField(max_length=500, unique=True)
    matrix = models.CharField(max_length=200)
    dilution_factor = models.DecimalField(max_digits=6, decimal_places=4)
    expected_concentration = models.DecimalField(max_digits=10, decimal_places=4)
    observed_concentration = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        verbose_name = "standard"
        ordering = ["-date_of_collection"]

    def __str__(self):
        return self.sample_id


class Water(Sample):
    """
    Model to describe water sample.
    """

    type = models.CharField(max_length=2, choices=WATER_TYPE_CHOICES)
    use = models.CharField(max_length=200, null=True, blank=True)
    ward = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(32)]
    )
    lat = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Latitude")
    long = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Longitude")

    class Meta:
        verbose_name = "water"
        ordering = ["-date_of_collection"]


class Stool(Sample):
    """
    Model to describe stool sample.
    """

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(200)]
    )
    symptoms = models.CharField(max_length=1000, null=True)
    stool_texture = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name = "stool"
        ordering = ["-date_of_collection"]


class Vegetable(Sample):
    """
    Model to describe vegetable sample.
    """

    ward = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(32)]
    )
    name = models.CharField(max_length=2, choices=VEGETABLE_CHOICES)
    origin = models.CharField(max_length=200, null=True, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Latitude")
    long = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Longitude")

    class Meta:
        verbose_name = "vegetable"
        ordering = ["-date_of_collection"]


class Slide(models.Model):
    """
    Model to describe sample slides.
    """

    standard_sample = models.ForeignKey(
        Standard, related_name="standard_slides", on_delete=models.PROTECT, null=True
    )

    stool_sample = models.ForeignKey(
        Stool, related_name="stool_slides", on_delete=models.PROTECT, null=True
    )

    vegetable_sample = models.ForeignKey(
        Vegetable, related_name="vegetable_slides", on_delete=models.PROTECT, null=True
    )

    water_sample = models.ForeignKey(
        Water, related_name="water_slides", on_delete=models.PROTECT, null=True
    )

    slide_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(water_sample__isnull=False)
                    & models.Q(stool_sample__isnull=True)
                    & models.Q(vegetable_sample__isnull=True)
                    & models.Q(standard_sample__isnull=True)
                )
                | (
                    models.Q(water_sample__isnull=True)
                    & models.Q(stool_sample__isnull=False)
                    & models.Q(vegetable_sample__isnull=True)
                    & models.Q(standard_sample__isnull=True)
                )
                | (
                    models.Q(water_sample__isnull=True)
                    & models.Q(stool_sample__isnull=True)
                    & models.Q(vegetable_sample__isnull=False)
                    & models.Q(standard_sample__isnull=True)
                )
                | (
                    models.Q(water_sample__isnull=True)
                    & models.Q(stool_sample__isnull=True)
                    & models.Q(vegetable_sample__isnull=True)
                    & models.Q(standard_sample__isnull=False)
                ),
                name="only_one_sample",
            )
        ]
        verbose_name = "slide"

    def __str__(self):
        if self.water_sample:
            return f"Slide {self.slide_number} for {self.water_sample}"
        if self.stool_sample:
            return f"Slide {self.slide_number} for {self.stool_sample}"
        if self.vegetable_sample:
            return f"Slide {self.slide_number} for {self.vegetable_sample}"
        if self.standard_sample:
            return f"Slide {self.slide_number} for {self.standard_sample}"


class SlideImage(models.Model):
    """
    Model to describe slide images.
    """

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="uploaded by",
        related_name="uploaded_by",
    )

    slide = models.ForeignKey(
        Slide, related_name="slide_image", on_delete=models.PROTECT, default=None
    )
    image = models.ImageField(
        upload_to=upload_samples,
        verbose_name="Slide Image",
    )
    image_id = models.CharField(max_length=100, unique=True)
    image_number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(15)]
    )
    image_type = models.CharField(max_length=1, choices=IMAGE_TYPE_CHOICES, default="S")

    created_at = models.DateTimeField(auto_now=True)

    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_by",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(image_type__exact="S") | models.Q(image_type__exact="B")
                ),
                name="image_type_S_or_B",
            )
        ]

    def __str__(self):
        return self.image_id
