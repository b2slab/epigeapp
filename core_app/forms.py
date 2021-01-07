from django import forms
from upload_validator import FileTypeValidator


class UploadFileForm(forms.Form):
    file = forms.FileField(label='File',
                           help_text="Only txt formats are accepted.",
                           validators=[FileTypeValidator(allowed_types=['text/plain'],
                                                         allowed_extensions=['.txt'])])
