from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.DiarrheaSymptom)
admin.site.register(models.Stool)
admin.site.register(models.Vegetable)
admin.site.register(models.Water)
