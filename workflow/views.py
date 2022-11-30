from django.shortcuts import render, redirect
from .forms import SampleModelForm
from .tasks import analysis_and_report, analysis_notification
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from .models import Sample, Classification, Calibration
from django.template.loader import render_to_string
import weasyprint
from django.http import HttpResponse
from django.conf import settings


def workflow_view(request):
    if request.method == 'POST':
        form = SampleModelForm(request.POST, request.FILES)
        if form.is_valid():
            sample = form.save()
            base_url = request.build_absolute_uri()
            if sample.send_mail:
                analysis_notification.delay(sample_id=sample.id)
            analysis_and_report.delay(sample_id=sample.id, base_url=base_url)
            return redirect('core_app:success')
    else:
        form = SampleModelForm()
    return render(request, 'core_app/upload_file.html', {'form': form})


@staff_member_required
def admin_report_pdf(request, sample_id):
    sample = get_object_or_404(Sample, id=sample_id)

    if not sample.txt_complete:
        html = render_to_string('workflow/report_error1.html',
                                {'sample': sample})
    elif not sample.all_cpg:
        calibration = get_object_or_404(Calibration, sample=sample)
        html = render_to_string('workflow/report_error2.html',
                                {'calibration': calibration,
                                 'sample': sample})
    else:
        calibration = get_object_or_404(Calibration, sample=sample)
        classification = get_object_or_404(Classification, sample=sample)

        html = render_to_string('workflow/report_complete.html',
                                {'classification': classification,
                                 'calibration': calibration,
                                 'sample': sample})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=sample_{sample.id}.pdf'
    stylesheets = [weasyprint.CSS(settings.STATICFILES_DIRS[0] / 'css/pdf.css')]
    weasyprint.HTML(string=html,
                    base_url=request.build_absolute_uri()).write_pdf(response, stylesheets=stylesheets)
    return response


def download_report(request, sample_id):
    sample = get_object_or_404(Sample, id=sample_id)
    calibration = get_object_or_404(Calibration, sample=sample)
    classification = get_object_or_404(Classification, sample=sample)

    html = render_to_string('workflow/report_complete.html',{'classification': classification,
                                                             'calibration': calibration,
                                                             'sample': sample})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=sample_{sample.id}.pdf'
    stylesheets = [weasyprint.CSS(settings.STATICFILES_DIRS[0] / 'css/pdf.css')]
    weasyprint.HTML(string=html,
                    base_url=request.build_absolute_uri()).write_pdf(response, stylesheets=stylesheets)
    return response

