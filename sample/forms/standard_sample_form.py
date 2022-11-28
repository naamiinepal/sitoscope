from django.forms import ModelForm, Form
from sample.models import Standard
from django.forms.widgets import DateInput
from django import forms


class StandardForm(ModelForm):
    class Meta:
        model = Standard
        fields = [
            "date_of_collection",
            "matrix",
            "dilution_factor",
            "expected_concentration",
            "observed_concentration",
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


class SlideImagesForm(Form):
    images = forms.ImageField(
        widget=forms.FileInput(attrs={"multiple": True}),
        help_text="Select 15 slide images.",
    )
