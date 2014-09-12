from django.forms.models import ModelForm
from django import forms
from spudderaffiliates.models import Affiliate
from django.core.exceptions import ValidationError


class AffiliateForm(ModelForm):
    """
    A simple Form for creating new affiliates.
    """
    url_name = forms.CharField(max_length=256, label="URL name",
                               help_text="This is what comes after www.spudder.com in the url for the affiliate.")
    description = forms.CharField(widget=forms.Textarea, help_text="Tip: You can put HTML tags in this description.")
    path_to_icon = forms.CharField(max_length=256, label="Link to Icon")
    path_to_cover_image = forms.CharField(max_length=256, label="Link to Jumbotron Image")
    username = forms.CharField(max_length=256, help_text="Username for the affiliate to log into their dashboard.")
    password = forms.CharField(max_length=256, help_text="Password for the affiliate to log into their dashbaord.")

    class Meta:
        model = Affiliate

    def clean_username(self):
        cleaned_data = super(AffiliateForm, self).clean()
        username = cleaned_data.get('username').strip()
        if Affiliate.objects.filter(username=username).count():
            raise ValidationError("That username is already being used by an affiliate.")
        return username

    def clean_name(self):
        cleaned_data = super(AffiliateForm, self).clean()
        name = cleaned_data.get('name').strip()
        if Affiliate.objects.filter(name=name).count():
            raise ValidationError("There is already an affiliate with that name.")
        return name

    def clean_url_name(self):
        cleaned_data = super(AffiliateForm, self).clean()
        url_name = cleaned_data.get('url_name').strip()
        if Affiliate.objects.filter(url_name=url_name).count():
            raise ValidationError("That URL is already being used by another affiliate.")
        return url_name

