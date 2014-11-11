from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from spudderaccounts.wrappers import RoleStudent
from spudmart.CERN.models import Student


class StudentMigrateForm(forms.Form):
    email_address = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super(StudentMigrateForm, self).clean()
        email_address = (data.get('email_address') or "").strip().lower()
        password = data.get('password', "")
        raise_error = False
        if not email_address:
            self._errors['email_address'] = self.error_class(['You must supply an email address'])
            raise_error = True

        try:
            user = User.objects.get(username=email_address)
        except ObjectDoesNotExist:
            student = check_students_for_email(email_address)
            if student:
                self.student = student
            else:
                self._errors['email_address'] = self.error_class(["No student recognized with this email address."])
                raise_error = True

        if not password or len(password) < 6:
            self._errors['password'] = self.error_class(['You must supply a password longer than 6 characters'])
            raise_error = True
        if raise_error:
            raise forms.ValidationError('There was a problem migrating your account.')
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
            if User.objects.filter(email=email_address).count():
                for u in User.objects.filter(email=email_address):
                    u.username = email_address
                    u.save()
            else:
                student = check_students_for_email(email_address)
                if student:
                    raise forms.ValidationError('Your account has not been migrated. <br/>'
                                                'Click <a href="/cern/login/migrate">here</a> to migrate your account.')
                else:
                    raise forms.ValidationError("Your email address was not recognized. <br/>"
                                                "Were you trying to <a href='/cern/register'>register</a>?")

        password = cleaned_data.get('password')
        try:
            User.objects.get(username=email_address, password=password)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Email and password do not match.')
        cleaned_data['email_address'] = email_address
        return cleaned_data


class StudentRegistrationForm(forms.Form):
    email_address = forms.EmailField(
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Your email address'}))
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Your password'}))

    def clean(self):
        cleaned_data = super(StudentRegistrationForm, self).clean()
        email_address = cleaned_data.get('email_address', '').strip().lower()
        try:
            u = User.objects.get(username=email_address)
            Student.objects.get(user=u)
        except ObjectDoesNotExist:
            pass
        except MultipleObjectsReturned:
            raise forms.ValidationError("You already have an account. "
                                        "Were you trying to <a href='/cern/login'>login?</a>")
        else:
            raise forms.ValidationError("You already have an account. "
                                        "Were you trying to <a href='/cern/login'>login?</a>")

        cleaned_data['email_address'] = email_address
        return cleaned_data


def check_students_for_email(email):
    """
    Used to check the student objects for email addresses that are not the
     primary email address on the account, making search for user by email
     address not return any results
    :param email: a string of email address
    :return: the student with the corresponding email, or none
    """
    student_emails = {}
    for s in Student.objects.all():
        role = RoleStudent(s)
        student_emails[role.contact_emails[0]] = role.entity
    try:
        return student_emails[email]
    except KeyError:
        return None