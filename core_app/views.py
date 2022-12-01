import mimetypes
import os

from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError

from .forms import InstructionsForm, ContactForm
from workflow.models import Sample, Calibration, Classification


def home_view(request):
    return render(request, 'core_app/home.html')


def protocols_view(request):
    return render(request, 'core_app/protocols.html')


def terms_view(request):
    return render(request, 'core_app/terms.html')


def privacy_view(request):
    return render(request, 'core_app/privacy.html')


def legal_view(request):
    return render(request, 'core_app/legal.html')


def funding_view(request):
    return render(request, 'core_app/funding.html')


def success_view(request):
    job_id = request.GET.get('job_id')
    sample = get_object_or_404(Sample, id=job_id)
    return render(request, 'core_app/success.html', context={'job_id': sample.id})


def information_view(request):
    return render(request, 'core_app/information.html')


def about_view(request):
    return render(request, 'core_app/about_us.html')


def instructions_view(request):
    if request.method == 'POST':
        form = InstructionsForm(request.POST)
        if form.is_valid():
            return redirect('workflow:upload_data')
    else:
        form = InstructionsForm()
    return render(request, 'core_app/instructions.html', {'form': form})


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


def search_view(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        if searched:
            return redirect('core_app:sample-detail', sample_id=searched)
        else:
            return render(request, 'core_app/search_job_id.html')
    else:
        return redirect('core_app:home')


def sample_view(request, sample_id):
    try:
        sample = get_object_or_404(Sample, id=sample_id)
        classification = get_object_or_404(Classification, sample=sample)
        calibration = get_object_or_404(Calibration, sample=sample)
        print("El estado de la muestra", sample.id, "es", sample.get_status_display())
        return render(request, 'core_app/sample_detail.html', {'sample': sample, 
                                                            'classification': classification, 
                                                            'calibration': calibration})
    except ValidationError:
        raise Http404("Job ID is not valid")


