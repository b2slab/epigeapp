from django.shortcuts import render, redirect
from .forms import InstructionsForm, SampleModelForm
from .tasks import analysis_and_report, analysis_notification
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
from .models import Sample, Classification, Calibration


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
            # analysis_notification.delay(sample_id=sample.id)
            analysis_and_report.delay(sample_id=sample.id)
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
