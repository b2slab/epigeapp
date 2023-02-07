from django import forms
from django.forms import ModelForm
from upload_validator import FileTypeValidator
from .models import Sample
from django.core.exceptions import ValidationError

from django.utils.safestring import mark_safe




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

    diagnosis = forms.BooleanField(label="Diagnosis of MB assessed by a pathologist.",
                                    help_text='EpiGe-App is not designed as a diagnostic tool.')
    
    
    confirmation = forms.BooleanField(label=mark_safe("<strong>Confirmation:</strong> I accept the <a href='https://www.irsjd.org/en/legal-notice-and-terms-of-use/' target='_blank' rel='noopener noreferrer'>terms of use</a>, "
                                                        "the <a href='https://www.irsjd.org/en/privacy-policy/' target='_blank' rel='noopener noreferrer'>privacy policy</a> "
                                                        "and I confirm that: “<i>The epigenetic classifier EpiWNT-SHH "
                                                        "has been designed for the classification of pediatric medulloblastoma tumors "
                                                        "into the consensus medulloblastoma subgroups WNT, SHH and non-WNT/non-SHH "
                                                        "(<a href='https://pubmed.ncbi.nlm.nih.gov/27040285/' target='_blank' rel='noopener noreferrer'>Ramaswamy et al. Acta Neuropathol 2016</a>; "
                                                        "<a href='https://pubmed.ncbi.nlm.nih.gov/34185076/' target='_blank' rel='noopener noreferrer'>Louis DN et al. Neuro Oncol 2021</a>). "
                                                        "It has not been developed and validated for diagnosis purposes</i>”."), required=True)

    def clean(self):
        cleaned_data = super().clean()
        send_mail = cleaned_data.get("send_mail")
        if send_mail:
            email = cleaned_data.get("email")
            if not email:
                msg = "Must put a valid e-mail when you want to recieve an e-mail with the results."
                self.add_error('email', msg)