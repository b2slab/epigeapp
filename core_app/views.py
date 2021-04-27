from django.shortcuts import render, redirect
from .forms import InstructionsForm, SampleModelForm
from .tasks import pipeline
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
from .models import Sample, Classification, Calibration
import glob


static_dir = str(settings.BASE_DIR) + '/static/'
base_root = str(settings.BASE_DIR)


def home_view(request):
    return render(request, 'core_app/home.html')


def instructions_view(request):
    if request.method == 'POST':
        form = InstructionsForm(request.POST)
        if form.is_valid():
            return redirect('core_app:analysis')
    else:
        form = InstructionsForm()
    return render(request, 'core_app/instructions.html', {'form': form})


def analysis_view(request):
    if request.method == 'POST':
        form = SampleModelForm(request.POST, request.FILES)
        if form.is_valid():
            sample = form.save()
            pipeline.delay(sample_id=sample.id)
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


def success_view(request):
    return render(request, 'core_app/success.html')


@staff_member_required
def admin_report_pdf(request, sample_id):
    score = None
    subgroup = None
    sample = get_object_or_404(Sample, id=sample_id)
    classification = get_object_or_404(Classification, sample=sample)
    calibration = get_object_or_404(Calibration, sample=sample)
    if classification.subgroup1 == classification.subgroup2:
        score = (classification.score1 + classification.score2) / 2
        subgroup = classification.subgroup1

    html = render_to_string('core_app/report/pdf.html',
                            {'sample': sample,
                             'classification': classification,
                             'calibration': calibration,
                             'score': score,
                             'subgroup': subgroup})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=sample_{sample.id}.pdf'
    weasyprint.HTML(string=html,
                    base_url=request.build_absolute_uri()).write_pdf(response,
                                                                     stylesheets=[weasyprint.CSS(static_dir + 'css/pdf.css')])
    return response


class Report:
    def __init__(self, identifier, filename, filesize, instrument_type, email, created):
        self.identifier = identifier
        self.filename = filename
        self.filesize = filesize
        self.instrument_type = instrument_type
        self.email = email
        self.created = created
        self.subgroup = None
        self.score = None






