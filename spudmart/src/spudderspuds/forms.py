from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class FanSigninForm(forms.Form):
    email_address = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

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

