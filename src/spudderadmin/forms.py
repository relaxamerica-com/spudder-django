from django import forms
import tweepy


class AtPostSpudTwitterAPIForm(forms.Form):
    api_key = forms.CharField(max_length=256)
    api_secret = forms.CharField(max_length=256)

    def clean(self):
        data = super(AtPostSpudTwitterAPIForm, self).clean()
        auth = tweepy.OAuthHandler(data['api_key'], data['api_secret'])
        auth.secure = True
        try:
            auth.get_authorization_url()
        except:
            raise forms.ValidationError("The api key and api secret you entered do not match a Twitter app.")
        return data


class PasswordAndActionForm(forms.Form):
    password = forms.CharField(max_length=256, widget=forms.PasswordInput)
    action = forms.CharField(max_length=256, widget=forms.HiddenInput)

    def clean_password(self):
        data = super(PasswordAndActionForm, self).clean()
        password = data.get('password', None)
        if password != "spudmart2":
            raise forms.ValidationError("You don't know the password, should you be doing this?")
        return password


class SystemDeleteVenuesForm(PasswordAndActionForm):
    pass


class ChallengesResetSystemForm(PasswordAndActionForm):
    pass