from django.forms import ModelForm
from django.forms.widgets import DateInput

from sample.models import Vegetable


class VegetableForm(ModelForm):
    class Meta:
        model = Vegetable
        fields = [
            "date_of_collection",
            "site_image",
            "name",
            "origin",
        ]
        widgets = {
            "date_of_collection": DateInput(
                format=(r"%Y-%m-%d"),
                attrs={
                    "class": "form-control",
                    "placeholder": "Select a date",
                    "type": "date",
                },
            ),
        }
