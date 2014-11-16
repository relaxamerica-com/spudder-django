from django import forms
from spudderadmin.forms import PasswordAndActionForm


class LeagueAthleticsFormAction():
    def __init__(self):
        pass

    RESET_CLUBS = 'reset_clubs'
    IMPORT_CLUBS = 'import_clubs'


class LeagueAthleticsPasswordAndActionForm(PasswordAndActionForm):
    default_password = 'spudmart3'


class LeagueAthleticsImportClubsForm(LeagueAthleticsPasswordAndActionForm):
    pass


class LeagueAthleticsResetClubsForm(LeagueAthleticsPasswordAndActionForm):
    pass


class LeagueAthleticsImportedClubsSearchForm(forms.Form):
    name = forms.CharField(required=True, help_text='Original full name from LeagueAthletics.com', label="Full name")