from django.forms import ModelForm
from django.forms.widgets import DateInput

from sample.models import Stool


class StoolForm(ModelForm):
    class Meta:
        model = Stool
        fields = ["date_of_collection", "gender", "age", "symptoms", "stool_texture"]
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
        labels = {
            "gender": "Patient's Gender",
            "age": "Patient's age",
        }
