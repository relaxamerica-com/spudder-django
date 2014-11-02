import logging
import stripe
import settings
from django import forms
from spudderdomain.models import StripeRecipient, Club
from spudmart.CERN.models import SORTED_STATES
from spudderadmin.templatetags.featuretags import feature_is_enabled


class ClubProfileCreateForm(forms.Form):
    address = forms.CharField(
        max_length=255, required=True,
        label="Address <span class='input-required'>*required<span>",
        help_text="Club main location address",
        widget=forms.TextInput(attrs={'placeholder': 'Address'})
    )
    state = forms.ChoiceField(
        choices=[('', 'Select a state...')] + sorted([(k, v) for k, v in SORTED_STATES.items()], key=lambda x: x[1]),
        label="State <span class=\"input-required\">*required</span>")


class ClubProfileEditForm(ClubProfileCreateForm):
    description = forms.CharField(
        max_length=2000, required=False,
        help_text="Say something about your club!",
        widget=forms.Textarea(attrs={'placeholder': 'Club description'})
    )


class ClubProfileBasicDetailsForm(forms.Form):
    id = forms.CharField(max_length=255, widget=forms.HiddenInput)
    name = forms.CharField(max_length=255, label='Organization Name')

    def __init__(self, club, *args, **kwargs):
        super(ClubProfileBasicDetailsForm, self).__init__(*args, **kwargs)
        if club.name_is_fixed:
            self.fields['name'].widget = forms.TextInput(attrs={'readonly': 'true'})
            self.fields['name'].help_text = "Once your organization name has been verified by Stripe, it can no " \
                                            "longer be changed."

    def clean_name(self):
        data = super(ClubProfileBasicDetailsForm, self).clean()
        name = data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('Organization name is required.')
        if len(name) < 3:
            raise forms.ValidationError('Organization name should be longer than 3 characters.')
        if Club.objects.filter(name=name).exclude(id=data.get('id')).count():
            raise forms.ValidationError('An organization with that name already exists.')
        return name


class RegisterClubWithFanForm(forms.Form):
    name = forms.CharField(
        label='',
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Organization name (required)'}),
        help_text="This should be your organization full legal name")

    def clean_name(self):
        data = super(RegisterClubWithFanForm, self).clean()
        name = data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('An organization name is required.')
        if Club.objects.filter(name=name).count():
            raise forms.ValidationError('An organization with that name already exists.')
        return name