from django import forms
from django.forms import ModelForm
from .models import Contact


class InstructionsForm(forms.Form):
    check1 = forms.BooleanField(label="The sample has been evaluated and diagnosed as medulloblastoma by "
                                      "a pathologist.", required=True)

    check2 = forms.BooleanField(label="The sample has more than 70% viable tumor cell content.", required=True)

    check3 = forms.BooleanField(label="Analyse only one sample in each qPCR experiment.", required=True)

    check4 = forms.BooleanField(label="The sample has been analysed in one of the following qPCR Thermocycle "
                                      "(Applied Biosystems 7500, QS, QS1, QS3, QS5 or QS6)", required=True)

    check5 = forms.BooleanField(label="The following names (W1_2554, W3_0222, S1_1033, S3_1292, G1_1884, G3_0126) have "
                                      "been assigned to the SNP primers.", required=True)

    check6 = forms.BooleanField(label="Upload a txt file that contains the results.", required=True)

    check7 = forms.BooleanField(label="Confirmation: I accept the terms and conditions of use [link], the data privacy "
                                      "statement [link] and I confirm that: “The epigenetic classifier EpiWNT-SHH "
                                      "has been designed for the classification of pediatric medulloblastoma tumors "
                                      "into the consensus medulloblastoma subgroups WNT, SHH and non-WNT/non-SHH "
                                      "(Ramaswamy et al. Acta Neuropathol 2016; Louis et al. Acta Neuropathol 2016). "
                                      "It has not been developed and validated for diagnosis purposes”.", required=True)

    check8 = forms.BooleanField(label="Avoid using personal patient information in the sample identifier such as name, "
                                      "gender or nationality.", required=True)


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'

    check_box = forms.BooleanField(label='I have read and accept that my data will be the responsibility of the '
                                         'Fundació Sant Joan de Déu · Institut de Recerca Sant Joan de Déu on '
                                         'the legal basis of consent. The data will not be transferred to third '
                                         'parties. For more information or how to exercise your rights, '
                                         'you can consult the terms of use and the privacy policy', required=True)


