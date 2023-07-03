from django import forms
from django.forms import ModelForm
from upload_validator import FileTypeValidator
from .models import Sample
from django.core.exceptions import ValidationError

from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML




class SampleModelForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['email', 'file', 'sample_identifier', 'send_mail']
        
    email = forms.EmailField(required=False,
                             label="Your e-mail:",
                             help_text="Optional.")

    file = forms.FileField(label='Upload File:',
                           help_text="Only txt formats are accepted.",
                           validators=[FileTypeValidator(allowed_types=['text/plain'],
                                                         allowed_extensions=['.txt'])])
    
    sample_identifier = forms.CharField(label="Sample identifier:",
                                        help_text=mark_safe('<b>Avoid</b> using personal patient information in the sample identifier '
                                                  'such as name, date of birth, gender or nationality.'))

    send_mail = forms.BooleanField(required=False,
                                    label="Do you want to receive the results via e-mail?",
                                    help_text="If you accept, you will receive an e-mail with the results to the e-mail address below. Otherwise you will be able to consult the results on our web server for the next 30 days.")


    diagnosis = forms.BooleanField(label="The sample has been reviewed and diagnosed as medulloblastoma by a pathologist.",
                                    help_text='EpiGe-App is not designed as a diagnostic tool.')
    
    
    confirmation = forms.BooleanField(label=mark_safe("<strong>Confirmation:</strong> I accept the <a href='https://www.irsjd.org/en/legal-notice-and-terms-of-use/' target='_blank' rel='noopener noreferrer'>terms of use</a>, "
                                                        "the <a href='https://www.irsjd.org/en/privacy-policy/' target='_blank' rel='noopener noreferrer'>privacy policy</a> "
                                                        "and I confirm that: “<i>The epigenetic classifier EpiWNT-SHH "
                                                        "has been designed for the classification of pediatric medulloblastoma tumors "
                                                        "into the consensus medulloblastoma subgroups WNT, SHH and non-WNT/non-SHH "
                                                        "(<a href='https://pubmed.ncbi.nlm.nih.gov/27040285/' target='_blank' rel='noopener noreferrer'>Ramaswamy et al. Acta Neuropathol 2016</a>; "
                                                        "<a href='https://pubmed.ncbi.nlm.nih.gov/34185076/' target='_blank' rel='noopener noreferrer'>Louis DN et al. Neuro Oncol 2021</a>). "
                                                        "It has not been developed and validated for diagnosis purposes</i>”."))
    
    cell_content = forms.BooleanField(label="The sample has more than 70% viable tumor cell content.")

    only_one = forms.BooleanField(label="Analyse only one sample in each qPCR experiment.")

    instruments = forms.BooleanField(label="The sample has been analysed in one of the following real-time qPCR Instruments: "
                                      "Applied Biosystems 7500, QS1, QS3, QS5 or QS6.")

    cpg_names = forms.BooleanField(label="The following names have been assigned to the SNP primers: "
                                "cg18849583, cg01268345, cg10333416, cg12925355, cg25542041 and cg02227036.")
        

    def clean(self):
        cleaned_data = super().clean()
        send_mail = cleaned_data.get("send_mail")
        if send_mail:
            email = cleaned_data.get("email")
            if not email:
                msg = "You must enter a valid e-mail address when you want to receive an e-mail with the results."
                self.add_error('email', msg)

       
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
                
    
    
    