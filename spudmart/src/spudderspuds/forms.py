import datetime
from django import forms
from django.core.validators import validate_ipv4_address
from django.forms.extras import SelectDateWidget
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from spudmart.CERN.models import STATES


class FanSigninForm(forms.Form):
    email_address = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    spud_id = forms.CharField(max_length=256, required=False, widget=forms.HiddenInput)
    twitter = forms.CharField(max_length=256, required=False, widget=forms.HiddenInput)

    def clean(self):
        cleaned_data = super(FanSigninForm, self).clean()
        email_address = cleaned_data.get('email_address', '')
        if not User.objects.filter(username=email_address).count():
            raise forms.ValidationError('Email address not recognized. Have you registered?')
        password = cleaned_data.get('password')
        user = authenticate(username=email_address, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError('Email and password do not match.')
        return cleaned_data


class FanRegisterForm(forms.Form):
    email_address = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    password_again = forms.CharField(widget=forms.PasswordInput)
    spud_id = forms.CharField(max_length=256, required=False, widget=forms.HiddenInput)
    twitter = forms.CharField(max_length=256, required=False, widget=forms.HiddenInput)

    def clean(self):
        data = super(FanRegisterForm, self).clean()
        email_address = data.get('email_address')
        password = data.get('password')
        password_again = data.get('password_again')
        raise_error = False
        if User.objects.filter(username__iexact=email_address).count():
            self._errors['email_address'] = self.error_class(['An account already exists for this email address.'])
            raise_error = True
        if password != password_again:
            message = 'Passwords must match.'
            self._errors['password'] = self.error_class([message])
            self._errors['password_again'] = self.error_class([message])
            raise_error = True
        if raise_error:
            raise forms.ValidationError('There was a problem creating your account.')
        return data


class FanPageForm(forms.Form):
    YEARS = range(datetime.datetime.now().date().year, datetime.datetime.now().date().year - 40, -1)

    name = forms.CharField(label='User Name', help_text='This can be your real name or something made up!')
    date_of_birth = forms.DateField(widget=SelectDateWidget(years=YEARS))
    state = forms.ChoiceField(choices=[(k, v) for k, v in STATES.items()], label="Where do you live?")


class FanPageSocialMediaForm(forms.Form):
    twitter = forms.CharField(max_length=256, required=False, label="Twitter Username")
    facebook = forms.CharField(max_length=256, required=False, label="Facebook Profile Url")
    google_plus = forms.CharField(max_length=256, required=False, label="Google+ Profile Url")
    instagram = forms.CharField(max_length=256, required=False, label="Instagram Username")