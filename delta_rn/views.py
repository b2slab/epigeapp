from django.shortcuts import render, redirect
from .forms import SampleModelForm
from core_app.tasks import analysis_notification
from .tasks import analysis_and_report


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
