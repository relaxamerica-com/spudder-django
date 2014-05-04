from django import forms
from spudmart.files.models import UploadedFile


class UploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        exclude = ('content_type', 'filename')