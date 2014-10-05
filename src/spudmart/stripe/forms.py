from django import forms


class StripeRegisterRecipientForm(forms.Form):
    name = forms.CharField(
        max_length=255, required=True,
        label="Full legal name <span class='input-required'>*required<span>",
        help_text="Club full legal name in which it was registered",
        widget=forms.TextInput(attrs={'placeholder': ''})
    )

    ein = forms.IntegerField(
        required=True,
        label="Tax ID <span class='input-required'>*required<span>",
        help_text="Employer Identification Number",
        widget=forms.TextInput(attrs={'placeholder': ''})
    )