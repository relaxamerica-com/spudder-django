from django import forms
from django.forms.widgets import HiddenInput
from spudderdomain.models import FanPage, ChallengeTemplate


class FanPageForm(forms.ModelForm):
    class Meta:
        model = FanPage
        exclude = ('fan', 'avatar', 'username')


class ChooseChallengeTemplateForm(forms.Form):
    template_id = forms.CharField(max_length=255, required=False, widget=HiddenInput)


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


class EditChallengeTemplateForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea)
    file = forms.FileField(
        required=False, label="Add logo to this challenge template",
        help_text="Great logos are square and at least 200px x 200px")

    def __init__(self, *args, **kwargs):
        template_id = kwargs.pop('template_id', None)
        self.template_id = template_id
        self.image = kwargs.pop('image', None)

        super(EditChallengeTemplateForm, self).__init__(*args, **kwargs)

        if self.image:
            self.update_file_field_label_and_help_text()

    def clean_name(self):
        cleaned_data = super(EditChallengeTemplateForm, self).clean()
        name = cleaned_data.get('name').strip()
        if ChallengeTemplate.objects.exclude(id=self.template_id).filter(name=name).count():
            raise forms.ValidationError("The template name you are using is already taken, try adding the town or city?")
        return name

    def update_file_field_label_and_help_text(self):
        self.fields['file'].label = "Replace this challenge template logo"
        self.fields['file'].help_text = """
<span class=\"help-text-content\">Great logos are square and at least 200px x 200px</span>
<img class=\"edit-team-logo-img pull-left\" src=\"/file/serve/%s\"/>
""" % self.image.id


class DeclineChallengeForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, required=False)


class DonateChallengeForm(forms.Form):
    donation_amount = forms.FloatField()


class AcceptChallengeForm(forms.Form):
    donation_amount = forms.FloatField()
    # file = forms.FileField(label="Upload video with you performing a challenge")

