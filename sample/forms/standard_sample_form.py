from datetime import date, timedelta
from django import forms
from django.forms import Form, ModelForm
from django.forms.widgets import DateInput
from bootstrap_daterangepicker import widgets as datepicker_widgets
from bootstrap_daterangepicker import fields as datepicker_fields

from sample.models import Standard
from address.models import Province


class StandardForm(ModelForm):
    class Meta:
        model = Standard
        fields = [
            "date_of_collection",
            "sample_type",
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

    def clean_images(self):
        files = self.files.getlist("images")
        if len(files) != 15:
            raise forms.ValidationError("Please upload exactly 15 images.")
        return files


class FilterForm(Form):
    # Date Range Fields
    filter_date_range = datepicker_fields.DateRangeField(
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=datepicker_widgets.DateRangeWidget(
            format='%Y-%m-%d',
            picker_options={
                "ranges": {
                    "Yesterday": [(date.today() - timedelta(days=1)).strftime('%Y-%m-%d'), (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')],
                    "Last 7 days": [(date.today() - timedelta(days=7)).strftime('%Y-%m-%d'), date.today().strftime('%Y-%m-%d')],
                    "Last Month": [(date.today() - timedelta(days=30)).strftime('%Y-%m-%d'), date.today().strftime('%Y-%m-%d')]
                }
            },
        )
    )
    province = forms.ModelChoiceField(Province.objects.only("name", "code"), widget=forms.widgets.Select(attrs={'class': "form-select"}), required=False)

    def __init__(self, default_range: str, province: int, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.initial['filter_date_range'] = default_range
        self.initial['province'] = province
        