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
