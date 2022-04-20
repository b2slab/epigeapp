import mimetypes
import os

import weasyprint
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from .forms import InstructionsForm, SampleModelForm, ContactForm
from .models import Sample, Classification, Calibration
from .tasks import analysis_and_report, analysis_notification
from django.core.mail import EmailMessage


def home_view(request):
    return render(request, 'core_app/home.html')


def protocols_view(request):
    return render(request, 'core_app/protocols.html')


def download_pdf(request, filename):
    if filename != '':
        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Define the full file path
        filepath = BASE_DIR + '/static/protocols/' + filename
        # Open the file for reading content
        path = open(filepath, 'rb', buffering=0)
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        # Return the response value
        return response
    else:
        return render(request, 'core_app/protocols.html')


def instructions_view(request):
    if request.method == 'POST':
        form = InstructionsForm(request.POST)
        if form.is_valid():
            return redirect('workflow:upload_data')
    else:
        form = InstructionsForm()
    return render(request, 'core_app/instructions.html', {'form': form})


def analysis_view(request):
    if request.method == 'POST':
        form = SampleModelForm(request.POST, request.FILES)
        if form.is_valid():
            sample = form.save()
            base_url = request.build_absolute_uri()
            analysis_notification.delay(sample_id=sample.id)
            analysis_and_report.delay(sample_id=sample.id, base_url=base_url)
            return redirect('core_app:success')
    else:
        form = SampleModelForm()
    return render(request, 'core_app/upload_file.html', {'form': form})


def terms_view(request):
    return render(request, 'core_app/terms.html')


def privacy_view(request):
    return render(request, 'core_app/privacy.html')


def legal_view(request):
    return render(request, 'core_app/legal.html')


def funding_view(request):
    return render(request, 'core_app/funding.html')


def success_view(request):
    return render(request, 'core_app/success.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            email_subject = f'New contact {form.cleaned_data["email"]}: {form.cleaned_data["subject"]}'
            email_message = form.cleaned_data['message']
            email = EmailMessage(email_subject, email_message, 'hospitalbarcelona.PECA@sjd.es',
                                 ['joshua.llano@upc.edu'])
            email.send()
            return render(request, 'core_app/success_contact.html')
    form = ContactForm()
    context = {'form': form}
    return render(request, 'core_app/contact.html', context)


def information_view(request):
    return render(request, 'core_app/information.html')


@staff_member_required
def admin_report_pdf(request, sample_id):
    sample = get_object_or_404(Sample, id=sample_id)
    score = None
    group = None

    if not sample.txt_complete:
        html = render_to_string('core_app/report/report_error1.html',
                                {'sample': sample})
    elif not sample.all_cpg:
        calibration = get_object_or_404(Calibration, sample=sample)
        html = render_to_string('core_app/report/report_error2.html',
                                {'calibration': calibration,
                                 'sample': sample})
    elif not sample.amplification_fit:
        calibration = get_object_or_404(Calibration, sample=sample)
        html = render_to_string('core_app/report/report_error3.html',
                                {'calibration': calibration,
                                 'sample': sample})
    else:
        calibration = get_object_or_404(Calibration, sample=sample)
        classification = get_object_or_404(Classification, sample=sample)
        if classification.distLab1 == classification.distLab2:
            score = (classification.score1 + classification.score2) / 2
            group = classification.distLab1

        html = render_to_string('core_app/report/report_complete.html',
                                {'classification': classification,
                                 'calibration': calibration,
                                 'sample': sample,
                                 'score': score,
                                 'group': group})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=sample_{sample.id}.pdf'
    if settings.DEBUG:
        stylesheets = [weasyprint.CSS(settings.STATICFILES_DIRS[0] / 'css/pdf.css')]
    else:
        stylesheets = [weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')]
    weasyprint.HTML(string=html,
                    base_url=request.build_absolute_uri()).write_pdf(response, stylesheets=stylesheets)
    return response
