import stripe
from django import forms
from django.conf import settings
from spudderdomain.models import StripeRecipient
from spudmart.CERN.models import SORTED_STATES


class StripeRegisterRecipientForm(forms.Form):
    name = forms.CharField(
        max_length=255, required=True,
        label="Full legal name of your team <span class='input-required'>*required<span>",
        help_text="Please ensure you enter the full legal name of your team as used in any communications with the "
                  "IRS.",
        widget=forms.TextInput(attrs={'placeholder': ''}))
    ein = forms.CharField(
        max_length=255,
        required=True,
        label="Tax ID <span class='input-required'>*required<span>",
        help_text="Your Tax ID should be 9 numbers with no spaces. This is sometimes referred to as your Employer "
                  "Identification Number",
        widget=forms.TextInput(attrs={'placeholder': ''}))

    def clean_name(self):
        data = super(StripeRegisterRecipientForm, self).clean()
        name = str(data.get('name'))
        name = name.strip()
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
        data = super(StripeRegisterRecipientForm, self).clean()
        name = data.get('name')
        ein = data.get('ein')
        if name and ein:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            try:
                recipient_creation_result = stripe.Recipient.create(
                    name=name,
                    type="corporation",
                    tax_id=ein)
            except Exception as ex:
                raise forms.ValidationError('Something went wrong: %s' % ex)
            is_verified = recipient_creation_result['verified']
            if is_verified:
                try:
                    StripeRecipient(
                        registered_by=self.user,
                        club=self.club,
                        recipient_id=recipient_creation_result['id']
                    ).save()
                except Exception as ex:
                    raise forms.ValidationError('Something went wrong: %s' % ex)
            else:
                raise forms.ValidationError(
                    "There was an problem checking these details with the IRS. Please ensure that the Full Legal Name "
                    "and the EIN are accurate.<br/><br/>If you are unsure or are having problems completing this, "
                    "please contact us at support@spudder.com")
        return data


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