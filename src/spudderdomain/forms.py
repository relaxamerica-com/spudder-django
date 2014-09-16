from django import forms
from django.forms.widgets import HiddenInput
from spudderdomain.models import FanPage, ChallengeTemplate


class FanPageForm(forms.ModelForm):
    class Meta:
        model = FanPage
        exclude = ('fan', 'avatar', 'username')


class ChooseChallengeTemplateForm(forms.Form):
    template_id = forms.CharField(max_length=255, required=False)


class NewChallengeTemplateForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            if ChallengeTemplate.objects.filter(name=name).count() > 0:
                raise forms.ValidationError('This Challenge Template name already exists')
        return name


class ChallengeClubForm(forms.Form):
    recipient_club_id = forms.CharField(max_length=255, required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        recipient_club_id = cleaned_data.get('recipient_club_id')
        if not recipient_club_id:
            raise forms.ValidationError('Please select a club')
        return cleaned_data

class ChallengeDonationForm(forms.Form):
    proposed_donation_amount = forms.FloatField()


class ChallengeDetailsForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea)

