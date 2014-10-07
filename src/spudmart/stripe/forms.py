from django import forms


class StripeRegisterRecipientForm(forms.Form):
    name = forms.CharField(
        max_length=255, required=True,
        label="Full legal name <span class='input-required'>*required<span>",
        help_text="Club full legal name in which it was registered",
        widget=forms.TextInput(attrs={'placeholder': ''}))
    ein = forms.CharField(
        max_length=255,
        required=True,
        label="Tax ID <span class='input-required'>*required<span>",
        help_text="Employer Identification Number",
        widget=forms.TextInput(attrs={'placeholder': ''}))

    def clean_name(self):
        data = super(StripeRegisterRecipientForm, self).clean()
        name = str(data.get('name'))
        if not name:
            raise forms.ValidationError('Your teams full legal name is required.')
        return name

    def clean_ein(self):
        data = super(StripeRegisterRecipientForm, self).clean()
        ein = str(data.get('ein'))
        if not ein:
            raise forms.ValidationError('A Tax ID is required.')
        ein = ein.strip()
        if len(ein) != 9 or not ein.isdigit():
            raise forms.ValidationError('A Tax ID should be 9 numbers only.')
        return ein

    def clean(self):
        name = request.POST.get('name')
        ein = request.POST.get('ein')
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        recipient_creation_result = stripe.Recipient.create(
            name=name,
            type="corporation",
            tax_id=ein
        )
        is_verified = recipient_creation_result['verified']
        if is_verified:
            StripeRecipient(
                registered_by=request.user,
                club=club,
                recipient_id=recipient_creation_result['id']
            ).save()

