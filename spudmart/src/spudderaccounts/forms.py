from django import forms


class ProfileDetailsForm(forms.Form):
    first_name = forms.CharField(max_length=256, required=False)
    last_name = forms.CharField(max_length=256, required=False)



