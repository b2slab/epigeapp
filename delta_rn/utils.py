import pandas as pd
from .models import Classification, Sample, Calibration
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from io import BytesIO
import weasyprint
from django.conf import settings


def get_classification(path_folder, sample):
    rf_data = pd.read_csv(path_folder / 'dataframe_rf.csv')

    Classification.objects.create(sample=sample,
                                  subgroup=rf_data.iloc[0]['subgroup'],
                                  probability_wnt=round(rf_data.iloc[0]['probability WNT'], 4),
                                  probability_shh=round(rf_data.iloc[0]['probability SHH'], 4),
                                  probability_gg=round(rf_data.iloc[0]['probability non-WNT/non-SHH'], 4),
                                  )


def send_report(sample_id):
    sample = Sample.objects.get(id=sample_id)

    # create e-mail
    subject = 'EpiGeApp Analysis complete'
    message = f"""
    Hello, the following analysis is complete:

    Job code: {sample.id}
    Sample identifier: {sample.sample_identifier}
    Created at: {sample.created}

    Please, find attached the results for your recent analysis.

    EpiGe Team
    """

    email = EmailMessage(subject, message, 'iosullanoviles@gmail.com',
                         [sample.email])

    if not sample.txt_complete:
        html = render_to_string('delta_rn/report_error1.html',
                                {'sample': sample})
    elif not sample.all_cpg:
        calibration = Calibration.objects.get(sample=sample_id)
        html = render_to_string('delta_rn/report_error2.html',
                                {'calibration': calibration,
                                 'sample': sample})
    else:
        calibration = Calibration.objects.get(sample=sample_id)
        classification = Classification.objects.get(sample=sample_id)

        html = render_to_string('delta_rn/report_complete.html',
                                {'classification': classification,
                                 'calibration': calibration,
                                 'sample': sample})
    # generate PDF file
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATICFILES_DIRS[0] / 'css/pdf.css')]
    weasyprint.HTML(string=html, base_url="http://127.0.0.1:8000/").write_pdf(out, stylesheets=stylesheets)
    # attach PDF file
    email.attach(f'analysis_{sample.id}.pdf', out.getvalue(), 'application/pdf')
    # send e-mail
    email.send()
    print("Report Sent!")

