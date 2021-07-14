from django.shortcuts import render, redirect
from .forms import SampleModelForm
from core_app.tasks import analysis_notification
from .tasks import analysis_and_report
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from .models import Sample, Classification, Calibration
from django.template.loader import render_to_string
import weasyprint
from django.http import HttpResponse
from django.conf import settings

static_dir = str(settings.BASE_DIR) + '/static/'
base_root = str(settings.BASE_DIR)


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


@staff_member_required
def admin_report_pdf(request, sample_id):
    sample = get_object_or_404(Sample, id=sample_id)

    calibration = get_object_or_404(Calibration, sample=sample)
    classification = get_object_or_404(Classification, sample=sample)

    html = render_to_string('delta_rn/report.html',
                            {'classification': classification,
                             'calibration': calibration,
                             'sample': sample})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=sample_{sample.id}.pdf'
    stylesheets = [weasyprint.CSS(static_dir + 'css/pdf.css')]
    weasyprint.HTML(string=html,
                    base_url=request.build_absolute_uri()).write_pdf(response, stylesheets=stylesheets)
    return response

