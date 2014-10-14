from django import forms
from django.contrib.auth.models import User
from django.forms import HiddenInput
from django.forms.models import ModelForm
from spudderaccounts.models import Invitation
from spudderdomain.controllers import SocialController, EntityController
from spudderdomain.models import TeamPage, FanPage
from spudmart.venues.models import SPORTS
from spudmart.CERN.models import SORTED_STATES


class BaseTeamForm(forms.Form):
    name = forms.CharField(max_length=255, help_text='The name of your team must be unique.',
                           label="Team name <span class=\"input-required\">*required</span>",
                           widget=forms.TextInput(attrs={'placeholder': 'Team name'}))
    contact_details = forms.EmailField(
        max_length=255,
        label="Email Address",
        help_text="This is where you will receive messages from Spudder users about your Team",
        required=False)
    free_text = forms.CharField(
        max_length=255, help_text='Say something about your team!',
        required=False, label="About us")

    def clean_name(self):
        cleaned_data = super(BaseTeamForm, self).clean()
        name = cleaned_data.get('name').strip()
        if TeamPage.objects.filter(name=name).count():
            raise forms.ValidationError("The team name you are using is already taken, try adding the town or city?")
        return name


class CreateTeamForm(BaseTeamForm):
    next_url = forms.CharField(max_length=255, widget=HiddenInput)
    at_name = forms.CharField(
        max_length=255,
        label="Teams @name <span class=\"input-required\">*required</span>",
        help_text="Used to identify this team and link spuds to it! <b>lowercase letters and numbers only please</b><div class='alert alert-danger' style='display:none;' id='at_name_alert'></div>",
        widget=forms.TextInput(attrs={'placeholder': 'Team @name'}))
    sport = forms.ChoiceField(
        choices=[('', 'Select a sport...')] + [('%s' % x, SPORTS[x]) for x in range(len(SPORTS))],
        label="Sport <span class=\"input-required\">*required</span>")
    state = forms.ChoiceField(
        choices=[('', 'Select a state...')] + sorted([(k, v) for k, v in SORTED_STATES.items()], key=lambda x: x[1]),
        label="Where is this team? <span class=\"input-required\">*required</span>")

    def clean_at_name(self):
        cleaned_data = super(CreateTeamForm, self).clean()
        at_name = cleaned_data.get('at_name', '').strip()
        if not SocialController.AtNameIsUniqueAcrossThePlatform(at_name):
            raise forms.ValidationError("The @name you are trying to use is already taken, please choose another.")
        for c in at_name:
            if c not in 'abcdefghijklmnopqrstuvwxyz0123456789':
                raise forms.ValidationError("At names can only contain lowercase letters and numbers!")
        return at_name

    # def is_valid(self):
    #     names = simplejson.loads(get_at_names(None))
    #     if self.


class EditTeamForm(BaseTeamForm):
    file = forms.FileField(
        required=False, label="Add logo to this team",
        help_text="Great logos are square and at least 200px x 200px")

    def __init__(self, *args, **kwargs):
        team_id = kwargs.pop('team_id', None)
        self.team_id = team_id
        self.image = kwargs.pop('image', None)

        super(EditTeamForm, self).__init__(*args, **kwargs)

        if self.image:
            self.update_file_field_label_and_help_text()

    def clean_name(self):
        cleaned_data = super(EditTeamForm, self).clean()
        name = cleaned_data.get('name').strip()
        if TeamPage.objects.exclude(id=self.team_id).filter(name=name).count():
            raise forms.ValidationError("The team name you are using is already taken, try adding the town or city?")
        return name

    def update_file_field_label_and_help_text(self):
        self.fields['file'].label = "Replace this team logo"
        self.fields['file'].help_text = """
<span class=\"help-text-content\">Great logos are square and at least 200px x 200px</span>
<img class=\"edit-team-logo-img pull-left\" src=\"/file/serve/%s\"/>
""" % self.image.id


class TeamPageForm(ModelForm):
    class Meta:
        model = TeamPage
        exclude = ('image', 'location')


class InviteNewFanByEmailForm(forms.Form):
    email = forms.EmailField()
    team_id = forms.CharField(max_length=255, widget=HiddenInput)