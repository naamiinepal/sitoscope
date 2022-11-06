from django.db import models
from address.models import Site
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

# Create your models here.


class DiarrheaSymptom(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="submitted by",
    )

    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name = "Diarrhea Symptom"
        db_table="diarrhea_symptom"


    def __str__(self):
        return self.name

class Sample(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="submitted by",
    )
    date_of_collection = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date of collection", 
        help_text="Enter a date"
    )
    site = models.ForeignKey(
        Site, 
        on_delete=models.PROTECT, 
        verbose_name="Sample Collection Site"
    )

    class Meta:
        abstract = True


class Stool(Sample):
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(150)],
        verbose_name="Patient's Age"    
    )
    gender = models.CharField(
        max_length=1, 
        choices=(
            ('M', 'Male'),
            ('F', "Female"),
            ('O', "Others")
        ),
        verbose_name="Patient's Gender"
    )
    symptoms = models.ManyToManyField(DiarrheaSymptom)

    class Meta:
        verbose_name = "Stool Sample"
    
    def __str__(self):
        return f"Stool-{self.site}-{self.date_of_collection}"


class Vegetable(Sample):
    name = models.CharField(max_length=100, verbose_name="Vegetable Name")
    origin = models.CharField(max_length=200, verbose_name="Origin of the vegetable")

    class Meta:
        verbose_name = "Vegetable Sample"

    def __str__(self):
        return f"Vegetable-{self.name}-{self.site}-{self.date_of_collection}"


class Water(Sample):
    source = models.CharField(max_length=1, choices=(
        ("T", "Tap"),
        ("P", "Pond"),
        ("R", "River"),
    ))

    class Meta:
        verbose_name = "Water Sample"
        ordering = ['-date_of_collection']

    def __str__(self):
        return f"Water-{self.site}-{self.date_of_collection}"
