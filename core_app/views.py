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
    sample = get_object_or_404(Sample, id=sample_id)
    classification = get_object_or_404(Classification, sample=sample)
    calibration = get_object_or_404(Calibration, sample=sample)
    report = Report(identifier=sample.sample_identifier, filename=sample.filename, filesize=sample.filesize,
                    instrument_type=calibration.instrument_type, email=sample.email, created=sample.created)
    report.ROX_valid = calibration.ROX_valid
    report.ROX_date = calibration.ROX_date
    report.FAM_valid = calibration.FAM_valid
    report.FAM_date = calibration.FAM_date
    report.VIC_valid = calibration.VIC_valid
    report.VIC_date = calibration.VIC_date
    report.amplification_test = calibration.amplification_test

    if classification.distLab1 == classification.distLab2:
        report.score = (classification.score1 + classification.score2) / 2
        report.subgroup = classification.distLab1

    html = render_to_string('core_app/report/pdf.html',
                            {'classification': classification,
                             'calibration': calibration,
                             'report': report
                             })

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
        self.ROX_valid = None
        self.ROX_date = None
        self.VIC_valid = None
        self.VIC_date = None
        self.FAM_valid = None
        self.FAM_date = None
        self.amplification_test = None






