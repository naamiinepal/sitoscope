from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Layout
from django import forms

from . import models


class AddressForm(forms.Form):
    province = forms.ModelChoiceField(models.Province.objects.only("name"))
    district = forms.ModelChoiceField(models.District.objects.only("name"))
    site = forms.ModelChoiceField(models.Site.objects.only("number"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Column("province", css_class="form-group col-md-6 mb-1"),
                css_class="row",
            ),
            Div(
                Column("district", css_class="form-group col-md-6 mb-1"),
                css_class="row",
            ),
            Div(Column("site", css_class="form-group col-md-4 mb-1"), css_class="row"),
        )
