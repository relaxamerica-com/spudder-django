from django.forms.models import ModelForm
from django import forms
from spudderaccounts.controllers import InvitationController
from spudderaccounts.models import Invitation
from spudderaffiliates.models import Affiliate
from django.core.exceptions import ValidationError
from spudderdomain.controllers import EntityController
from spudmart.CERN.models import SORTED_STATES


class AffiliateForm(ModelForm):
    """
    A simple Form for creating new affiliates.
    """
    url_name = forms.CharField(max_length=255, label="URL name",
                               help_text="This is what comes after www.spudder.com in the url for the affiliate.")
    description = forms.CharField(widget=forms.Textarea, help_text="Tip: You can put HTML tags in this description.")
    path_to_icon = forms.CharField(max_length=255, label="Link to Icon")
    path_to_cover_image = forms.CharField(max_length=255, label="Link to Jumbotron Image")
    username = forms.CharField(max_length=255, help_text="Username for the affiliate to log into their dashboard.")
    password = forms.CharField(max_length=255, help_text="Password for the affiliate to log into their dashboard.")

    class Meta:
        model = Affiliate

    def clean_username(self):
        cleaned_data = super(AffiliateForm, self).clean()
        username = cleaned_data.get('username').strip()
        if self.instance.id:
            objects = Affiliate.objects.exclude(id=self.instance.id)
        else:
            objects = Affiliate.objects.all()
        if objects.filter(username=username).count():
            raise ValidationError("That username is already being used by an affiliate.")
        return username

    def clean_name(self):
        cleaned_data = super(AffiliateForm, self).clean()
        name = cleaned_data.get('name').strip()
        if self.instance.id:
            objects = Affiliate.objects.exclude(id=self.instance.id)
        else:
            objects = Affiliate.objects.all()
        if objects.filter(name=name).count():
            raise ValidationError("There is already an affiliate with that name.")
        return name

    def clean_url_name(self):
        cleaned_data = super(AffiliateForm, self).clean()
        url_name = cleaned_data.get('url_name').strip()
        if self.instance.id:
            objects = Affiliate.objects.exclude(id=self.instance.id)
        else:
            objects = Affiliate.objects.all()
        if objects.filter(url_name=url_name).count():
            raise ValidationError("That URL is already being used by another affiliate.")

        if "/" in url_name:
            raise ValidationError("No slashes (/) are allowed in Affiliate urls.")
        return url_name


class ClubAdministratorForm(forms.Form):
    """
    A simple form for inviting someone to create a club in Spudder
    """
    email = forms.EmailField(max_length=255, help_text="Email address for the person managing this club/team<br>")
    club_name = forms.CharField(max_length=255, help_text="The name of the club/team<br>")
    state = forms.ChoiceField(
        choices=[('', 'Select a state...')] + sorted([(k, v) for k, v in SORTED_STATES.items()], key=lambda x: x[1]),
        help_text="The state where the club/team plays<br>")


class NaysSurveyEmailForm(forms.Form):
    # Name field is used to fool bots. its hidden and if text is entered then the form submission fails
    name = forms.CharField(
        label='',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'style': 'display:none;'}))
    email = forms.EmailField(
        max_length=255,
        label='Your email address',
        help_text='Submit your email address to enter the free prize draw.',
        widget=forms.TextInput(attrs={
            'addon_before': '<i class="fa fa-envelope"></i>',
            'placeholder': 'Email'}))

    def clean_name(self):
        data = super(NaysSurveyEmailForm, self).clean()
        name = data.get('name')
        if name:
            raise forms.ValidationError('You are a bot')
        return name