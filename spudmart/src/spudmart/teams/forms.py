from django import forms
from django.forms import HiddenInput
from django.forms.models import ModelForm
from spudderdomain.controllers import SocialController
from spudderdomain.models import TeamPage
from spudmart.venues.models import SPORTS
from spudmart.CERN.models import SORTED_STATES


class CreateTeamForm(forms.Form):
    next_url = forms.CharField(max_length=255, widget=HiddenInput)
    team_name = forms.CharField(max_length=255, help_text='The name of your team must be unique.',
                                label="Team name <span class=\"input-required\">*required</span>")
    at_name = forms.CharField(
        max_length=255,
        label="Teams @name <span class=\"input-required\">*required</span>",
        help_text="Used to identify this team and link spuds to it! <b>lowercase letters and numbers only please</b><div class='alert alert-danger' style='display:none;' id='at_name_alert'></div>")
    sport = forms.ChoiceField(
        choices=[('', 'Select a sport...')] + [('%s' % x, SPORTS[x]) for x in range(len(SPORTS))],
        label="Sport <span class=\"input-required\">*required</span>")
    contact_details = forms.EmailField(
        max_length=255,
        help_text='How should people contact you and your team? Leave instructions, number and emails '
                  'addresses here!',
        required=False)
    free_text = forms.CharField(
        max_length=255, help_text='Say something about your team!',
        required=False, label="About us")
    # file = forms.FileField(required=False, label="Image")
    state = forms.ChoiceField(
        choices=[('', 'Select a state...')] + sorted([(k, v) for k, v in SORTED_STATES.items()], key=lambda x:x[1]),
        label="State <span class=\"input-required\">*required</span>")

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


class TeamPageForm(ModelForm):
    class Meta:
        model = TeamPage
        exclude = ('image', 'location')