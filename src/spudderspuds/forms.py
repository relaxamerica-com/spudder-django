import datetime
from django import forms
from django.forms.extras import SelectDateWidget
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from spudmart.CERN.models import SORTED_STATES


class FanSigninForm(forms.Form):
    email_address = forms.EmailField(
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Your email address'}))
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Your password'}))
    spud_id = forms.CharField(max_length=256, required=False, widget=forms.HiddenInput)
    twitter = forms.CharField(max_length=256, required=False, widget=forms.HiddenInput)

    def clean(self):
        cleaned_data = super(FanSigninForm, self).clean()
        email_address = cleaned_data.get('email_address', '').strip().lower()
        if not User.objects.filter(username=email_address).count():
            raise forms.ValidationError('Email address not recognized. Have you registered?')
        password = cleaned_data.get('password')
        user = authenticate(username=email_address, password=password)
        if not user or not user.is_active:
            del cleaned_data['email_address']
            del cleaned_data['password']
            raise forms.ValidationError('Email and password do not match.')
        cleaned_data['email_address'] = email_address
        return cleaned_data


class FanRegisterForm(forms.Form):
    email_address = forms.EmailField(
        required=True,
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Your email address (required)'}))
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Choose a password (required)'}),
        help_text='Passwords should be at least 6 characters long.')
    state = forms.ChoiceField(
        choices=[('', 'Most important state for sports (required)')] + sorted(
            [(k, v) for k, v in SORTED_STATES.items()], key=lambda x: x[1]),
        label="",
        help_text="Why are we asking this: So that we can localize experience to the sports that matter most to you.")
    over_13 = forms.BooleanField(
        label="I am over <span class='age' style='display:inline; position: relative;'>13</span> years of age",
        help_text="You must confirm that you are old enough to open this type of account on Spudder.")

    next = forms.CharField(max_length=256, required=False, widget=forms.HiddenInput, initial='/')
    spud_id = forms.CharField(max_length=256, required=False, widget=forms.HiddenInput)
    twitter = forms.CharField(max_length=256, required=False, widget=forms.HiddenInput)

    def clean_email(self):
        data = super(FanRegisterForm, self).clean()
        email = data.get('email', '').strip()
        if not email:
            raise forms.ValidationError('Email is required.')
        if User.objects.filter(email=email).count():
            raise forms.ValidationError('This email address is already associated with an account.')
        return email

    def clean_password(self):
        data = super(FanRegisterForm, self).clean()
        password = data.get('password', '').strip()
        if len(password) < 6:
            raise forms.ValidationError("Passwords must be at least 6 characters long.")
        return password


class FanPageForm(forms.Form):
    YEARS = range(datetime.datetime.now().date().year, datetime.datetime.now().date().year - 100, -1)

    name = forms.CharField(label='User Name', help_text='This can be your real name or something made up!')
    date_of_birth = forms.DateField(widget=SelectDateWidget(years=YEARS))
    state = forms.ChoiceField(choices=[(k, v) for k, v in SORTED_STATES.items()],
                              label="Where is your favorite team located?")
    file = forms.FileField(
        required=False, label="Add logo to your profile",
        help_text="Great logos are square and about 200px x 200px")

    def __init__(self, *args, **kwargs):
        fan_id = kwargs.pop('fan_id', None)
        self.fan_id = fan_id
        self.image = kwargs.pop('image', None)

        super(FanPageForm, self).__init__(*args, **kwargs)

        if self.image:
            self.update_file_field_label_and_help_text()

    def update_file_field_label_and_help_text(self):
        self.fields['file'].label = "Replace your current logo"
        self.fields['file'].help_text = """
<span class=\"help-text-content\">Great logos are square and about 200px x 200px</span>
<img class=\"edit-team-logo-img pull-left\" src=\"/file/serve/%s\"/>
""" % self.image.id


class BasicSocialMediaForm(forms.Form):
    twitter = forms.CharField(max_length=256, required=False, label="Twitter Username")
    facebook = forms.CharField(max_length=256, required=False, label="Facebook Profile Url")
    google_plus = forms.CharField(max_length=256, required=False, label="Google+ Profile Url")
    instagram = forms.CharField(max_length=256, required=False, label="Instagram Username")

    @staticmethod
    def get_social_media():
        return 'twitter', 'facebook', 'google_plus', 'instagram',


class LinkedInSocialMediaForm(BasicSocialMediaForm):
    linkedin = forms.CharField(max_length=256, required=False, label="LinkedIn Username")

    @staticmethod
    def get_social_media():
        return 'twitter', 'facebook', 'google_plus', 'instagram', 'linkedin',