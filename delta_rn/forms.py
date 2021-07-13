from django import forms
from django.forms import ModelForm
from upload_validator import FileTypeValidator
from .models import Sample


class SampleModelForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['email', 'file', 'sample_identifier', 'diagnosis']

    check1 = forms.BooleanField(label="The sample has been evaluated and diagnosed as medulloblastoma by "
                                      "a pathologist.", required=True)

    check2 = forms.BooleanField(label="The sample has more than 70% viable tumor cell content.", required=True)

    check3 = forms.BooleanField(label="The sample has been analysed in one of the following qPCR Thermocycle "
                                      "(Applied Biosistems 7500, QS5 or QS6)", required=True)

    check4 = forms.BooleanField(label="The following names (W1_2554, W3_0222, S1_1033, S3_1292, G1_1884, G3_0126) have "
                                      "been assigned to the SNP primers", required=True)

    check5 = forms.BooleanField(label="Confirmation: I accept the terms and conditions of use [link], the data privacy "
                                      "statement [link] and I confirm that: “The epigenetic classifier EpiWNT-SHH "
                                      "has been designed for the classification of pediatric medulloblastoma tumors "
                                      "into the consensus medulloblastoma subgroups WNT, SHH and non-WNT/non-SHH "
                                      "(Ramaswamy et al. Acta Neuropathol 2016; Louis et al. Acta Neuropathol 2016). "
                                      "It has not been developed and validated for diagnosis purposes”.", required=True)

    file = forms.FileField(label='Upload File:',
                           help_text="Only txt formats are accepted.",
                           validators=[FileTypeValidator(allowed_types=['text/plain'],
                                                         allowed_extensions=['.txt'])])

    email = forms.EmailField(label="Your email:",
                             help_text="You will receive an e-mail when the analysis is finished.",)

    sample_identifier = forms.CharField(label="Sample identifier:")

    diagnosis = forms.CharField(label="Diagnosis:")

