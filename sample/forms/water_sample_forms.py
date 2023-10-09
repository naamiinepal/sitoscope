from django.forms import ModelForm
from django.forms.widgets import DateInput

from sample.models import Water


class WaterForm(ModelForm):
    class Meta:
        model = Water
        fields = ["date_of_collection", "site_image", "type", "use", "lat", "long"]
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
        help_texts = {
            'lat': 'Format: 27.684865',
            'long': 'Format: 85.319869'
        }
