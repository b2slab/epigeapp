from django import forms
from django.forms import ModelForm
from upload_validator import FileTypeValidator
from .models import Sample
from django.core.exceptions import ValidationError



class SampleModelForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['email', 'file', 'sample_identifier', 'diagnosis', 'send_mail']

    file = forms.FileField(label='Upload File:',
                           help_text="Only txt formats are accepted.",
                           validators=[FileTypeValidator(allowed_types=['text/plain'],
                                                         allowed_extensions=['.txt'])])

    send_mail = forms.BooleanField(required=False,
                                    label="Do you want to receive the results via email?",
                                    help_text="If you accept, you will receive an email with the results to the email address below. Otherwise you will be able to consult the results on our web server for the next 30 days.")

    email = forms.EmailField(required=False,
                             label="Your e-mail:",
                             help_text="Optional.")

    sample_identifier = forms.CharField(label="Sample identifier:",
                                        help_text='Avoid using personal patient information in the sample identifier '
                                                  'such as name, gender or nationality.')

    diagnosis = forms.CharField(label="Diagnosis:",
                                help_text='EpiGe-App is not designed as a diagnostic tool.')

    def clean(self):
        cleaned_data = super().clean()
        send_mail = cleaned_data.get("send_mail")
        if send_mail:
            email = cleaned_data.get("email")
            if not email:
                msg = "Must put a valid e-mail when you want to recieve an e-mail with the results."
                self.add_error('email', msg)

    

