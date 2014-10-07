from django import forms
from spudmart.CERN.models import SORTED_STATES


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