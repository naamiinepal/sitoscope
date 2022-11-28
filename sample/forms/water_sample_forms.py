from django.forms import ModelForm
from sample.models import Water
from django.forms.widgets import DateInput


class WaterForm(ModelForm):
    class Meta:
        model = Water
        fields = [
            "date_of_collection",
            "site",
            "ward",
            "locality",
            "site_image",
            "type",
            "use",
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
