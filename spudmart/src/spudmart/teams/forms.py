from django import forms
from django.forms.models import ModelForm
from spudderdomain.models import TeamPage
from spudmart.venues.models import SPORTS
from spudmart.CERN.models import STATES


class CreateTeamForm(forms.Form):
    team_name = forms.CharField(max_length=255, help_text='The name of your team must be unique.')
    sport = forms.ChoiceField(choices=[('%s' % x, SPORTS[x]) for x in range(len(SPORTS))])
    contact_details = forms.CharField(
        max_length=255,
        help_text='How should people contact you and your team? Leave instructions, number and emails '
                  'addresses here!',
        required=False)
    free_text = forms.CharField(
        max_length=255, help_text='Say something about your team!',
        required=False)
    file = forms.FileField(required=False, label="Image")
    state = forms.ChoiceField(choices=[('%s' % x, x) for x in STATES])

    def clean(self):
        cleaned_data = super(CreateTeamForm, self).clean()
        name = cleaned_data.get('team_name').strip()
        if TeamPage.objects.filter(name=name).count():
            raise forms.ValidationError("The team name you are using is already taken, try adding the town or city?")
        return cleaned_data


class TeamPageForm(ModelForm):
    class Meta:
        model = TeamPage
        exclude = ('image', 'location')