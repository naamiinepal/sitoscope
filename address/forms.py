from django import forms

from . import models


class AddressForm(forms.Form):
    province = forms.ModelChoiceField(models.Province.objects.only("name"))
    district = forms.ModelChoiceField(models.District.objects.only("name"))
    municipality = forms.ModelChoiceField(
        models.Municipality.objects.only("name"), label="Municipality/Gaunpalika"
    )
    ward = forms.IntegerField(initial=1, min_value=1, max_value=32, required=False)
    locality = forms.CharField(max_length=500, required=False)
