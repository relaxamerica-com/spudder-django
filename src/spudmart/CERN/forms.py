from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from spudmart.CERN.models import Student


class StudentMigrateForm(forms.Form):
    email_address = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super(StudentMigrateForm, self).clean()
        email_address = (data.get('email_address') or "").strip().lower()
        password = (data.get('password') or "").strip()
        raise_error = False
        if not email_address:
            self._errors['email_address'] = self.error_class(['You must supply an email address'])
            raise_error = True

        users = User.objects.filter(username__iexact=email_address)
        if users.count:
            for u in users:
                try:
                    Student.objects.get(user=u)
                except Student.DoesNotExist:
                    self._errors['email_address'] = self.error_class(['No student recognized with this email.'])
                    raise_error = True
                except Student.MultipleObjectsReturned:
                    pass
        else:
            self._errors['email_address'] = self.error_class(
                ['No account exists with this email address. Were you trying to <a href="/cern/register">register</a>?']
            )
            raise_error = True
        if not password or len(password) < 6:
            self._errors['password'] = self.error_class(['You must supply a password longer than 6 characters'])
            raise_error = True
        if raise_error:
            raise forms.ValidationError('There was a problem creating your account.')
        return data


class StudentLoginForm(forms.Form):
    email_address = forms.EmailField(
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Your email address'}))
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Your password'}))

    def clean(self):
        cleaned_data = super(StudentLoginForm, self).clean()
        email_address = cleaned_data.get('email_address', '').strip().lower()
        if not User.objects.filter(username=email_address).count():
            raise forms.ValidationError('Email address not recognized. Have you registered?')
        password = cleaned_data.get('password')
        user = authenticate(username=email_address, password=password)
        if not user or not user.is_active:
            del cleaned_data['password']
            raise forms.ValidationError('Email and password do not match.')
        cleaned_data['email_address'] = email_address
        return cleaned_data