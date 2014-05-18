from django.forms import ModelForm
from spudmart.sponsors.models import SponsorPage


class SponsorPageForm(ModelForm):
    class Meta:
        model = SponsorPage
        exclude = ('sponsor', 'map_info', 'thumbnail', 'images')