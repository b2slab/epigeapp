from django.shortcuts import render, redirect
from .forms import InstructionsForm, SampleModelForm
from .tasks import pipeline
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
from .models import Sample, QualityControl, Calibration
import pandas as pd
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
    quality_control = get_object_or_404(QualityControl, sample=sample)
    calibration = get_object_or_404(Calibration, sample=sample)

    png_list = glob.glob(static_dir + "samples/" + str(sample_id) + '/*.png', recursive=True)
    png_list = [x.split("epigen_app")[1] for x in png_list]
    print(png_list)

    df = pd.read_csv(base_root + sample.file.url.split("data")[0] + "results/CMS.csv", index_col=False)

    html = render_to_string('core_app/report/pdf.html',
                            {'sample': sample,
                             'quality_control': quality_control,
                             'calibration': calibration,
                             'path_to_image': "/static/samples/af4359de-0002-4e1c-b7b8-e0f9f8cc63a5/CMS_panel.png",
                             'df': df,
                             'lista1': png_list})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=sample_{sample.id}.pdf'
    weasyprint.HTML(string=html,
                    base_url=request.build_absolute_uri()).write_pdf(response,
                                                                     stylesheets=[weasyprint.CSS(static_dir + 'css/pdf.css')])
    return response


