from django import forms
from django.forms import HiddenInput
from django.forms.models import ModelForm
from spudderdomain.models import TeamPage
from spudmart.venues.models import SPORTS
from spudmart.CERN.models import STATES


class BaseTeamForm(forms.Form):
    team_name = forms.CharField(max_length=255, help_text='The name of your team must be unique.')
    contact_details = forms.CharField(
        max_length=255,
        help_text='How should people contact you and your team? Leave instructions, number and emails '
                  'addresses here!',
        required=False)
    free_text = forms.CharField(
        max_length=255, help_text='Say something about your team!',
        required=False, label="About us")

    def clean_team_name(self):
        cleaned_data = super(BaseTeamForm, self).clean()
        name = cleaned_data.get('team_name').strip()
        if TeamPage.objects.filter(name=name).count():
            raise forms.ValidationError("The team name you are using is already taken, try adding the town or city?")
        return name


class CreateTeamForm(BaseTeamForm):
    next_url = forms.CharField(max_length=255, widget=HiddenInput)
    at_name = forms.CharField(
        max_length=255,
        label="Teams @name",
        help_text="Used to identify this team and link spuds to it! <b>lowercase letters and numbers only please</b>")
    sport = forms.ChoiceField(choices=[('%s' % x, SPORTS[x]) for x in range(len(SPORTS))])
    # file = forms.FileField(required=False, label="Image")
    state = forms.ChoiceField(choices=[(k, v) for k, v in STATES.items()])

    def clean_at_name(self):
        cleaned_data = super(CreateTeamForm, self).clean()
        at_name = cleaned_data.get('at_name', '').strip()
        if TeamPage.objects.filter(at_name=at_name).count():
            raise forms.ValidationError("The @name you are trying to use is already taken, please choose another.")
        for c in at_name:
            if c not in 'abcdefghijklmnopqrstuvwxyz0123456789':
                raise forms.ValidationError("At names can only contain lowercase letters and numbers!")
        return at_name


class EditTeamForm(BaseTeamForm):

    def __init__(self, *args, **kwargs):
        team_id = kwargs.pop('team_id', None)
        self.team_id = team_id
        super(EditTeamForm, self).__init__(*args, **kwargs)


    def clean_team_name(self):
        cleaned_data = super(EditTeamForm, self).clean()
        name = cleaned_data.get('team_name').strip()
        if TeamPage.objects.exclude(id=self.team_id).filter(name=name).count():
            raise forms.ValidationError("The team name you are using is already taken, try adding the town or city?")
        return name


class TeamPageForm(ModelForm):
    class Meta:
        model = TeamPage
        exclude = ('image', 'location')
