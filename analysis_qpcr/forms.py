from django import forms
from .models import Sample
from upload_validator import FileTypeValidator


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = '__all__'

    file = forms.FileField(label='File',
                           help_text="Only txt formats are accepted.",
                           validators=[FileTypeValidator(allowed_types=['text/plain'],
                                                         allowed_extensions=['.txt'])])
