from django import forms


class ClubProfileForm(forms.Form):
    address = forms.CharField(max_length=255, required=True,
                              label="Address <span class='input-required'>*required<span>",
                              help_text="Club main location address",
                              widget=forms.TextInput(attrs={'placeholder': 'Address'}))