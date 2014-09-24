from django import forms
from django.contrib.auth.models import User
from spudderdomain.controllers import SocialController
from spudmart.CERN.models import STATES
from spudderspuds.forms import FanSigninForm



class CreateTempClubForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        help_text="Please be a descriptive as possible, a good, accurate name will help us identify your club and "
                  "get them their money sooner!")
    email = forms.EmailField(
        help_text="If you know an email address of someone at the club, we'll contact them to ensure they get "
                  "their money",
        required=False)
    other_information = forms.CharField(
        max_length=1024,
        required=False,
        help_text="Do you have any other information that we can use to quickly find your club and ensure they "
                  "get their money, their address for example?",
        widget=forms.Textarea)


class ChallengeConfigureForm(forms.Form):
    donation_with_challenge = forms.IntegerField(
        label="Suggested donation when accepting challenge",
        help_text="The suggested donation each person will be asked for when they accept this challenge.",
        widget=forms.TextInput(attrs={'addon_before': '$', 'addon_after': '.00', 'placeholder': '$\'s'}))
    donation_without_challenge = forms.IntegerField(
        label="Suggested donation when declining challenge",
        help_text="The suggested donation each person will be asked for if they decline this challenge.",
        widget=forms.TextInput(attrs={'addon_before': '$', 'addon_after': '.00', 'placeholder': '$\'s'}))
    file = forms.FileField(
        label="Upload photo or video",
        help_text="Here is your chance to upload a photo or video for this challenge, it can be a video of you doing "
                  "the challenge or just an image that's associated with the club.",
        required=False)


class ChallengesRegisterForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255, widget=forms.PasswordInput)
    password_again = forms.CharField(max_length=255, widget=forms.PasswordInput)
    email_address = forms.EmailField()
    next = forms.CharField(max_length=256, required=False, widget=forms.HiddenInput)

    def clean_email_address(self):
        email_address = super(ChallengesRegisterForm, self).clean().get('email_address', '').lower()
        if User.objects.filter(email=email_address):
            raise forms.ValidationError(
                'There is a user already using this email address. Are you sure you don\'t want to sign in?')
        return email_address
        
    def clean_username(self):
        username = super(ChallengesRegisterForm, self).clean().get('username', '').lower()
        if not SocialController.AtNameIsUniqueAcrossThePlatform(username):
            raise forms.ValidationError('There is a user already using this username.')
        if not SocialController.AtNameIsValid(username):
            raise forms.ValidationError('Please use only letter and number in your username.')
        return username
        
    def clean(self):
        data = super(ChallengesRegisterForm, self).clean()
        password = data.get('password', '').strip()
        password_again = data.get('password_again', '').strip()
        if not password or password != password_again or len(password) < 6:
            self._errors['password'] = self.error_class([
                'You must enter two passwords that match and are longer than 6 characters.'])
            self._errors['password_again'] = self.error_class([
                'You must enter two passwords that match and are longer than 6 characters.'])
            del data['password']
            del data['password_again']
            raise forms.ValidationError('Something went wrong with your registration.')
        return data


class ChallengesSigninForm(FanSigninForm):
    next = forms.CharField(max_length=255, required=False, widget=forms.HiddenInput)


class AcceptChallengeForm(forms.Form):
    donation = forms.IntegerField(
        label="How much do you pledge?",
        help_text="The amount shown here is the suggested pledge amount, you are free to pledge more or less.",
        widget=forms.TextInput(attrs={'addon_before': '$', 'addon_after': '.00'}))
    file = forms.FileField(
        label="Upload photo or video",
        help_text="Here is your chance to upload a photo or video of you doing the challenge.",
        required=False)