from django.forms import ModelForm
from . import models


# Create your forms here
class DiarrheaSymptomsForm(ModelForm):
    class Meta:
        model = models.DiarrheaSymptom
        fields = ['name']