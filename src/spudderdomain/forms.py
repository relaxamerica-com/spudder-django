from django.forms import ModelForm
from spudderdomain.models import FanPage, TeamPage


class FanPageForm(ModelForm):
    class Meta:
        model = FanPage
        exclude = ('fan', 'avatar', 'username')