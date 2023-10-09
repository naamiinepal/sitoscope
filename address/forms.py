from django import forms

from address import models


class AddressForm(forms.Form):
    province = forms.ModelChoiceField(models.Province.objects.only("name"))
    district = forms.ModelChoiceField(models.District.objects.only("name"))
    municipality = forms.ModelChoiceField(
        models.Municipality.objects.only("name"), label="Municipality/Gaunpalika"
    )
    ward = forms.IntegerField(initial=1, min_value=1, max_value=32, required=False)
    locality = forms.CharField(max_length=500, required=False)

    def __init__(self, *args, **kwargs):
        hide_condition = kwargs.pop("anonymous", None)
        super(AddressForm, self).__init__(*args, **kwargs)
        if hide_condition:
            del self.fields["ward"]
            del self.fields["locality"]
