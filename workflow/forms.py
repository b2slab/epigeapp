from django import forms
from django.forms import ModelForm
from upload_validator import FileTypeValidator
from .models import Sample


class SampleModelForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['email', 'file', 'sample_identifier', 'diagnosis']

    file = forms.FileField(label='Upload File:',
                           help_text="Only txt formats are accepted.",
                           validators=[FileTypeValidator(allowed_types=['text/plain'],
                                                         allowed_extensions=['.txt'])])

    email = forms.EmailField(label="Your email:",
                             help_text="You will receive an e-mail when the analysis is finished.",)

    sample_identifier = forms.CharField(label="Sample identifier:")

    diagnosis = forms.CharField(label="Diagnosis:")

