from spudmart.upload.models import UploadedFile
from django import forms

class UploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        exclude = ('user', 'content_type', 'name')