from django.contrib import admin

from .models import Annotation, Annotator

# Register your models here.


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ("image", "annotator", "annotated")


admin.site.register(Annotator)
admin.site.register(Annotation, AnnotationAdmin)
