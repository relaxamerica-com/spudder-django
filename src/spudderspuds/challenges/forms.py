import re
from django import forms
from django.contrib.auth.models import User
from settings import SPORTS
from spudderadmin.templatetags.featuretags import feature_is_enabled
from spudderdomain.controllers import SocialController, RoleController, EntityController
from spudderdomain.models import TeamPage
from spudmart.CERN.models import SORTED_STATES
from spudderspuds.forms import FanSigninForm

REQUIRED = "<span class=\"input-required\">*required</span>"
HELP_TEXT = '<i class="fa fa-question-circle text-primary" title="%s"></i>'
# HELP_TEXT = '<i class="fa fa-question-circle text-primary popover" data-content="%s" data-toggle="popover" ' \
#             'data-trigger="focus"></i>'


class CreateTempClubForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        label="Enter team's name: " + REQUIRED
              + HELP_TEXT % "This is a name used to recognize this team.",
        widget=forms.TextInput(attrs={
            'addon_before': '<i class="fa fa-fw fa-pencil"></i>',
            'placeholder': 'Team name'}))
    email = forms.EmailField(
        label="Enter an email to reach the team: "
              + HELP_TEXT % "We will use this email address to try to contact the team.",
        required=False,
        widget=forms.TextInput(attrs={
            'addon_before': '<i class="fa fa-fw fa-envelope"></i>',
            'placeholder': 'Contact email (optional)'}))
    website = forms.URLField(
        label="Enter a website for the team: "
              + HELP_TEXT % "This website will be used to help identify the team.",
        required=False,
        widget=forms.TextInput(attrs={
            'addon_before': '<i class="fa fa-fw fa-home"></i>',
            'placeholder': 'Teams website (optional)'}))
    contact_number = forms.CharField(
        label="Enter a contact number for the team: "
              + HELP_TEXT % "This phone number will be used to help identify the team.",
        required=False,
        widget=forms.TextInput(attrs={
            'addon_before': '<i class="fa fa-fw fa-phone"></i>',
            'placeholder': 'Contact number (optional)'}))
    other_information = forms.CharField(
        label='Any other information: '
              + HELP_TEXT % 'Do you have any other information that we can use to quickly find your club and ensure '
              'they get their money, their address for example?',
        max_length=1024,
        required=False,
        help_text="",
        widget=forms.Textarea(attrs={'rows': '3', 'placeholder': ''}))


class ChallengeConfigureForm(forms.Form):
    donation_with_challenge = forms.IntegerField(
        label="Suggested donation when accepting challenge",
        help_text="The suggested donation each person will be asked for when they accept this challenge.",
        widget=forms.TextInput(attrs={'addon_before': '$', 'addon_after': '.00'}))
    donation_without_challenge = forms.IntegerField(
        label="Suggested donation when declining challenge",
        help_text="The suggested donation each person will be asked for if they decline this challenge.",
        widget=forms.TextInput(attrs={'addon_before': '$', 'addon_after': '.00'}))
    file = forms.FileField(
        label="Upload an image",
        help_text="Here is your chance to upload an image associated with your team, something that your fans will "
                  "recognize. The best images are landscape!",
        required=False)


class ChallengesRegisterForm(forms.Form):
    ACCOUNT_TYPE_CHOICES = (
        (RoleController.ENTITY_FAN, 'I\'m a sports fan'),
        (EntityController.ENTITY_CLUB, 'I\'m a team administrator'),
    )

    account_type = forms.CharField(widget=forms.HiddenInput, initial=RoleController.ENTITY_FAN)
    username = forms.CharField(
        max_length=255,
        label="Choose a username",
        help_text="A username can only consist of letters and numbers. Letters are not case sensitive.",
        widget=forms.TextInput(attrs={'addon_before': '<i class="fa fa-fw fa-user"></i>'}))
    password = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(attrs={'addon_before': '<i class="fa fa-fw fa-lock"></i>'}),
        label="Please choose a password",
        help_text="Six or more characters please!")
    email_address = forms.EmailField(
        label="Your email address",
        widget=forms.TextInput(attrs={'addon_before': '<i class="fa fa-fw fa-envelope"></i>'}))
    state = forms.ChoiceField(
        choices=[('', 'Select a state...')] + sorted([(k, v) for k, v in SORTED_STATES.items()], key=lambda x: x[1]),
        label="Most important state for sports",
        help_text="Why are we asking this: So that we can localize experience to the sports that matter most to you.")
    next = forms.CharField(max_length=256, required=False, widget=forms.HiddenInput, initial='/')

    def __init__(self, *args, **kwargs):
        enable_register_club = kwargs.pop('enable_register_club', None)
        self.prevent_password_again = kwargs.pop('prevent_password_again', None)
        super(ChallengesRegisterForm, self).__init__(*args, **kwargs)
        if enable_register_club:
            self.fields['account_type'] = forms.ChoiceField(choices=self.ACCOUNT_TYPE_CHOICES,
                                                            initial=RoleController.ENTITY_FAN)

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
            raise forms.ValidationError()
        return username
        
    def clean_password(self):
        password = super(ChallengesRegisterForm, self).clean().get('password', '')
        if len(password) < 6:
            raise forms.ValidationError("Passwords must be at least 6 characters long.")
        return password


class ChallengesSigninForm(FanSigninForm):
    next = forms.CharField(max_length=255, required=False, widget=forms.HiddenInput)


class AcceptChallengeForm(forms.Form):
    donation = forms.IntegerField(
        label="How much do you pledge?",
        help_text="The amount shown here is the suggested pledge amount, you are free to pledge more or less.",
        widget=forms.TextInput(attrs={'addon_before': '$', 'addon_after': '.00'}))


class UploadImageForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput)
    file = forms.FileField(
        label="Upload photo",
        help_text="Here is your chance to upload a photo of you doing the challenge.",
        required=True)


class RegisterCreateClubForm(forms.Form):
    name = forms.CharField(max_length=255,
                           label="The name of your team" + REQUIRED)
    at_name = forms.CharField(
        max_length=255,
        label="Create a hashtag for your team",
        help_text="""
hashtags are used throughout Spudder so fans
can easily find, follow and interact with your team. letters and numbers
only please""")
    sport = forms.ChoiceField(
        choices=[('', 'Select a sport...')] + [('%s' % x, SPORTS[x]) for x in range(len(SPORTS))],
        label="Choose a sport",
        help_text="If your team plays more than one sport, just choose one")
    description = forms.CharField(
        max_length=2000, required=False,
        help_text="Say something about your team!",
        widget=forms.Textarea(attrs={'placeholder': 'Team description'})
    )
    state = forms.ChoiceField(
        choices=[('', 'Select a state...')] + sorted([(k, v) for k, v in SORTED_STATES.items()], key=lambda x: x[1]),
        label="Where is this team? " + REQUIRED)
    address = forms.CharField(
        max_length=255, required=True,
        label="Address " + REQUIRED,
        help_text="Team main location address",
        widget=forms.TextInput(attrs={'placeholder': 'Address'})
    )
    next = forms.CharField(max_length=256, required=False, widget=forms.HiddenInput)

    def clean_at_name(self):
        at_name = self.cleaned_data.get('at_name')
        if at_name:
            if not re.match("^[a-zA-Z0-9]*$", at_name):
                raise forms.ValidationError('Only letters and numbers are allowed.')

            try:
                TeamPage.objects.get(at_name=at_name)
            except TeamPage.DoesNotExist:
                pass
            else:
                raise forms.ValidationError("This at_name is already taken by other team.")

        return at_name


class ChallengeChallengeParticipationForm(forms.Form):
    youtube_video_id = forms.CharField(
        max_length=256,
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'youtube-video-id'}))
    challenge_name = forms.CharField(
        max_length=255,
        help_text="Give your challenge a name!",
        widget=forms.TextInput(attrs={'addon_before': '<i class="fa fa-pencil"></i>'}))
    challenge_description = forms.CharField(
        max_length=2056,
        widget=forms.Textarea)
    file = forms.FileField(
        label="Upload photo of your challenge <small>(optional)</small>",
        help_text="You will increase you chances of winning if you upload a photo!",
        required=False)


class ChallengeDonationEditForm(forms.Form):
    """
    A form to change just the donations on a challenge.
    """
    donation_with_challenge = forms.IntegerField(
        label="Suggested donation when accepting challenge",
        help_text="The suggested donation each person will be asked for when they accept this challenge.",
        widget=forms.TextInput(attrs={'addon_before': '$', 'addon_after': '.00'}))
    donation_without_challenge = forms.IntegerField(
        label="Suggested donation when declining challenge",
        help_text="The suggested donation each person will be asked for if they decline this challenge.",
        widget=forms.TextInput(attrs={'addon_before': '$', 'addon_after': '.00'}))


class ChallengeImageEditForm(forms.Form):
    """
    A form to change just the image on a challenge.
    """
    file = forms.FileField(
        label="Upload an image",
        help_text="Here is your chance to upload an image associated with your team, something that your fans will "
                  "recognize. The best images are landscape!",
        required=False)
