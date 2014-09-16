from django import forms


class QASigninForm(forms.Form):
    email_address = forms.EmailField()
    password = forms.CharField(max_length=255, widget=forms.PasswordInput)
    
    def clean_email_address(self):
        data = super(QASigninForm, self).clean()
        email_address = data.get('email_address', None)
        if email_address != "qa@spudder.com":
            raise forms.ValidationError("This email address is not valid")
        return email_address

    def clean_password(self):
        data = super(QASigninForm, self).clean()
        password = data.get('password', None)
        if password != "spudmart1":
            raise forms.ValidationError("This password is not valid")
        return password
